from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import main_menu_kb
from database import get_weekly_stats, format_stats_text

router = Router()


async def send_stats(target, state: FSMContext = None):
    user_id = target.from_user.id
    if state:
        await state.clear()
    stats = await get_weekly_stats(user_id)
    text  = format_stats_text(stats)
    if isinstance(target, Message):
        await target.answer(text, reply_markup=main_menu_kb())
    else:
        await target.message.answer(text, reply_markup=main_menu_kb())


@router.message(F.text == "📊 Моя статистика")
async def menu_stats(msg: Message, state: FSMContext):
    await send_stats(msg, state)
