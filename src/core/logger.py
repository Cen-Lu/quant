import logging
from rich.logging import RichHandler  # Correct import path

def setup_logger(name: str = "TradingBot") -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger(name)