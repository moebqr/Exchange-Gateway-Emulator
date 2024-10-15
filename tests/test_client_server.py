import unittest
import asyncio
import json
from src.server import ExchangeServer
from src.client import TradingClient

class TestClientServer(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.server = ExchangeServer("localhost", 6789)
        self.client = TradingClient("ws://localhost:6789", "test_client")

    def test_client_server_communication(self):
        async def run_test():
            server_task = asyncio.create_task(self.server.start())
            await asyncio.sleep(0.1)  # Give the server time to start

            await self.client.connect()
            order = {
                "type": "buy",
                "symbol": "AAPL",
                "price": 150.0,
                "quantity": 100
            }
            result = await self.client.send_order(order)
            
            self.assertIsNotNone(result)
            self.assertIn("status", result)
            
            await self.client.websocket.close()
            server_task.cancel()

        self.loop.run_until_complete(run_test())

    def test_json_validation(self):
        async def run_test():
            server_task = asyncio.create_task(self.server.start())
            await asyncio.sleep(0.1)  # Give the server time to start

            await self.client.connect()
            invalid_order = "This is not a JSON"
            
            with self.assertRaises(json.JSONDecodeError):
                await self.client.websocket.send(invalid_order)
                response = await self.client.websocket.recv()
                json.loads(response)
            
            await self.client.websocket.close()
            server_task.cancel()

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()

