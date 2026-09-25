import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config import BOT_TOKEN
from app.database.database import init_db
from app.handlers import start, callbacks
from app.utils.logger import setup_logging

async def main():
    setup_logging()

    if not BOT_TOKEN:
        logging.error("BOT_TOKEN не задан в переменной окружения!")
        sys.exit(1)

    # Initialize database
    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Include routers
    dp.include_router(start.router)
    dp.include_router(callbacks.router)

    logging.info("Бот запущен и ожидает сообщения...")
    
    # Drop pending updates and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")

