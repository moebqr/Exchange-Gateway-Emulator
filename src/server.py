import asyncio
import json
import websockets
from websockets import WebSocketServerProtocol
from typing import Dict, Any, Set, List
import uuid
import logging
from src.order_matching import OrderMatchingEngine, Order
from src.utils import profile, track_latency
from src.config import BATCH_SIZE, PROCESSING_DELAY, WEBSOCKET_HOST, WEBSOCKET_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExchangeServer:
    """
    Handles WebSocket connections and order processing for the exchange.
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.order_matching_engine = OrderMatchingEngine()
        self.order_queue: List[Dict[str, Any]] = []
        self.processing_lock = asyncio.Lock()
        self.metrics = {
            'avg_latency': 0,
            'order_throughput': 0,
            'total_trades': 0
        }

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle a new WebSocket client connection.

        This method is called for each new client that connects to the server.
        It adds the client to the set of connected clients, processes incoming
        messages, and handles client disconnection.

        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection for the client.
            path (str): The path of the WebSocket connection (unused in this implementation).
        """
        logger.info(f"New client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        try:
            async for message in websocket:
                logger.debug(f"Received message: {message}")
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"Connection closed unexpectedly: {e}")
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected: {websocket.remote_address}")

    async def process_message(self, websocket: WebSocketServerProtocol, message: str):
        """
        Process an incoming message from a client.

        This method handles different types of messages, including subscriptions
        and order placements. It validates the message, creates an Order object,
        and adds it to the processing queue.

        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection for the client.
            message (str): The JSON-encoded message received from the client.
        """
        try:
            data = json.loads(message)
            if data.get('type') == 'subscribe':
                logger.info(f"Client subscribed to channel: {data.get('channel')}")
                return

            # Create an Order object from the received data
            order_data = data
            order = Order(
                order_id=str(uuid.uuid4()),
                symbol=order_data['symbol'],
                order_type=order_data['type'],
                price=order_data['price'],
                quantity=order_data['quantity']
            )
            self.order_queue.append((websocket, order))
            logger.debug(f"Order added to queue: {order}")

            # Trigger batch processing if queue reaches threshold
            if len(self.order_queue) >= BATCH_SIZE:
                await self.process_order_batch()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {message}")
            await websocket.send(json.dumps({"error": "Invalid JSON format"}))
        except KeyError as e:
            logger.error(f"Missing key in order data: {e}")
            await websocket.send(json.dumps({"error": f"Missing key in order data: {e}"}))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await websocket.send(json.dumps({"error": "Internal server error"}))

    @profile
    @track_latency
    async def process_order_batch(self):
        """
        Process a batch of orders from the queue.

        This method is called when the order queue reaches the BATCH_SIZE threshold.
        It processes orders in batches for improved efficiency, updates metrics,
        and broadcasts results to all connected clients.
        """
        async with self.processing_lock:
            batch = self.order_queue[:BATCH_SIZE]
            self.order_queue = self.order_queue[BATCH_SIZE:]

            logger.info(f"Processing batch of {len(batch)} orders")
            for websocket, order in batch:
                try:
                    logger.info(f"Processing order: {order}")
                    result = self.order_matching_engine.process_order(order.__dict__)
                    logger.info(f"Order processing result: {result}")
                    await websocket.send(json.dumps(result))
                    
                    # Update metrics
                    self.update_metrics(result)
                    
                    # Broadcast the result to all connected clients
                    broadcast_message = json.dumps({
                        "type": "order_update",
                        "data": {
                            **result,
                            "latency": self.metrics['avg_latency'],
                            "throughput": self.metrics['order_throughput']
                        }
                    })
                    logger.info(f"Broadcasting message: {broadcast_message}")
                    await self.broadcast(broadcast_message)
                except Exception as e:
                    logger.error(f"Error processing order: {e}", exc_info=True)
                    await websocket.send(json.dumps({"error": f"Error processing order: {str(e)}"}))

    def update_metrics(self, result: Dict[str, Any]):
        """
        Update the server's performance metrics based on the order processing result.

        Args:
            result (Dict[str, Any]): The result of processing an order.
        """
        # Update average latency
        if 'latency' in result:
            self.metrics['avg_latency'] = (self.metrics['avg_latency'] + result['latency']) / 2

        # Update order throughput (orders per second)
        self.metrics['order_throughput'] += 1

        # Update total trades if a trade occurred
        if result.get('status') == 'matched':
            self.metrics['total_trades'] += 1

    async def broadcast(self, message: str):
        """
        Broadcast a message to all connected clients.

        Args:
            message (str): The message to broadcast.
        """
        logger.info(f"Broadcasting message to {len(self.clients)} clients: {message}")
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Failed to send message to client: {client.remote_address}")

    async def start(self):
        """
        Start the WebSocket server and the order processing loop.
        """
        server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port
        )
        logger.info(f"Server started on ws://{self.host}:{self.port}")
        
        # Start the order processing loop
        asyncio.create_task(self.order_processing_loop())
        
        await server.wait_closed()

    async def order_processing_loop(self):
        while True:
            if self.order_queue:
                await self.process_order_batch()
            await asyncio.sleep(PROCESSING_DELAY)

async def main():
    """
    Main function to start the Exchange Server.
    """
    try:
        server = ExchangeServer(WEBSOCKET_HOST, WEBSOCKET_PORT)
        await server.start()
    except Exception as e:
        logger.error(f"Error in main server loop: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
