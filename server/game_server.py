import sys
import os
import time
import random
import string

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "core"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FIND_TIMEOUT_SEC = 60
DISCONNECT_RESIGN_SEC = 20

import asyncio
import json
import websockets
from board_parser import BoardParser
from game_controller import GameController
from event_bus import EventBus
from board_view import BoardRenderer
from users_db import UsersDB


def make_room_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))


STARTING_BOARD = [
    "Board:",
    "bR bN bB bQ bK bB bN bR",
    "bP bP bP bP bP bP bP bP",
    ". . . . . . . .",
    ". . . . . . . .",
    ". . . . . . . .",
    ". . . . . . . .",
    "wP wP wP wP wP wP wP wP",
    "wR wN wB wQ wK wB wN wR",
]

TICK_MS = 50


class GameServer:
    def __init__(self):
        board, _ = BoardParser().parse(STARTING_BOARD)
        self.bus = EventBus()
        self.controller = GameController(board, bus=self.bus)
        self.db = UsersDB()
        self.clients = {}  # websocket -> {"color", "username", "elo", ...}
        self.waiting = []
        self.rooms = {}  # code -> {"host": websocket, "guest": None}
        self.elo_applied = False
        self.last_winner = None
        self.disconnect_deadline = None
        self.disconnect_winner = None
        self.match_players = {}  # {"w": username, "b": username}
        self.activity = []  # recent log lines for clients
        self.bus.subscribe("game_over", self._on_game_over)

    def log(self, text):
        self.activity.append(text)
        if len(self.activity) > 20:
            self.activity = self.activity[-20:]
        print(f"[log] {text}")

    def _on_game_over(self, data):
        if data and data.get("winner") in ("w", "b"):
            self.last_winner = data["winner"]
            winner_name = self.match_players.get(data["winner"], data["winner"])
            self.log(f"game over — winner: {winner_name}")

    def assign_color(self):
        taken = {info["color"] for info in self.clients.values()}
        if "w" not in taken:
            return "w"
        if "b" not in taken:
            return "b"
        return "viewer"

    def state_message(self):
        remaining = None
        if self.disconnect_deadline is not None:
            remaining = max(0, int(self.disconnect_deadline - time.time()))

        return json.dumps({
            "type": "state",
            "board": BoardRenderer.to_rows(self.controller.board),
            "game_over": self.controller.engine.game_over,
            "disconnect_remaining": remaining,
            "activity": list(self.activity),
        })

    async def broadcast_state(self):
        msg = self.state_message()
        for ws in list(self.clients):
            try:
                await ws.send(msg)
            except websockets.ConnectionClosed:
                pass

    def maybe_apply_elo(self):
        if self.elo_applied or not self.controller.engine.game_over:
            return
        if self.last_winner not in ("w", "b"):
            return

        by_color = dict(self.match_players)
        for info in self.clients.values():
            if info["username"] and info["color"] in ("w", "b"):
                by_color[info["color"]] = info["username"]

        if "w" not in by_color or "b" not in by_color:
            return

        winner_color = self.last_winner
        loser_color = "b" if winner_color == "w" else "w"
        winner = by_color[winner_color]
        loser = by_color[loser_color]

        try:
            new_w, new_l = self.db.apply_game_result(winner, loser)
            self.elo_applied = True
            print(f"ELO updated: {winner}={new_w}, {loser}={new_l}")
            self.log(f"ELO updated: {winner}={new_w}, {loser}={new_l}")
        except ValueError as e:
            print("ELO not updated:", e)

    async def handler(self, websocket):
        try:
            raw = await websocket.recv()
            msg = json.loads(raw)
        except Exception:
            await websocket.close()
            return

        if msg.get("type") != "login":
            await websocket.send(json.dumps({
                "type": "error", "message": "login required first"
            }))
            await websocket.close()
            return

        ok, text, elo = self.db.login(
            msg.get("username", ""), msg.get("password", ""))
        if not ok:
            await websocket.send(json.dumps({
                "type": "error", "message": text
            }))
            await websocket.close()
            return

        username = msg["username"].strip()
        await websocket.send(json.dumps({
            "type": "welcome",
            "color": None,
            "username": username,
            "elo": elo,
            "status": "lobby",
        }))
        self.clients[websocket] = {
            "color": None,
            "username": username,
            "elo": elo,
            "room": None,
        }
        print(f"{username} logged in — lobby (ELO {elo})")
        self.log(f"{username} logged in (ELO {elo})")

        try:
            async for message in websocket:
                await self.handle_message(
                    websocket,
                    self.clients[websocket]["color"],
                    json.loads(message),
                )
        finally:
            info = self.clients.pop(websocket, None)
            if websocket in self.waiting:
                self.waiting.remove(websocket)

            code = info.get("room") if info else None
            if code and code in self.rooms:
                room = self.rooms[code]
                if room["host"] is websocket and room["guest"] is None:
                    del self.rooms[code]
                    print(f"room {code} removed (host left)")

            if (info and info.get("color") in ("w", "b")
                    and not self.controller.engine.game_over):
                winner_color = "b" if info["color"] == "w" else "w"
                self.disconnect_winner = winner_color
                self.disconnect_deadline = time.time() + DISCONNECT_RESIGN_SEC
                print(f"{info['username']} ({info['color']}) left; "
                      f"{winner_color} wins in {DISCONNECT_RESIGN_SEC}s if they stay gone")

            print(f"{info['username'] if info else '?'} disconnected")
            if info:
                self.log(f"{info['username']} disconnected")

    async def handle_message(self, websocket, color, msg):
        if msg.get("type") == "create_room":
            if websocket in self.waiting:
                self.waiting.remove(websocket)

            code = make_room_code()
            while code in self.rooms:
                code = make_room_code()

            self.rooms[code] = {"host": websocket, "guest": None}
            self.clients[websocket]["room"] = code
            name = self.clients[websocket]["username"]
            print(f"{name} created room {code}")
            self.log(f"{name} created room {code}")
            await websocket.send(json.dumps({
                "type": "room_created",
                "code": code,
                "message": f"room {code} — waiting for guest...",
            }))
            return

        if msg.get("type") == "cancel_room":
            code = self.clients[websocket].get("room")
            room = self.rooms.get(code) if code else None
            if room and room["host"] is websocket and room["guest"] is None:
                del self.rooms[code]
                self.clients[websocket]["room"] = None
                print(f"room {code} cancelled")
                await websocket.send(json.dumps({
                    "type": "room_cancelled",
                    "message": "room cancelled",
                }))
            return

        if msg.get("type") == "join_room":
            if websocket in self.waiting:
                self.waiting.remove(websocket)

            code = str(msg.get("code", "")).strip().upper()
            room = self.rooms.get(code)
            if room is None:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"room {code} not found",
                }))
                return
            if room["guest"] is not None:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"room {code} is already full",
                }))
                return
            if room["host"] is websocket:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "you cannot join your own room",
                }))
                return
            if room["host"] not in self.clients:
                del self.rooms[code]
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"room {code} host left",
                }))
                return

            host = room["host"]
            room["guest"] = websocket
            self.clients[websocket]["room"] = code
            del self.rooms[code]  # match started — room no longer open

            await self.start_match(host, websocket)
            print(f"ROOM {code}: "
                  f"{self.clients[host]['username']}(w) vs "
                  f"{self.clients[websocket]['username']}(b)")
            self.log(
                f"room {code} started: "
                f"{self.clients[host]['username']}(w) vs "
                f"{self.clients[websocket]['username']}(b)"
            )
            return

        if msg.get("type") == "spectate":
            if websocket in self.waiting:
                self.waiting.remove(websocket)

            # Need an active match with both colors assigned
            if not self.match_players or self.controller.engine.game_over:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "no active game to watch",
                }))
                return

            white_name = self.match_players.get("w")
            black_name = self.match_players.get("b")
            self.clients[websocket]["color"] = "viewer"
            name = self.clients[websocket]["username"]
            print(f"{name} is spectating {white_name} vs {black_name}")
            self.log(f"{name} is spectating {white_name} vs {black_name}")
            await websocket.send(json.dumps({
                "type": "match_found",
                "color": "viewer",
                "opponent": f"{white_name} vs {black_name}",
                "white": white_name,
                "black": black_name,
            }))
            return

        if msg.get("type") == "find_match":
            if websocket not in self.waiting:
                self.waiting.append(websocket)
                self.clients[websocket]["wait_since"] = time.time()

            name = self.clients[websocket]["username"]
            print(f"{name} is searching...")
            await websocket.send(json.dumps({
                "type": "searching",
                "message": "looking for opponent...",
            }))
            await self.try_match(websocket)
            return

        if msg.get("type") != "move" or color not in ("w", "b"):
            return

        (fr_r, fr_c), (to_r, to_c) = msg["from"], msg["to"]
        piece = self.controller.board.get_cell(fr_r, fr_c)
        if piece is None or piece.color != color:
            await websocket.send(json.dumps({
                "type": "move_result", "result": "invalid"
            }))
            return

        result = self.controller.engine.request_move(fr_r, fr_c, to_r, to_c)
        print(f"{color} move ({fr_r},{fr_c})->({to_r},{to_c}): {result}")
        await websocket.send(json.dumps({
            "type": "move_result", "result": result
        }))

    def check_disconnect_resign(self):
        if self.disconnect_deadline is None:
            return
        if time.time() < self.disconnect_deadline:
            return
        if self.controller.engine.game_over:
            self.disconnect_deadline = None
            return

        self.controller.engine.game_over = True
        self.last_winner = self.disconnect_winner
        self.disconnect_deadline = None
        print(f"Auto-resign: winner={self.last_winner}")
        winner_name = self.match_players.get(self.last_winner, self.last_winner)
        self.log(f"auto-resign — winner: {winner_name}")

    async def game_loop(self):
        while True:
            self.controller.wait(TICK_MS)
            self.check_disconnect_resign()
            self.maybe_apply_elo()
            await self.broadcast_state()
            await asyncio.sleep(TICK_MS / 1000)
            await self.check_search_timeouts()

    async def start_match(self, white_ws, black_ws):
        """Assign colors and notify both players that a match began."""
        self.clients[white_ws]["color"] = "w"
        self.clients[black_ws]["color"] = "b"
        self.match_players = {
            "w": self.clients[white_ws]["username"],
            "b": self.clients[black_ws]["username"],
        }
        self.elo_applied = False
        self.last_winner = None
        self.disconnect_deadline = None
        self.disconnect_winner = None

        await white_ws.send(json.dumps({
            "type": "match_found",
            "color": "w",
            "opponent": self.clients[black_ws]["username"],
        }))
        await black_ws.send(json.dumps({
            "type": "match_found",
            "color": "b",
            "opponent": self.clients[white_ws]["username"],
        }))

    async def try_match(self, websocket):
        """If another waiter is within ±100 ELO, start a match."""
        me = self.clients[websocket]
        my_elo = me["elo"]

        for other in list(self.waiting):
            if other is websocket:
                continue
            if other not in self.clients:
                continue
            other_elo = self.clients[other]["elo"]
            if abs(other_elo - my_elo) > 100:
                continue

            self.waiting.remove(websocket)
            self.waiting.remove(other)
            await self.start_match(other, websocket)
            print(f"MATCH: {self.clients[other]['username']}(w) vs {me['username']}(b)")
            self.log(
                f"match started: "
                f"{self.clients[other]['username']}(w) vs {me['username']}(b)"
            )
            return True

        return False

    async def check_search_timeouts(self):
        now = time.time()
        for ws in list(self.waiting):
            info = self.clients.get(ws)
            if not info:
                self.waiting.remove(ws)
                continue
            since = info.get("wait_since", now)
            if now - since >= FIND_TIMEOUT_SEC:
                self.waiting.remove(ws)
                try:
                    await ws.send(json.dumps({
                        "type": "search_failed",
                        "message": "could not find opponent within 1 minute",
                    }))
                except Exception:
                    pass
                print(f"{info['username']} search timed out")


async def main():
    server = GameServer()
    async with websockets.serve(server.handler, "127.0.0.1", 8765):
        print("game server on ws://127.0.0.1:8765", flush=True)
        await server.game_loop()


if __name__ == "__main__":
    asyncio.run(main())
