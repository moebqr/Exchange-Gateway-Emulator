import logging

# WebSocket configuration
WEBSOCKET_PORT = 6789
WEBSOCKET_HOST = 'localhost'

# Supported symbols
SUPPORTED_SYMBOLS = ["AAPL", "GOOG", "TSLA"]

# Logging configuration
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'exchange_gateway.log'

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, filename=LOG_FILE)
logger = logging.getLogger(__name__)

# Enable console logging as well
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(console_handler)

logger.info("Configuration loaded")

# Add these configurations
BATCH_SIZE = 10
PROCESSING_DELAY = 0.01


def some_function():
    pass

