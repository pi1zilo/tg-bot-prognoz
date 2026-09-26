"""
Root entrypoint for Prognoz Weather Telegram Bot.
Delegates execution to src.main:main.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root and src directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

for directory in (BASE_DIR, SRC_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from src.main import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
