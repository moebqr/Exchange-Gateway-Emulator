import asyncio
import json
import websockets
import random
from typing import Dict, Any

class TradingClient:
    def __init__(self, uri: str, client_id: str):
        self.uri = uri
        self.client_id = client_id
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(
            self.uri,
            extra_headers={"Client-ID": self.client_id},
            tcp_nodelay=True  # Enable TCP_NODELAY to minimize latency
        )

    async def send_order(self, order: Dict[str, Any]):
        try:
            await self.websocket.send(json.dumps(order))
            print(f"Sent order: {order}")
            
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            try:
                data = json.loads(response)
                print(f"Received confirmation: {data}")
                return data
            except json.JSONDecodeError:
                print(f"Received invalid JSON: {response}")
                return None
        except asyncio.TimeoutError:
            print("Timeout waiting for server response")
            return None
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed unexpectedly")
            return None

    async def run(self):
        await self.connect()
        
        try:
            while True:
                # Generate and send a random order
                order = self.generate_random_order()
                confirmation = await self.send_order(order)
                
                # Wait for a short time before sending the next order
                await asyncio.sleep(random.uniform(0.5, 2.0))
        finally:
            await self.websocket.close()

    def generate_random_order(self) -> Dict[str, Any]:
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]
        order_types = ["buy", "sell"]
        return {
            "type": random.choice(order_types),
            "symbol": random.choice(symbols),
            "price": round(random.uniform(100, 1000), 2),
            "quantity": random.randint(1, 100)
        }

async def main():
    client = TradingClient("ws://localhost:6789", "client1")
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
