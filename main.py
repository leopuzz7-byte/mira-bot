"""
Точка входа — запуск бота.
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from database import init_db
from ai_provider import get_provider
from handlers import all_routers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start",  description="Начать / вернуться в меню"),
        BotCommand(command="diary",  description="Внести запись в дневник"),
        BotCommand(command="chat",   description="Поговорить с Мирой"),
        BotCommand(command="sos",    description="Помощь прямо сейчас"),
        BotCommand(command="help",   description="Что умеет бот"),
    ]
    await bot.set_my_commands(commands)


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN не задан в .env")

    # Инициализация БД
    await init_db()
    logger.info("База данных инициализирована")

    # AI провайдер — передаём как middleware-данные в хендлеры
    ai_provider = get_provider()
    logger.info(
        "AI провайдер: %s / модель: %s",
        os.getenv("AI_PROVIDER", "claude"),
        os.getenv("AI_MODEL", "—"),
    )

    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())

    # Передаём ai_provider во все хендлеры через workflow_data
    dp["ai"] = ai_provider

    # Подключаем все роутеры
    for r in all_routers:
        dp.include_router(r)

    await set_commands(bot)
    logger.info("Бот запущен. Ожидаем сообщений...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
