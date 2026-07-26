"""Private rooms: create / join / cancel / spectate / viewers."""

import json
import random
import string


def make_room_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))


class RoomManager:
    def __init__(self, server):
        self.server = server

    def _leave_queue(self, websocket):
        if websocket in self.server.waiting:
            self.server.waiting.remove(websocket)

    async def create_room(self, websocket):
        s = self.server
        self._leave_queue(websocket)

        code = make_room_code()
        while code in s.rooms:
            code = make_room_code()

        s.rooms[code] = {
            "host": websocket, "guest": None, "active": False, "viewers": [],
        }
        s.clients[websocket]["room"] = code
        s.current_room_code = code
        name = s.clients[websocket]["username"]
        print(f"{name} created room {code}")
        s.broadcaster.log(f"{name} created room {code}")
        await websocket.send(json.dumps({
            "type": "room_created",
            "code": code,
            "message": f"room {code} — waiting for guest...",
        }))

    async def cancel_room(self, websocket):
        s = self.server
        code = s.clients[websocket].get("room")
        room = s.rooms.get(code) if code else None
        if room and room["host"] is websocket and room["guest"] is None:
            del s.rooms[code]
            s.clients[websocket]["room"] = None
            if s.current_room_code == code:
                s.current_room_code = None
            print(f"room {code} cancelled")
            await websocket.send(json.dumps({
                "type": "room_cancelled",
                "message": "room cancelled",
            }))

    async def join_room(self, websocket, msg):
        s = self.server
        self._leave_queue(websocket)

        code = str(msg.get("code", "")).strip().upper()
        room = s.rooms.get(code)
        if room is None:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"room {code} not found",
            }))
            return
        if room["host"] is websocket:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "you cannot join your own room",
            }))
            return
        if room["host"] not in s.clients:
            del s.rooms[code]
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"room {code} host left",
            }))
            return

        # 3rd+ player joining same room → viewer
        if room["guest"] is not None or room.get("active"):
            s.clients[websocket]["color"] = "viewer"
            s.clients[websocket]["room"] = code
            room.setdefault("viewers", []).append(websocket)
            white = s.match_players.get("w", "?")
            black = s.match_players.get("b", "?")
            name = s.clients[websocket]["username"]
            print(f"{name} joined room {code} as viewer")
            s.broadcaster.log(f"{name} joined room {code} as viewer")
            await websocket.send(json.dumps({
                "type": "match_found",
                "color": "viewer",
                "opponent": f"{white} vs {black}",
                "code": code,
                "white": white,
                "black": black,
            }))
            return

        host = room["host"]
        room["guest"] = websocket
        room["active"] = True
        s.clients[websocket]["room"] = code
        s.current_room_code = code

        await s.session.start_match(host, websocket)
        print(f"ROOM {code}: "
              f"{s.clients[host]['username']}(w) vs "
              f"{s.clients[websocket]['username']}(b)")
        s.broadcaster.log(
            f"room {code} started: "
            f"{s.clients[host]['username']}(w) vs "
            f"{s.clients[websocket]['username']}(b)"
        )

    async def spectate(self, websocket):
        s = self.server
        self._leave_queue(websocket)

        if not s.match_players or s.controller.engine.game_over:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "no active game to watch",
            }))
            return

        white_name = s.match_players.get("w")
        black_name = s.match_players.get("b")
        s.clients[websocket]["color"] = "viewer"
        name = s.clients[websocket]["username"]
        print(f"{name} is spectating {white_name} vs {black_name}")
        s.broadcaster.log(f"{name} is spectating {white_name} vs {black_name}")
        await websocket.send(json.dumps({
            "type": "match_found",
            "color": "viewer",
            "opponent": f"{white_name} vs {black_name}",
            "white": white_name,
            "black": black_name,
        }))

    def cleanup_on_disconnect(self, websocket, info):
        """Remove empty waiting room if host left before a guest joined."""
        s = self.server
        code = info.get("room") if info else None
        if code and code in s.rooms:
            room = s.rooms[code]
            if room["host"] is websocket and room["guest"] is None:
                del s.rooms[code]
                print(f"room {code} removed (host left)")
