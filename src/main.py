import asyncio
import logging
import sys
from pathlib import Path

# Ensure project root and src directory are in sys.path
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
for directory in (PROJECT_ROOT, SRC_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeDefault

from src.app.config import BOT_TOKEN
from src.app.database.database import init_db
from src.app.handlers import start, callbacks
from src.app.utils.logger import setup_logging


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="pogoda", description="🌤 Погода на сегодня (или /pogoda <город>)"),
        BotCommand(command="start", description="🚀 Главное меню и выбор дня"),
    ]
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logging.info("Команды бота успешно установлены в Telegram.")
    except Exception as e:
        logging.warning(f"Не удалось установить команды бота в Telegram: {e}")


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

    # Register bot commands in Telegram UI
    await set_bot_commands(bot)

    logging.info("Бот запущен и ожидает сообщения...")

    # Drop pending updates and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
