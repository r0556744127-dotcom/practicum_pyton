"""Match lifecycle: start match, scores from bus, ELO, disconnect resign."""

import json
import time

from constants import CAPTURE_POINTS, DISCONNECT_RESIGN_SEC


class MatchSession:
    """One live match on this single-process server."""

    def __init__(self, server):
        self.server = server
        s = server
        s.bus.subscribe("game_over", self._on_game_over)
        s.bus.subscribe("move_made", self._on_bus_move)
        s.bus.subscribe("piece_captured", self._on_bus_capture)

    def _push_bus_event(self, name, data):
        s = self.server
        s.bus_events.append({"event": name, "data": data or {}})
        if len(s.bus_events) > 20:
            s.bus_events = s.bus_events[-20:]

    def _on_bus_move(self, data):
        self._push_bus_event("move_made", data)
        if data:
            line = f"{data.get('color')}: {data.get('from')}->{data.get('to')}"
            self.server.move_log.append(line)
            if len(self.server.move_log) > 12:
                self.server.move_log = self.server.move_log[-12:]

    def _on_bus_capture(self, data):
        self._push_bus_event("piece_captured", data)
        if data and data.get("by") in ("w", "b") and data.get("piece"):
            kind = data["piece"][1]
            self.server.scores[data["by"]] += CAPTURE_POINTS.get(kind, 0)

    def _on_game_over(self, data):
        if data and data.get("winner") in ("w", "b"):
            self.server.last_winner = data["winner"]
            winner_name = self.server.match_players.get(
                data["winner"], data["winner"])
            self.server.broadcaster.log(f"game over — winner: {winner_name}")
            self._push_bus_event("game_over", data)

    async def start_match(self, white_ws, black_ws):
        """Assign colors and notify both players that a match began."""
        s = self.server
        s.clients[white_ws]["color"] = "w"
        s.clients[black_ws]["color"] = "b"
        s.match_players = {
            "w": s.clients[white_ws]["username"],
            "b": s.clients[black_ws]["username"],
        }
        s.elo_applied = False
        s.last_winner = None
        s.disconnect_deadline = None
        s.disconnect_winner = None
        s.scores = {"w": 0, "b": 0}
        s.move_log = []
        s.bus_events = []
        s.bus.publish("game_started", {})

        await white_ws.send(json.dumps({
            "type": "match_found",
            "color": "w",
            "opponent": s.clients[black_ws]["username"],
            "code": s.current_room_code,
        }))
        await black_ws.send(json.dumps({
            "type": "match_found",
            "color": "b",
            "opponent": s.clients[white_ws]["username"],
            "code": s.current_room_code,
        }))

    def on_player_disconnect(self, info):
        """Start 20s resign timer if a playing side left mid-game."""
        s = self.server
        if (info and info.get("color") in ("w", "b")
                and not s.controller.engine.game_over):
            winner_color = "b" if info["color"] == "w" else "w"
            s.disconnect_winner = winner_color
            s.disconnect_deadline = time.time() + DISCONNECT_RESIGN_SEC
            print(f"{info['username']} ({info['color']}) left; "
                  f"{winner_color} wins in {DISCONNECT_RESIGN_SEC}s if they stay gone")

    def check_disconnect_resign(self):
        s = self.server
        if s.disconnect_deadline is None:
            return
        if time.time() < s.disconnect_deadline:
            return
        if s.controller.engine.game_over:
            s.disconnect_deadline = None
            return

        s.controller.engine.game_over = True
        s.last_winner = s.disconnect_winner
        s.disconnect_deadline = None
        print(f"Auto-resign: winner={s.last_winner}")
        winner_name = s.match_players.get(s.last_winner, s.last_winner)
        s.broadcaster.log(f"auto-resign — winner: {winner_name}")

    def maybe_apply_elo(self):
        s = self.server
        if s.elo_applied or not s.controller.engine.game_over:
            return
        if s.last_winner not in ("w", "b"):
            return

        by_color = dict(s.match_players)
        for info in s.clients.values():
            if info["username"] and info["color"] in ("w", "b"):
                by_color[info["color"]] = info["username"]

        if "w" not in by_color or "b" not in by_color:
            return

        winner_color = s.last_winner
        loser_color = "b" if winner_color == "w" else "w"
        winner = by_color[winner_color]
        loser = by_color[loser_color]

        try:
            new_w, new_l = s.db.apply_game_result(winner, loser)
            s.elo_applied = True
            print(f"ELO updated: {winner}={new_w}, {loser}={new_l}")
            s.broadcaster.log(f"ELO updated: {winner}={new_w}, {loser}={new_l}")
        except ValueError as e:
            print("ELO not updated:", e)
