"""
Напоминания раз в 2 дня, последовательно с 1 по 15, потом новый круг.
"""
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import get_all_onboarded_users, update_reminder_sent
from keyboards import remind_kb_simple, remind_kb_sos, remind_kb_check, remind_kb_diary

logger = logging.getLogger(__name__)

# 15 напоминаний — по порядку, потом снова с 1
REMINDERS = [
    {
        "text": "Привет 🌿 Просто зашла проверить — как ты сегодня?\nМожно одним словом или просто нажать кнопку.",
        "kb": "check",
    },
    {
        "text": "Привет 💛 Давно не виделись.\nКак прошли эти дни с едой — было что-то, что хочется отметить?",
        "kb": "simple",
    },
    {
        "text": "🌬️ Один вопрос на сегодня:\nБыло ли что-то, что ты съела не от голода?\nНикаких оценок — просто замечаем вместе.",
        "kb": "diary",
    },
    {
        "text": "Привет 🌿\nНе нужно ничего объяснять.\nПросто — ты как?",
        "kb": "check",
    },
    {
        "text": "Иногда самое важное — просто заметить.\nКак ты себя чувствуешь прямо сейчас? 💛",
        "kb": "check",
    },
    {
        "text": "Привет 🌿 Я здесь.\nЕсли последние дни были тяжёлыми — это нормально.\nХочешь рассказать или просто сохранить момент?",
        "kb": "simple",
    },
    {
        "text": "Один маленький вопрос 💛\nЧто ты чувствовала после последнего приёма пищи?\nМожем записать — займёт минуту.",
        "kb": "diary",
    },
    {
        "text": "Привет 🌬️\nПомнишь, зачем ты пришла сюда?\nЯ помню. И я здесь.",
        "kb": "simple",
    },
    {
        "text": "Как прошли эти дни? 🌿\nИногда важно просто остановиться и спросить себя об этом.",
        "kb": "sos",
    },
    {
        "text": "Привет 💛\nТы сегодня была добра к себе?\nНе нужно отвечать правильно — просто честно.",
        "kb": "check",
    },
    {
        "text": "🌿 Маленькое напоминание:\nТы не обязана есть идеально.\nТы просто замечаешь — и этого достаточно.\n\nКак ты сейчас?",
        "kb": "check",
    },
    {
        "text": "Привет 🌬️\nЕсли в эти дни было что-то тяжёлое —\nне нужно нести это одной.",
        "kb": "sos",
    },
    {
        "text": "Просто зашла сказать — я здесь 💛\nКак ты?",
        "kb": "check",
    },
    {
        "text": "🌿 Один вопрос:\nБыло ли в эти дни что-то, чем ты гордишься?\nДаже маленькое — считается.",
        "kb": "simple",
    },
    {
        "text": "Привет 💛\nИногда тяжёлые дни приходят без предупреждения.\nЕсли сейчас такой — я рядом.",
        "kb": "sos",
    },
]

KB_MAP = {
    "simple": remind_kb_simple,
    "sos":    remind_kb_sos,
    "check":  remind_kb_check,
    "diary":  remind_kb_diary,
}


async def send_reminders(bot: Bot):
    users = await get_all_onboarded_users()
    now = datetime.utcnow()

    for user in users:
        last = user.get("last_reminded_at")
        if last:
            last_dt = datetime.fromisoformat(last)
            if now - last_dt < timedelta(days=2):
                continue  # ещё не пора

        idx = (user.get("reminder_index") or 0) % 15
        reminder = REMINDERS[idx]
        kb_fn = KB_MAP.get(reminder["kb"], remind_kb_simple)

        try:
            await bot.send_message(
                chat_id=user["user_id"],
                text=reminder["text"],
                reply_markup=kb_fn(),
            )
            await update_reminder_sent(user["user_id"], (idx + 1) % 15)
        except Exception as e:
            logger.warning("Не удалось отправить напоминание %s: %s", user["user_id"], e)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    # Проверяем каждый час — отправляем тем, у кого прошло 2 дня
    scheduler.add_job(send_reminders, "interval", hours=1, args=[bot])
    return scheduler
