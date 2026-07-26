"""
Game server entry point — wires modules together (good design / SRP).

Modules:
  constants.py   — shared numbers / starting board
  broadcast.py   — state JSON + activity log + broadcast
  session.py     — match start, scores, ELO, disconnect resign
  matchmaking.py — Play / find opponent by ELO
  rooms.py       — Create / Join / Cancel / viewers / spectate
  users_db.py    — SQLite auth + ELO storage
  elo.py         — ELO math
"""
import sys
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "core"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
import websockets
from board_parser import BoardParser
from game_controller import GameController
from event_bus import EventBus
from users_db import UsersDB

from constants import STARTING_BOARD, TICK_MS
from broadcast import StateBroadcaster
from session import MatchSession
from matchmaking import Matchmaker
from rooms import RoomManager


class GameServer:
    def __init__(self):
        board, _ = BoardParser().parse(STARTING_BOARD)
        self.bus = EventBus()
        self.controller = GameController(board, bus=self.bus)
        self.db = UsersDB()

        # Shared runtime state
        self.clients = {}  # websocket -> {color, username, elo, room}
        self.waiting = []
        self.rooms = {}
        self.elo_applied = False
        self.last_winner = None
        self.disconnect_deadline = None
        self.disconnect_winner = None
        self.match_players = {}
        self.activity = []
        self.bus_events = []
        self.scores = {"w": 0, "b": 0}
        self.move_log = []
        self.current_room_code = None

        # Collaborators (each module owns one concern)
        self.broadcaster = StateBroadcaster(self)
        self.session = MatchSession(self)
        self.matchmaker = Matchmaker(self)
        self.room_manager = RoomManager(self)

    async def handler(self, websocket):
        try:
            raw = await websocket.recv()
            msg = json.loads(raw)
        except Exception:
            await websocket.close()
            return

        # Register (optional) then login
        if msg.get("type") == "register":
            ok, text = self.db.register(
                msg.get("username", ""), msg.get("password", ""))
            await websocket.send(json.dumps({
                "type": "register_result", "ok": ok, "message": text,
            }))
            if not ok:
                await websocket.close()
                return
            msg = {
                "type": "login",
                "username": msg.get("username", ""),
                "password": msg.get("password", ""),
            }

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
        self.broadcaster.log(f"{username} logged in (ELO {elo})")

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

            self.room_manager.cleanup_on_disconnect(websocket, info)
            self.session.on_player_disconnect(info)

            print(f"{info['username'] if info else '?'} disconnected")
            if info:
                self.broadcaster.log(f"{info['username']} disconnected")

    async def handle_message(self, websocket, color, msg):
        kind = msg.get("type")

        if kind == "create_room":
            await self.room_manager.create_room(websocket)
            return
        if kind == "cancel_room":
            await self.room_manager.cancel_room(websocket)
            return
        if kind == "join_room":
            await self.room_manager.join_room(websocket, msg)
            return
        if kind == "spectate":
            await self.room_manager.spectate(websocket)
            return
        if kind == "find_match":
            await self.matchmaker.find_match(websocket)
            return

        if kind != "move" or color not in ("w", "b"):
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

    async def game_loop(self):
        while True:
            self.controller.wait(TICK_MS)
            self.session.check_disconnect_resign()
            self.session.maybe_apply_elo()
            await self.broadcaster.broadcast_state()
            await asyncio.sleep(TICK_MS / 1000)
            await self.matchmaker.check_search_timeouts()


async def main():
    server = GameServer()
    async with websockets.serve(server.handler, "127.0.0.1", 8765):
        print("game server on ws://127.0.0.1:8765", flush=True)
        await server.game_loop()


if __name__ == "__main__":
    asyncio.run(main())
