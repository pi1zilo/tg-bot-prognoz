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
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault, MenuButtonWebApp, WebAppInfo

from src.app.config import BOT_TOKEN, WEB_APP_HOST, WEB_APP_PORT, WEB_APP_URL
from src.app.database.database import init_db
from src.app.handlers import callbacks, start, weather
from src.app.utils.logger import setup_logging
from src.app.webapp.server import start_webapp_server


async def set_bot_commands(bot: Bot):
    commands_default = [
        BotCommand(command="app", description="📱 Open Weather Mini App"),
        BotCommand(command="weather", description="🌤 Today's weather (or /weather <city>)"),
        BotCommand(command="pogoda", description="🌤 Weather for today (/pogoda <city>)"),
        BotCommand(command="city", description="📍 View or change saved location"),
        BotCommand(command="start", description="🚀 Main menu and day selection"),
        BotCommand(command="lang", description="🌐 Change language / Сменить язык"),
        BotCommand(command="help", description="📖 Help and command list"),
    ]
    commands_ru = [
        BotCommand(command="app", description="📱 Открыть Mini App погоды"),
        BotCommand(command="pogoda", description="🌤 Погода на сегодня (или /pogoda <город>)"),
        BotCommand(command="weather", description="🌤 Погода на сегодня (/weather <город>)"),
        BotCommand(command="city", description="📍 Текущий город или сменить город"),
        BotCommand(command="start", description="🚀 Главное меню и выбор дня"),
        BotCommand(command="lang", description="🌐 Сменить язык (RU / EN)"),
        BotCommand(command="help", description="📖 Справка по командам"),
    ]
    commands_en = [
        BotCommand(command="app", description="📱 Open Weather Mini App"),
        BotCommand(command="weather", description="🌤 Today's weather (or /weather <city>)"),
        BotCommand(command="pogoda", description="🌤 Today's weather (/pogoda <city>)"),
        BotCommand(command="city", description="📍 View or change saved location"),
        BotCommand(command="start", description="🚀 Main menu and day selection"),
        BotCommand(command="lang", description="🌐 Change language (RU / EN)"),
        BotCommand(command="help", description="📖 Bot commands help"),
    ]
    try:
        await bot.set_my_commands(commands_default, scope=BotCommandScopeDefault())
        await bot.set_my_commands(commands_ru, scope=BotCommandScopeDefault(), language_code="ru")
        await bot.set_my_commands(commands_en, scope=BotCommandScopeDefault(), language_code="en")
        logging.info("Команды бота успешно установлены в Telegram.")
    except Exception as e:
        logging.warning(f"Не удалось установить команды бота в Telegram: {e}")

    if WEB_APP_URL and WEB_APP_URL.startswith("https://"):
        try:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="🌤 Погода",
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            )
            logging.info(f"Кнопка Menu Button для Web App настроена на {WEB_APP_URL}")
        except Exception as e:
            logging.warning(f"Не удалось настроить Menu Button: {e}")
    else:
        logging.info(
            f"Mini App запущен на {WEB_APP_URL}. "
            "Кнопка Menu Button в Telegram требует HTTPS "
            "(задайте WEB_APP_URL=https://... в .env для публичного доступа)."
        )


async def main():
    setup_logging()

    if not BOT_TOKEN:
        logging.error("BOT_TOKEN не задан в переменной окружения!")
        sys.exit(1)

    # Initialize database
    await init_db()

    # Start Mini App HTTP server
    runner, site = await start_webapp_server(host=WEB_APP_HOST, port=WEB_APP_PORT)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Include routers
    dp.include_router(weather.router)
    dp.include_router(start.router)
    dp.include_router(callbacks.router)

    # Register bot commands in Telegram UI
    await set_bot_commands(bot)

    logging.info("Бот запущен и ожидает сообщения...")

    # Drop pending updates and start polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        logging.info("Остановка сервера Mini App...")
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
