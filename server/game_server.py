import sys
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "core"))

import asyncio
import json
import websockets
from board_parser import BoardParser
from game_controller import GameController
from event_bus import EventBus
from board_view import BoardRenderer

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

TICK_MS = 50   # כל כמה מילישניות מקדמים את המשחק ומשדרים מצב


class GameServer:
    """מחזיק את האמת: הלוח, המנוע, ה-Bus, ורשימת הלקוחות."""

    def __init__(self):
        board, _ = BoardParser().parse(STARTING_BOARD)
        self.bus = EventBus()
        self.controller = GameController(board, bus=self.bus)
        self.clients = {}   # websocket -> "w" / "b" / "viewer"

    def assign_color(self):
        """ראשון שמתחבר = לבן, שני = שחור, השאר צופים."""
        taken = set(self.clients.values())
        if "w" not in taken:
            return "w"
        if "b" not in taken:
            return "b"
        return "viewer"

    def state_message(self):
        """אורז את מצב המשחק כ-JSON — ה'צילום' שנשלח ברשת."""
        return json.dumps({
            "type": "state",
            "board": BoardRenderer.to_rows(self.controller.board),
            "game_over": self.controller.engine.game_over,
        })

    async def broadcast_state(self):
        """שולח את המצב הנוכחי לכל הלקוחות המחוברים."""
        msg = self.state_message()
        for ws in list(self.clients):
            try:
                await ws.send(msg)
            except websockets.ConnectionClosed:
                pass   # הלקוח התנתק — handler שלו כבר ינקה אותו

    async def handler(self, websocket):
        """רץ עבור כל לקוח: קובע צבע, מקבל פקודות עד שהוא מתנתק."""
        color = self.assign_color()
        self.clients[websocket] = color
        await websocket.send(json.dumps({"type": "welcome", "color": color}))
        print(f"client connected as: {color}")

        try:
            async for message in websocket:
                self.handle_message(color, json.loads(message))
        finally:
            del self.clients[websocket]
            print(f"client disconnected: {color}")

    def handle_message(self, color, msg):
        """מטפל בפקודה מלקוח — רק מהלכים של הצבע שלו."""
        if msg.get("type") != "move" or color == "viewer":
            return

        (fr_r, fr_c), (to_r, to_c) = msg["from"], msg["to"]
        piece = self.controller.board.get_cell(fr_r, fr_c)

        if piece is None or piece.color != color:
            return   # אסור להזיז כלי של היריב

        result = self.controller.engine.request_move(fr_r, fr_c, to_r, to_c)
        print(f"{color} move ({fr_r},{fr_c})->({to_r},{to_c}): {result}")

    async def game_loop(self):
        """לב השרת: מקדם את שעון המשחק ומשדר מצב, בלי סוף."""
        while True:
            self.controller.wait(TICK_MS)
            await self.broadcast_state()
            await asyncio.sleep(TICK_MS / 1000)


async def main():
    server = GameServer()
    async with websockets.serve(server.handler, "localhost", 8765):
        print("game server on ws://localhost:8765")
        await server.game_loop()


if __name__ == "__main__":
    asyncio.run(main())