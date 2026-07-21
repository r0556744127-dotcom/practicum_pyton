import asyncio
import websockets


async def main():
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send("hello")          # send a message to the server
        reply = await websocket.recv()         # wait for the server's answer
        print(reply)                           # print it


if __name__ == "__main__":
    asyncio.run(main())