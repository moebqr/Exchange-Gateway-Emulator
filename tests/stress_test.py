import asyncio
import time
import statistics
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import ExchangeServer
from src.client import TradingClient

async def run_client(client_id, num_orders):
    """
    Simulates a single client sending orders and measures latencies.
    
    Args:
        client_id (int): Unique identifier for the client.
        num_orders (int): Number of orders to send.
    
    Returns:
        list: List of latencies (in milliseconds) for each order sent.
    """
    client = TradingClient(f"ws://localhost:6789", f"client_{client_id}")
    await client.connect()
    
    latencies = []
    for _ in range(num_orders):
        order = client.generate_random_order()
        start_time = time.time()
        await client.send_order(order)
        end_time = time.time()
        latencies.append((end_time - start_time) * 1000)  # Convert to ms
    
    await client.websocket.close()
    return latencies

async def run_stress_test(num_clients, orders_per_client):
    """
    Runs a stress test by simulating multiple clients sending orders concurrently.
    
    Args:
        num_clients (int): Number of clients to simulate.
        orders_per_client (int): Number of orders each client should send.
    """
    # Start the exchange server
    server = ExchangeServer("localhost", 6789)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(1)  # Give the server time to start

    start_time = time.time()
    
    # Create and run tasks for all clients
    client_tasks = [run_client(i, orders_per_client) for i in range(num_clients)]
    all_latencies = await asyncio.gather(*client_tasks)
    
    end_time = time.time()
    
    # Flatten the list of latencies
    all_latencies = [latency for client_latencies in all_latencies for latency in client_latencies]
    
    # Calculate and print test results
    total_orders = num_clients * orders_per_client
    total_time = end_time - start_time
    throughput = total_orders / total_time
    
    avg_latency = statistics.mean(all_latencies)
    median_latency = statistics.median(all_latencies)
    p95_latency = statistics.quantiles(all_latencies, n=20)[-1]  # 95th percentile
    
    print(f"Stress Test Results:")
    print(f"Total orders processed: {total_orders}")
    print(f"Throughput: {throughput:.2f} orders/second")
    print(f"Average latency: {avg_latency:.2f} ms")
    print(f"Median latency: {median_latency:.2f} ms")
    print(f"95th percentile latency: {p95_latency:.2f} ms")
    
    # Clean up: cancel the server task
    server_task.cancel()

if __name__ == "__main__":
    NUM_CLIENTS = 500
    ORDERS_PER_CLIENT = 10
    
    asyncio.run(run_stress_test(NUM_CLIENTS, ORDERS_PER_CLIENT))
