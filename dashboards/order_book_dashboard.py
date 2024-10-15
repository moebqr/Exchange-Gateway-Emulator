import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import defaultdict
import asyncio
import websockets
import json
import time
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the Dash app
app = dash.Dash(__name__)

# Initialize data structures
order_book = defaultdict(lambda: {'buy': defaultdict(int), 'sell': defaultdict(int)})
metrics = {
    'avg_latency': 0,
    'order_throughput': 0,
    'total_trades': 0
}

# Layout of the dashboard
app.layout = html.Div([
    html.H1('Real-time Order Book Dashboard'),
    
    dcc.Graph(id='order-book-chart'),
    
    html.Div([
        html.Div([
            html.H3('Average Latency'),
            html.H4(id='avg-latency', children='0 ms')
        ], className='metric'),
        html.Div([
            html.H3('Order Throughput'),
            html.H4(id='order-throughput', children='0 orders/s')
        ], className='metric'),
        html.Div([
            html.H3('Total Trades'),
            html.H4(id='total-trades', children='0')
        ], className='metric')
    ], className='metrics-container'),
    
    dcc.Interval(
        id='interval-component',
        interval=1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    [Output('order-book-chart', 'figure'),
     Output('avg-latency', 'children'),
     Output('order-throughput', 'children'),
     Output('total-trades', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    logger.debug(f"Updating dashboard. Current order book: {order_book}")
    # Update order book chart
    buy_prices = list(order_book['AAPL']['buy'].keys())
    buy_quantities = list(order_book['AAPL']['buy'].values())
    sell_prices = list(order_book['AAPL']['sell'].keys())
    sell_quantities = list(order_book['AAPL']['sell'].values())
    
    fig = go.Figure(data=[
        go.Bar(name='Buy Orders', x=buy_prices, y=buy_quantities, marker_color='green'),
        go.Bar(name='Sell Orders', x=sell_prices, y=sell_quantities, marker_color='red')
    ])
    
    fig.update_layout(
        title='AAPL Order Book Depth',
        xaxis_title='Price',
        yaxis_title='Quantity',
        barmode='group'
    )
    
    # Update metrics
    avg_latency = f"{metrics['avg_latency']:.2f} ms"
    order_throughput = f"{metrics['order_throughput']:.2f} orders/s"
    total_trades = str(metrics['total_trades'])
    
    logger.debug(f"Updated metrics: Latency={avg_latency}, Throughput={order_throughput}, Trades={total_trades}")
    return fig, avg_latency, order_throughput, total_trades

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
                                order_book[order.get('symbol', '')][order.get('order_type', '')][order.get('price', 0)] += order.get('quantity', 0)
                                logger.info(f"Updated order book: {order_book}")
                            elif order_data.get('status') == 'matched':
                                trade = order_data.get('trade', {})
                                order_book[trade.get('symbol', '')]['buy'][trade.get('price', 0)] -= trade.get('quantity', 0)
                                order_book[trade.get('symbol', '')]['sell'][trade.get('price', 0)] -= trade.get('quantity', 0)
                                metrics['total_trades'] += 1
                                logger.info(f"Matched trade. Updated order book: {order_book}")
                            
                            # Update metrics
                            metrics['avg_latency'] = order_data.get('latency', metrics['avg_latency'])
                            metrics['order_throughput'] = order_data.get('throughput', metrics['order_throughput'])
                            logger.info(f"Updated metrics: {metrics}")
                        
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed. Reconnecting...")
                        break
        except Exception as e:
            logger.error(f"Error in WebSocket client: {e}")
            await asyncio.sleep(5)  # Wait before trying to reconnect

if __name__ == '__main__':
    # Start the WebSocket client in a separate thread
    loop = asyncio.get_event_loop()
    loop.create_task(websocket_client())
    
    # Run the Dash app
    app.run_server(debug=True)
