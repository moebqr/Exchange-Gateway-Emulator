import unittest
from src.order_matching import OrderMatchingEngine, Order

class TestOrderMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OrderMatchingEngine()

    def test_exact_match(self):
        buy_order = Order("buy1", "AAPL", "buy", 150.0, 100)
        sell_order = Order("sell1", "AAPL", "sell", 150.0, 100)
        
        self.engine.add_order(buy_order)
        result = self.engine.add_order(sell_order)
        
        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["trade"]["symbol"], "AAPL")
        self.assertEqual(result["trade"]["price"], 150.0)
        self.assertEqual(result["trade"]["quantity"], 100)

    def test_unmatched_orders(self):
        buy_order = Order("buy1", "AAPL", "buy", 150.0, 100)
        sell_order = Order("sell1", "AAPL", "sell", 151.0, 100)
        
        buy_result = self.engine.add_order(buy_order)
        sell_result = self.engine.add_order(sell_order)
        
        self.assertEqual(buy_result["status"], "open")
        self.assertEqual(sell_result["status"], "open")
        self.assertEqual(len(self.engine.buy_orders["AAPL"]), 1)
        self.assertEqual(len(self.engine.sell_orders["AAPL"]), 1)

    def test_empty_order_book(self):
        buy_order = Order("buy1", "AAPL", "buy", 150.0, 100)
        result = self.engine.add_order(buy_order)
        
        self.assertEqual(result["status"], "open")
        self.assertEqual(len(self.engine.buy_orders["AAPL"]), 1)
        self.assertEqual(len(self.engine.sell_orders["AAPL"]), 0)

    def test_partial_match(self):
        buy_order = Order("buy1", "AAPL", "buy", 150.0, 100)
        sell_order = Order("sell1", "AAPL", "sell", 150.0, 50)
        
        self.engine.add_order(buy_order)
        result = self.engine.add_order(sell_order)
        
        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["trade"]["quantity"], 50)
        self.assertEqual(len(self.engine.buy_orders["AAPL"]), 1)
        self.assertEqual(self.engine.buy_orders["AAPL"][0].quantity, 50)

if __name__ == '__main__':
    unittest.main()
