import asyncio
import json
import websockets
from websockets import WebSocketServerProtocol
from typing import Dict, Any, Set, List
import cProfile
import pstats
import io
import uuid
from src.order_matching import OrderMatchingEngine, Order
from src.utils import profile, track_latency
from src.config import BATCH_SIZE, PROCESSING_DELAY

class ExchangeServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.order_matching_engine = OrderMatchingEngine()
        self.order_queue: List[Dict[str, Any]] = []
        self.processing_lock = asyncio.Lock()

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        finally:
            self.clients.remove(websocket)

    async def process_message(self, websocket: WebSocketServerProtocol, message: str):
        try:
            order_data = json.loads(message)
            order = Order(
                order_id=str(uuid.uuid4()),  # Generate a unique ID
                symbol=order_data['symbol'],
                order_type=order_data['type'],
                price=order_data['price'],
                quantity=order_data['quantity']
            )
            self.order_queue.append((websocket, order))
            if len(self.order_queue) >= BATCH_SIZE:  # Process in batches of 10
                await self.process_order_batch()
        except json.JSONDecodeError:
            await websocket.send(json.dumps({"error": "Invalid JSON format"}))

    @profile
    @track_latency
    async def process_order_batch(self):
        async with self.processing_lock:
            batch = self.order_queue[:BATCH_SIZE]
            self.order_queue = self.order_queue[BATCH_SIZE:]

            for websocket, order in batch:
                result = await self.order_matching_engine.process_order(order)
                await websocket.send(json.dumps(result))

    async def start(self):
        server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            tcp_nodelay=True  # Enable TCP_NODELAY to minimize latency
        )
        print(f"Server started on ws://{self.host}:{self.port}")
        
        # Start the order processing loop
        asyncio.create_task(self.order_processing_loop())
        
        await server.wait_closed()

    async def order_processing_loop(self):
        while True:
            if self.order_queue:
                await self.process_order_batch()
            await asyncio.sleep(PROCESSING_DELAY)  # Small delay to prevent busy-waiting

async def main():
    server = ExchangeServer("localhost", 6789)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
