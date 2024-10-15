from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

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

    def add_order(self, order: Order) -> Dict[str, Any]:
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
            if order.price == opposite_order.price:
                return opposite_order
        return None

    def _execute_trade(self, order1: Order, order2: Order) -> Dict[str, Any]:
        trade_quantity = min(order1.quantity, order2.quantity)
        
        # Update order quantities
        order1.quantity -= trade_quantity
        order2.quantity -= trade_quantity
        
        # Remove or update orders in the book
        if order1.order_type == 'buy':
            self.buy_orders[order1.symbol] = [order for order in self.buy_orders[order1.symbol] if order.order_id != order1.order_id]
            self.sell_orders[order1.symbol] = [order for order in self.sell_orders[order1.symbol] if order.order_id != order2.order_id]
        else:
            self.sell_orders[order1.symbol] = [order for order in self.sell_orders[order1.symbol] if order.order_id != order1.order_id]
            self.buy_orders[order1.symbol] = [order for order in self.buy_orders[order1.symbol] if order.order_id != order2.order_id]

        # If there's remaining quantity, add back to the book
        if order1.quantity > 0:
            if order1.order_type == 'buy':
                self.buy_orders[order1.symbol].append(order1)
            else:
                self.sell_orders[order1.symbol].append(order1)
        if order2.quantity > 0:
            if order2.order_type == 'buy':
                self.buy_orders[order2.symbol].append(order2)
            else:
                self.sell_orders[order2.symbol].append(order2)

        return {
            "status": "matched",
            "message": "Trade executed",
            "trade": {
                "symbol": order1.symbol,
                "price": order1.price,
                "quantity": trade_quantity,
                "buy_order_id": order1.order_id if order1.order_type == 'buy' else order2.order_id,
                "sell_order_id": order2.order_id if order1.order_type == 'buy' else order1.order_id
            }
        }

    def process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            order = Order(
                order_id=order_data.get('order_id', ''),
                symbol=order_data['symbol'],
                order_type=order_data['order_type'],  # Change 'type' to 'order_type'
                price=order_data['price'],
                quantity=order_data['quantity']
            )
            logger.debug(f"Processing order: {order}")
            result = self.add_order(order)
            logger.debug(f"Order processing result: {result}")
            return result
        except KeyError as e:
            logger.error(f"Missing key in order data: {e}", exc_info=True)
            return {"error": f"Missing key in order data: {str(e)}"}
        except Exception as e:
            logger.error(f"Error processing order: {e}", exc_info=True)
            return {"error": f"Error processing order: {str(e)}"}
