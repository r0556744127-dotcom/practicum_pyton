"""Build and send game state to all connected clients."""

import json
import time

import websockets
from board_view import BoardRenderer


class StateBroadcaster:
    """Owns activity log + state JSON + broadcast."""

    def __init__(self, server):
        self.server = server

    def log(self, text):
        s = self.server
        s.activity.append(text)
        if len(s.activity) > 20:
            s.activity = s.activity[-20:]
        print(f"[log] {text}")

    def pending_motions_payload(self):
        arb = self.server.controller.engine.arbiter
        out = []
        for m in arb.pending_motions:
            piece = self.server.controller.board.get_cell(m.from_row, m.from_col)
            out.append({
                "from": [m.from_row, m.from_col],
                "to": [m.to_row, m.to_col],
                "arrival_time": m.arrival_time,
                "token": str(piece) if piece else None,
            })
        return out, arb.clock

    def state_message(self):
        s = self.server
        remaining = None
        if s.disconnect_deadline is not None:
            remaining = max(0, int(s.disconnect_deadline - time.time()))

        pending, clock = self.pending_motions_payload()
        return json.dumps({
            "type": "state",
            "board": BoardRenderer.to_rows(s.controller.board),
            "game_over": s.controller.engine.game_over,
            "disconnect_remaining": remaining,
            "activity": list(s.activity),
            "bus_events": list(s.bus_events),
            "room_code": s.current_room_code,
            "scores": dict(s.scores),
            "moves": list(s.move_log),
            "pending": pending,
            "clock": clock,
        })

    async def broadcast_state(self):
        msg = self.state_message()
        for ws in list(self.server.clients):
            try:
                await ws.send(msg)
            except websockets.ConnectionClosed:
                pass
