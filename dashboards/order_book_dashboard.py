import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import defaultdict
import asyncio
import websockets
import json
import time

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
    
    return fig, avg_latency, order_throughput, total_trades

async def websocket_client():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                # Update order book
                if data['status'] == 'open':
                    order = data['order']
                    order_book[order['symbol']][order['type']][order['price']] += order['quantity']
                elif data['status'] == 'matched':
                    trade = data['trade']
                    order_book[trade['symbol']]['buy'][trade['price']] -= trade['quantity']
                    order_book[trade['symbol']]['sell'][trade['price']] -= trade['quantity']
                    metrics['total_trades'] += 1
                
                # Update metrics
                metrics['avg_latency'] = data.get('latency', metrics['avg_latency'])
                metrics['order_throughput'] = data.get('throughput', metrics['order_throughput'])
                
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed. Reconnecting...")
                break

if __name__ == '__main__':
    # Start the WebSocket client in a separate thread
    loop = asyncio.get_event_loop()
    loop.create_task(websocket_client())
    
    # Run the Dash app
    app.run_server(debug=True)

