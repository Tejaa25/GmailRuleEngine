import logging
import sys
from config import Config


def setup_logger(name: str) -> logging.Logger:
    """Function to create and configure a logger."""

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_level = getattr(logging, Config.LOG_LEVEL)
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    formatter = logging.Formatter(Config.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance. Use this in all modules. Uses (__name__)"""

    return setup_logger(name)
