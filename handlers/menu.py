"""
Главное меню и общие команды.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from states import Menu
from keyboards import main_menu_kb, help_choice_kb

router = Router()


async def send_main_menu(target, returning: bool = False):
    text = (
        "Привет! Как я могу помочь тебе сегодня?"
        if returning
        else "Я здесь. Пиши, когда нужно."
    )
    if isinstance(target, Message):
        await target.answer(text, reply_markup=main_menu_kb())
    else:
        await target.message.answer(text, reply_markup=main_menu_kb())


# ─── Кнопка "Внести запись" ───────────────────────────────────────────────────

@router.message(F.text == "📝 Внести запись")
async def menu_diary(msg: Message, state: FSMContext):
    await state.clear()
    from handlers.diary import start_diary
    await start_diary(msg, state)


# ─── Кнопка "Помоги мне!" ────────────────────────────────────────────────────

@router.message(F.text == "🆘 Помоги мне!")
async def menu_help(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Menu.help_choice)
    await msg.answer("Что происходит?", reply_markup=help_choice_kb())


@router.callback_query(F.data == "help_sos", Menu.help_choice)
async def help_sos(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_reply_markup()
    from handlers.sos import start_sos
    await start_sos(cb, state)


@router.callback_query(F.data == "help_chat", Menu.help_choice)
async def help_chat(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_reply_markup()
    from handlers.chat import start_chat
    await start_chat(cb, state, mode="chat")


# ─── Кнопка "Поболтаем" ───────────────────────────────────────────────────────

@router.message(F.text == "💬 Поболтаем")
async def menu_casual(msg: Message, state: FSMContext):
    await state.clear()
    from handlers.chat import start_chat
    await start_chat(msg, state, mode="casual", opening_text="Привет! Как ты сегодня?")


# ─── Команды ─────────────────────────────────────────────────────────────────

@router.message(Command("diary"))
async def cmd_diary(msg: Message, state: FSMContext):
    await state.clear()
    from handlers.diary import start_diary
    await start_diary(msg, state)


@router.message(Command("chat"))
async def cmd_chat(msg: Message, state: FSMContext):
    await state.clear()
    from handlers.chat import start_chat
    await start_chat(msg, state, mode="chat")


@router.message(Command("sos"))
async def cmd_sos(msg: Message, state: FSMContext):
    await state.clear()
    from handlers.sos import start_sos
    await start_sos(msg, state)


@router.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "Вот что я умею:\n\n"
        "📝 /diary — записать, как прошёл приём пищи\n"
        "🆘 /sos — помощь прямо сейчас, если тяжело\n"
        "💬 /chat — просто поговорить со мной\n"
        "🔄 /start — вернуться в начало\n\n"
        "Или используй кнопки внизу — они всегда там."
    )
