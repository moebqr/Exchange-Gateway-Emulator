# 📈 Latency-Optimized Exchange Gateway Emulator

## Project Overview

This project implements a real-time, low-latency exchange gateway emulator in Python, designed to simulate a high-frequency trading environment. The emulator is architected to handle large volumes of orders with minimal latency, making it suitable for performance testing and strategy development.

### Architecture

- **WebSocket Server**: The server is built using Python's `websockets` library, enabling efficient real-time communication with multiple clients. It handles incoming order requests, processes them, and sends back confirmations or rejections. The server is designed to be non-blocking, leveraging `asyncio` for concurrent operations.

- **Order Matching Engine**: The core of the emulator, implemented in `src/order_matching.py`, maintains an in-memory order book. It uses efficient data structures to store and match buy and sell orders. The engine supports various order types and matching algorithms, ensuring high throughput and low latency.

- **Client Simulation**: The client component, found in `src/client.py`, acts as a trading participant. It can generate random orders or be configured to follow specific trading strategies. The client connects to the server via WebSockets, sending orders and receiving trade confirmations.

- **Real-Time Dashboard**: The dashboard, implemented using Dash and Plotly, provides a visual interface for monitoring the order book and key performance metrics. It updates in real-time, offering insights into order flow, latency, and throughput.

### Key Features

- **Asynchronous Processing**: Utilizes Python's `asyncio` to handle multiple client connections and order processing concurrently, reducing latency and improving scalability.

- **Performance Profiling**: Integrated with `cProfile` for detailed performance analysis, allowing users to identify bottlenecks and optimize the system.

- **Comprehensive Testing**: Includes unit tests and stress tests to ensure reliability and performance under load. The stress tests simulate hundreds of concurrent clients to evaluate system robustness.

## 📁 Project Structure

Here's an overview of the project's file structure:

```
.
├── src
│   ├── server.py
│   ├── order_matching.py
│   └── client.py
├── dashboards
│   └── order_book_dashboard.py
├── tests
│   ├── stress_test.py
│   ├── test_client_server.py
│   └── test_order_matching.py
├── README.md
├── requirements.txt
└── latency-optimized-exchange-gateway-emulator
    └── requirements.txt
```

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
   git clone https://github.com/moebqr/exchange-gateway-emulator.git
   cd exchange-gateway-emulator
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

- Throughput: ~6000 orders/second
- Average Latency: 10 ms
- Median Latency: 8 ms
- 95th Percentile Latency: 20 ms

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

## 🤝 Contributing

Contributions to this project are welcome! Please fork the repository and submit a pull request with your proposed changes.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
