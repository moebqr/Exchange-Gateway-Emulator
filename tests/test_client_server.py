import unittest
import asyncio
import json
from src.server import ExchangeServer
from src.client import TradingClient

class TestClientServer(unittest.TestCase):
    def setUp(self):
        # Create a new event loop for each test
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        # Close the event loop after each test
        self.loop.close()

    def test_client_server_communication(self):
        async def run_test():
            # Start the server
            server = ExchangeServer("localhost", 6790)
            server_task = asyncio.create_task(server.start())
            await asyncio.sleep(0.1)  # Give the server time to start

            # Create and connect a client
            client = TradingClient("ws://localhost:6790", "test_client")
            await client.connect()

            # Create a sample order
            order = {
                "type": "buy",
                "symbol": "AAPL",
                "price": 150.0,
                "quantity": 100
            }

            # Send the order and get the result
            result = await client.send_order(order)
            
            # Assert that we received a valid response
            self.assertIsNotNone(result)
            self.assertIn("status", result)
            
            # Clean up: close client connection and cancel server task
            await client.websocket.close()
            server_task.cancel()

        self.loop.run_until_complete(run_test())

    def test_json_validation(self):
        async def run_test():
            # Start the server
            server = ExchangeServer("localhost", 6791)
            server_task = asyncio.create_task(server.start())
            await asyncio.sleep(0.1)  # Give the server time to start

            # Create and connect a client
            client = TradingClient("ws://localhost:6791", "test_client")
            await client.connect()

            # Send an invalid JSON string
            invalid_order = "This is not a JSON"
            await client.websocket.send(invalid_order)

            # Receive and parse the response
            response = await client.websocket.recv()
            response_data = json.loads(response)
            
            # Assert that we received the expected error message
            self.assertEqual(response_data, {"error": "Invalid JSON format"})

            # Clean up: close client connection and cancel server task
            await client.websocket.close()
            server_task.cancel()

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
