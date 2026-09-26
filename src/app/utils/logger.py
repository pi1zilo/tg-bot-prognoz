import logging
from pathlib import Path
from src.app.config import BASE_DIR

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
ERROR_LOG_PATH = LOGS_DIR / "errors.log"

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplication
    if logger.handlers:
        logger.handlers.clear()

    # File handler for errors with date and time
    file_handler = logging.FileHandler(ERROR_LOG_PATH, encoding="utf-8")
    file_handler.setLevel(logging.ERROR)
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s]: %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_error(error_msg: str, exc: Exception = None):
    logger = logging.getLogger("weather_bot.error")
    if exc:
        logger.error(f"{error_msg} | Exception: {exc}", exc_info=True)
    else:
        logger.error(error_msg)
