import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    log_file: str = "logs/trading_bot.log",
    log_level: int = logging.INFO,
    console_level: int = logging.WARNING,
) -> None:
    """
    Configure logging for the trading bot.
    Sets up a rotating file handler and a console handler.
    Prevents duplicate handlers if called more than once.
    """
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return  # already configured, skip setup

    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root_logger.setLevel(min(log_level, console_level))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File Handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Silence noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for a specific module.
    """
    return logging.getLogger(name)
