import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import asyncio
import websockets
import json
import threading
from collections import defaultdict
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variables to store real-time data
order_book = defaultdict(lambda: {'buy': defaultdict(float), 'sell': defaultdict(float)})
metrics = {
    'avg_latency': 0,
    'order_throughput': 0,
    'total_trades': 0
}

async def websocket_client():
    uri = "ws://localhost:6789"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Connected to WebSocket server")
                await websocket.send(json.dumps({"type": "subscribe", "channel": "trades"}))
                logger.info("Sent subscription request")
                while True:
                    try:
                        message = await websocket.recv()
                        logger.info(f"Received message: {message}")
                        data = json.loads(message)
                        
                        if data.get('type') == 'order_update':
                            order_data = data.get('data', {})
                            
                            # Update order book
                            if order_data.get('status') == 'open':
                                order = order_data.get('order', {})
                                symbol = order.get('symbol', '')
                                order_type = order.get('type', '')
                                price = order.get('price', 0)
                                quantity = order.get('quantity', 0)
                                logger.info(f"Updating order book: {symbol} {order_type} {price} {quantity}")
                                order_book[symbol][order_type][price] += quantity
                            elif order_data.get('status') == 'matched':
                                trade = order_data.get('trade', {})
                                symbol = trade.get('symbol', '')
                                price = trade.get('price', 0)
                                quantity = trade.get('quantity', 0)
                                logger.info(f"Matched trade: {symbol} {price} {quantity}")
                                order_book[symbol]['buy'][price] -= quantity
                                order_book[symbol]['sell'][price] -= quantity
                                metrics['total_trades'] += 1
                            
                            # Update metrics
                            metrics['avg_latency'] = order_data.get('latency', metrics['avg_latency'])
                            metrics['order_throughput'] = order_data.get('throughput', metrics['order_throughput'])
                            logger.info(f"Updated metrics: {metrics}")
                            logger.info(f"Current order book: {order_book}")
                        else:
                            logger.warning(f"Received unknown message type: {data.get('type')}")
                    
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed. Reconnecting...")
                        break
        except Exception as e:
            logger.error(f"Error in WebSocket client: {e}")
            await asyncio.sleep(5)  # Wait before trying to reconnect

def run_websocket_client():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_client())

def plot_order_book(symbol):
    buy_prices = list(order_book[symbol]['buy'].keys())
    buy_quantities = list(order_book[symbol]['buy'].values())
    sell_prices = list(order_book[symbol]['sell'].keys())
    sell_quantities = list(order_book[symbol]['sell'].values())
    
    if not buy_prices and not sell_prices:
        return go.Figure().add_annotation(
            x=0.5, y=0.5,
            text="No data available",
            showarrow=False,
            font=dict(size=20)
        )
    
    fig = go.Figure(data=[
        go.Bar(name='Buy Orders', x=buy_prices, y=buy_quantities, marker_color='green'),
        go.Bar(name='Sell Orders', x=sell_prices, y=sell_quantities, marker_color='red')
    ])
    
    fig.update_layout(
        title=f'{symbol} Order Book Depth',
        xaxis_title='Price',
        yaxis_title='Quantity',
        barmode='group'
    )
    
    return fig

def main():
    st.set_page_config(page_title="Real-Time Order Book Dashboard", layout="wide")
    st.title("Real-Time Order Book Dashboard")

    # Available symbols
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]  # Add more symbols as needed
    
    # Start WebSocket client thread
    threading.Thread(target=run_websocket_client, daemon=True).start()

    # Sidebar for stock selection
    selected_symbol = st.sidebar.selectbox("Select a stock", symbols)

    # Main content
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Order Book")
        order_book_chart = st.empty()

    with col2:
        st.subheader("Metrics")
        latency_metric = st.empty()
        throughput_metric = st.empty()
        trades_metric = st.empty()

    # Debug information
    st.subheader("Debug Information")
    debug_info = st.empty()

    # Update dashboard in real-time
    while True:
        try:
            fig = plot_order_book(selected_symbol)
            order_book_chart.plotly_chart(fig, use_container_width=True)
        
            latency_metric.metric("Average Latency", f"{metrics['avg_latency']:.2f} ms")
            throughput_metric.metric("Order Throughput", f"{metrics['order_throughput']:.2f} orders/s")
            trades_metric.metric("Total Trades", metrics['total_trades'])
        
            # Update debug information
            debug_info.json({
                "Current Order Book": dict(order_book),
                "Metrics": metrics
            })
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Error in main loop: {e}", exc_info=True)
        
        time.sleep(1)  # Update every second

if __name__ == "__main__":
    main()
