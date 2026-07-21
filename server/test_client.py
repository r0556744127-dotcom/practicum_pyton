import asyncio
import json
import websockets


def print_board(rows):
    print("-" * 24)
    for row in rows:
        print(" ".join(row))


async def main():
    async with websockets.connect("ws://localhost:8765") as websocket:
        welcome = json.loads(await websocket.recv())
        color = welcome["color"]
        print("connected as:", color)

        # לבן שולח מהלך חייל; שחור שולח מהלך חייל משלו
        if color == "w":
           move = {"type": "move", "from": [6, 0], "to": [5, 0]}
        elif color == "b":
             move = {"type": "move", "from": [1, 7], "to": [2, 7]}
        else:
            move = None

        if move:
            await websocket.send(json.dumps(move))
            print("sent move:", move["from"], "->", move["to"])

        # מקבלים ~60 עדכוני מצב (3 שניות) ומדפיסים כל עשירי
        for i in range(60):
            state = json.loads(await websocket.recv())
            if i % 10 == 0:
                print_board(state["board"])


if __name__ == "__main__":
    asyncio.run(main())