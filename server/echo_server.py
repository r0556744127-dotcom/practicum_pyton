import asyncio
import websockets


async def handler(websocket):
    """רץ פעם אחת עבור כל לקוח שמתחבר."""
    print("client connected!")
    async for message in websocket:          # מחכה להודעות מהלקוח
        print("received:", message)
        await websocket.send("echo: " + message)   # מחזיר את אותה הודעה


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("server listening on ws://localhost:8765")
        await asyncio.Future()               # "חכה לנצח" — השרת לא נסגר


if __name__ == "__main__":
    asyncio.run(main())