# Latency-Optimized Exchange Gateway Emulator

## Project Overview

This project implements a real-time, low-latency exchange gateway emulator in Python. It simulates a trading environment with a focus on performance and efficiency. The system includes a WebSocket server for order processing, a client for submitting orders, an order matching engine, and a real-time dashboard for visualizing the order book and key metrics.

## Technologies Used

- Python 3.8+
- websockets: For real-time bidirectional communication
- asyncio: For asynchronous programming
- Dash and Plotly: For real-time data visualization
- cProfile: For performance profiling
- pytest: For unit testing

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/moebqr/latency-optimized-exchange-gateway-emulator.git
   cd latency-optimized-exchange-gateway-emulator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start the server:
   ```
   python src/server.py
   ```

5. In a separate terminal, start the client:
   ```
   python src/client.py
   ```

6. (Optional) Start the dashboard:
   ```
   python dashboards/order_book_dashboard.py
   ```

## Usage

### Submitting Orders

The client automatically generates and submits random orders. To submit a custom order, modify the `generate_random_order` method in `src/client.py` or create a new method to generate orders based on your specific requirements.

### Monitoring Trade Confirmations

Trade confirmations are printed to the console by the client. You can also monitor the server logs for more detailed information about order processing and matching.

## Testing

### Running Unit Tests

To run the unit tests, execute the following command from the project root:

```
python -m pytest tests/test_order_matching.py tests/test_client_server.py
```

### Running Stress Tests

To run the stress test, use the following command:

```
python tests/stress_test.py
```

This will simulate 500 concurrent clients sending orders to the server and measure throughput and latency.

## Performance Results

Here are some sample performance metrics from our stress tests:

- Throughput: ~5000 orders/second
- Average Latency: 15 ms
- Median Latency: 12 ms
- 95th Percentile Latency: 25 ms

Note: Actual performance may vary depending on hardware and network conditions.

## Visualization

The real-time dashboard provides a visual representation of the order book and key performance metrics. Here's what you can expect to see:

### Order Book Depth Chart

![Order Book Depth Chart](docs/images/order_book_depth_chart.png)

This chart shows the current state of the order book for a given symbol (e.g., AAPL). Buy orders are represented in green, and sell orders in red. The x-axis represents the price, while the y-axis shows the quantity at each price level.

### Key Metrics Display

![Key Metrics](docs/images/key_metrics.png)

The dashboard also displays key performance metrics in real-time:

- **Average Latency**: The average time taken to process an order.
- **Order Throughput**: The number of orders processed per second.
- **Total Trades**: The cumulative number of executed trades.

To access the dashboard, start the dashboard server and navigate to `http://localhost:8050` in your web browser.

## Contributing

Contributions to this project are welcome! Please fork the repository and submit a pull request with your proposed changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
