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
from reminders import setup_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start",  description="Начать / вернуться в меню"),
        BotCommand(command="diary",  description="Мой дневник"),
        BotCommand(command="sos",    description="Мне сейчас плохо"),
        BotCommand(command="chat",   description="Поговорить с Мирой"),
        BotCommand(command="help",   description="Что умеет бот"),
    ])


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN не задан")

    await init_db()
    ai_provider = get_provider()
    logger.info("AI: %s / %s", os.getenv("AI_PROVIDER"), os.getenv("AI_MODEL"))

    bot = Bot(token=token)
    dp  = Dispatcher(storage=MemoryStorage())
    dp["ai"] = ai_provider

    for r in all_routers:
        dp.include_router(r)

    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("Scheduler запущен — напоминания каждые 2 дня")

    await set_commands(bot)
    logger.info("Бот запущен ✅")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
