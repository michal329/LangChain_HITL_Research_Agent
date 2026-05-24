import logging

# Configure basic application-wide logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance for the given module name.
    """
    return logging.getLogger(name)
