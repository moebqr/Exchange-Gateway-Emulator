import asyncio
import json
import websockets
import random
from typing import Dict, Any
import socket
import logging

# Configure logging
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
                # Attempt to establish a WebSocket connection
                self.websocket = await websockets.connect(
                    self.uri,
                    extra_headers={"Client-ID": self.client_id}
                )
                # Set TCP_NODELAY option on the socket for lower latency
                sock = self.websocket.transport.get_extra_info('socket')
                if sock is not None:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                logger.info("Connected to the server")
                
                # Subscribe to the trades channel after successful connection
                await self.subscribe_to_trades()
                return
            except Exception as e:
                logger.error(f"Failed to connect: {e}")
                await asyncio.sleep(5)  # Wait for 5 seconds before retrying

    async def subscribe_to_trades(self):
        # Prepare and send subscription message
        subscription_message = {
            "type": "subscribe",
            "channel": "trades"
        }
        await self.websocket.send(json.dumps(subscription_message))
        logger.info("Subscribed to trades channel")

    async def send_order(self, order: Dict[str, Any]):
        try:
            # Send the order to the server
            await self.websocket.send(json.dumps(order))
            logger.info(f"Sent order: {order}")
            
            # Wait for server response with a 5-second timeout
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
            await self.connect()  # Attempt to reconnect
            return None

    async def listen_for_updates(self):
        while True:
            try:
                # Continuously listen for incoming messages
                message = await self.websocket.recv()
                data = json.loads(message)
                if data.get('type') == 'order_update':
                    logger.info(f"Received order update: {data}")
                    # Process the order update as needed (implement specific logic here)
            except websockets.exceptions.ConnectionClosed:
                logger.error("WebSocket connection closed. Reconnecting...")
                await self.connect()
            except Exception as e:
                logger.error(f"Error while listening for updates: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def run(self):
        await self.connect()
        
        # Start listening for updates in a separate task
        asyncio.create_task(self.listen_for_updates())
        
        while True:
            try:
                # Generate and send a random order
                order = self.generate_random_order()
                confirmation = await self.send_order(order)
                
                # Wait for a short random time before sending the next order
                await asyncio.sleep(random.uniform(0.5, 2.0))
            except Exception as e:
                logger.error(f"Error in run loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    def generate_random_order(self) -> Dict[str, Any]:
        # List of available symbols and order types
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]
        order_types = ["buy", "sell"]
        
        # Generate a random order
        order = {
            "type": random.choice(order_types),
            "symbol": random.choice(symbols),
            "price": round(random.uniform(100, 1000), 2),
            "quantity": random.randint(1, 100)
        }
        logger.info(f"Generated random order: {order}")
        return order

async def main():
    # Create and run a trading client
    client = TradingClient("ws://localhost:6789", "client1")
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
