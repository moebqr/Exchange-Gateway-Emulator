import unittest
import asyncio
import json
from src.server import ExchangeServer
from src.client import TradingClient

class TestClientServer(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_client_server_communication(self):
        async def run_test():
            server = ExchangeServer("localhost", 6790)
            server_task = asyncio.create_task(server.start())
            await asyncio.sleep(0.1)  # Give the server time to start

            client = TradingClient("ws://localhost:6790", "test_client")
            await client.connect()
            order = {
                "type": "buy",
                "symbol": "AAPL",
                "price": 150.0,
                "quantity": 100
            }
            result = await client.send_order(order)
            
            self.assertIsNotNone(result)
            self.assertIn("status", result)
            
            await client.websocket.close()
            server_task.cancel()

        self.loop.run_until_complete(run_test())

    def test_json_validation(self):
        async def run_test():
            server = ExchangeServer("localhost", 6791)
            server_task = asyncio.create_task(server.start())
            await asyncio.sleep(0.1)  # Give the server time to start

            client = TradingClient("ws://localhost:6791", "test_client")
            await client.connect()
            invalid_order = "This is not a JSON"
            
            await client.websocket.send(invalid_order)
            response = await client.websocket.recv()
            response_data = json.loads(response)
            
            self.assertEqual(response_data, {"error": "Invalid JSON format"})

            await client.websocket.close()
            server_task.cancel()

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
