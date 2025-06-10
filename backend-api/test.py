# %%
import asyncio
import websockets


async def test_ws():
    uri = "ws://localhost:8000/ws/1"
    async with websockets.connect(uri) as websocket:
        await websocket.send("whats up? /no_think")
        while True:
            response = await websocket.recv()
            print(f"📩 Received Response: {response}")


if __name__ == "__main__":
    asyncio.run(test_ws())
