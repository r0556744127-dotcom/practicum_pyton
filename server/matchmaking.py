"""Auto matchmaking by ELO (±100) with 1-minute search timeout."""

import json
import time

from constants import FIND_TIMEOUT_SEC


class Matchmaker:
    def __init__(self, server):
        self.server = server

    async def find_match(self, websocket):
        s = self.server
        if websocket not in s.waiting:
            s.waiting.append(websocket)
            s.clients[websocket]["wait_since"] = time.time()

        name = s.clients[websocket]["username"]
        print(f"{name} is searching...")
        await websocket.send(json.dumps({
            "type": "searching",
            "message": "looking for opponent...",
        }))
        await self.try_match(websocket)

    async def try_match(self, websocket):
        """If another waiter is within ±100 ELO, start a match."""
        s = self.server
        me = s.clients[websocket]
        my_elo = me["elo"]

        for other in list(s.waiting):
            if other is websocket:
                continue
            if other not in s.clients:
                continue
            other_elo = s.clients[other]["elo"]
            if abs(other_elo - my_elo) > 100:
                continue

            s.waiting.remove(websocket)
            s.waiting.remove(other)
            await s.session.start_match(other, websocket)
            print(f"MATCH: {s.clients[other]['username']}(w) vs {me['username']}(b)")
            s.broadcaster.log(
                f"match started: "
                f"{s.clients[other]['username']}(w) vs {me['username']}(b)"
            )
            return True

        return False

    async def check_search_timeouts(self):
        s = self.server
        now = time.time()
        for ws in list(s.waiting):
            info = s.clients.get(ws)
            if not info:
                s.waiting.remove(ws)
                continue
            since = info.get("wait_since", now)
            if now - since >= FIND_TIMEOUT_SEC:
                s.waiting.remove(ws)
                try:
                    await ws.send(json.dumps({
                        "type": "search_failed",
                        "message": "could not find opponent within 1 minute",
                    }))
                except Exception:
                    pass
                print(f"{info['username']} search timed out")
