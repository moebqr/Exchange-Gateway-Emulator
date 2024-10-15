from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Order:
    order_id: str
    symbol: str
    order_type: str  # 'buy' or 'sell'
    price: float
    quantity: int

class OrderMatchingEngine:
    def __init__(self):
        self.buy_orders: Dict[str, List[Order]] = defaultdict(list)
        self.sell_orders: Dict[str, List[Order]] = defaultdict(list)

    def add_order(self, order: Order) -> Dict[str, any]:
        if order.order_type == 'buy':
            matched_order = self._match_order(order, self.sell_orders[order.symbol])
            if matched_order:
                return self._execute_trade(order, matched_order)
            self.buy_orders[order.symbol].append(order)
            return {"status": "open", "message": "Order added to the book"}
        elif order.order_type == 'sell':
            matched_order = self._match_order(order, self.buy_orders[order.symbol])
            if matched_order:
                return self._execute_trade(order, matched_order)
            self.sell_orders[order.symbol].append(order)
            return {"status": "open", "message": "Order added to the book"}
        else:
            return {"status": "error", "message": "Invalid order type"}

    def _match_order(self, order: Order, opposite_orders: List[Order]) -> Optional[Order]:
        for opposite_order in opposite_orders:
            if (order.price == opposite_order.price and 
                order.quantity == opposite_order.quantity):
                return opposite_order
        return None

    def _execute_trade(self, order1: Order, order2: Order) -> Dict[str, any]:
        # Remove matched orders from the book
        if order1.order_type == 'buy':
            self.sell_orders[order1.symbol].remove(order2)
        else:
            self.buy_orders[order1.symbol].remove(order2)

        return {
            "status": "matched",
            "message": "Trade executed",
            "trade": {
                "symbol": order1.symbol,
                "price": order1.price,
                "quantity": order1.quantity,
                "buy_order_id": order1.order_id if order1.order_type == 'buy' else order2.order_id,
                "sell_order_id": order2.order_id if order1.order_type == 'buy' else order1.order_id
            }
        }

    def process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        order = Order(
            order_id=order_data.get('order_id', ''),
            symbol=order_data['symbol'],
            order_type=order_data['type'],
            price=order_data['price'],
            quantity=order_data['quantity']
        )
        return self.add_order(order)
