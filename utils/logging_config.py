"""Logging configuration for Universal Video Factory."""
import logging
import sys
from pathlib import Path
from utils.config import Config


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup application logging."""
    # Create logs directory
    log_dir = Config.BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Setup root logger
    logger = logging.getLogger("universal_video_factory")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


# Initialize logger
logger = setup_logging()
