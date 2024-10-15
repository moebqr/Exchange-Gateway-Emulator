import logging
import time
import cProfile
import pstats
import io
from functools import wraps

logger = logging.getLogger(__name__)

def log_transaction(symbol: str, price: float, quantity: int, buy_order_id: str, sell_order_id: str):
    """Log each buy/sell transaction along with timestamps."""
    timestamp = time.time()
    logger.info(f"Transaction: Symbol={symbol}, Price={price}, Quantity={quantity}, "
                f"BuyOrderID={buy_order_id}, SellOrderID={sell_order_id}, Timestamp={timestamp}")

def track_latency(func):
    """Decorator to calculate and log the round-trip time for each order."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        logger.info(f"Latency for {func.__name__}: {latency:.2f} ms")
        return result
    return wrapper

def profile(func):
    """Decorator to profile a function using cProfile."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        logger.debug(f"Profile for {func.__name__}:\n{s.getvalue()}")
        return result
    return wrapper

# Example usage of the profile decorator
@profile
def example_function():
    # Some code to profile
    time.sleep(0.1)
    return "Example result"

if __name__ == "__main__":
    log_transaction("AAPL", 150.0, 100, "buy_123", "sell_456")
    example_function()
