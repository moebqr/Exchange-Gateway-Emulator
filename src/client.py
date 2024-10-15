import asyncio
import json
import websockets
import random
from typing import Dict, Any
import socket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingClient:
    def __init__(self, uri: str, client_id: str):
        self.uri = uri
        self.client_id = client_id
        self.websocket = None

    async def connect(self):
        while True:
            try:
                self.websocket = await websockets.connect(
                    self.uri,
                    extra_headers={"Client-ID": self.client_id}
                )
                # Set TCP_NODELAY option on the socket
                sock = self.websocket.transport.get_extra_info('socket')
                if sock is not None:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                logger.info("Connected to the server")
                return
            except Exception as e:
                logger.error(f"Failed to connect: {e}")
                await asyncio.sleep(5)  # Wait for 5 seconds before retrying

    async def send_order(self, order: Dict[str, Any]):
        try:
            await self.websocket.send(json.dumps(order))
            logger.info(f"Sent order: {order}")
            
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            try:
                data = json.loads(response)
                logger.info(f"Received confirmation: {data}")
                return data
            except json.JSONDecodeError:
                logger.error(f"Received invalid JSON: {response}")
                return None
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for server response")
            return None
        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed unexpectedly")
            await self.connect()  # Try to reconnect
            return None

    async def run(self):
        await self.connect()
        
        while True:
            try:
                # Generate and send a random order
                order = self.generate_random_order()
                confirmation = await self.send_order(order)
                
                # Wait for a short time before sending the next order
                await asyncio.sleep(random.uniform(0.5, 2.0))
            except Exception as e:
                logger.error(f"Error in run loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

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
