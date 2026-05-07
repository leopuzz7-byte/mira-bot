"""
ИИ-чат с Мирой — свободный разговор.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import Chat
from keyboards import main_menu_kb, stop_chat_kb
from database import get_last_entries
from utils.ai_chat import get_ai_response, format_diary_context

router = Router()


async def start_chat(
    target,
    state: FSMContext,
    mode: str = "chat",
    opening_text: str | None = None,
):
    """
    Запускает ИИ-чат. target — Message или CallbackQuery.
    mode: "chat" | "sos" | "casual"
    """
    await state.set_state(Chat.active)
    await state.update_data(chat_mode=mode, history=[])

    text = opening_text or "Я здесь. Что хотела бы обсудить?"
    if isinstance(target, Message):
        await target.answer(text, reply_markup=stop_chat_kb())
    else:
        await target.message.answer(text, reply_markup=stop_chat_kb())


# ─── Выход из чата ────────────────────────────────────────────────────────────

@router.message(F.text == "Завершить разговор", Chat.active)
async def stop_chat(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Рада, что поговорили. Если что-то навалится, пиши, я здесь.",
        reply_markup=main_menu_kb(),
    )


# ─── Основной обработчик сообщений в чате ────────────────────────────────────

@router.message(Chat.active)
async def chat_message(msg: Message, state: FSMContext, ai):
    data = await state.get_data()
    history: list = data.get("history", [])
    mode: str = data.get("chat_mode", "chat")

    # Добавляем сообщение пользователя в историю
    history.append({"role": "user", "content": msg.text or ""})

    # Контекст из дневника (последние 3 записи)
    entries = await get_last_entries(msg.from_user.id, limit=3)
    diary_ctx = format_diary_context(entries)

    # Показываем "печатает..."
    await msg.bot.send_chat_action(msg.chat.id, "typing")

    try:
        reply = await get_ai_response(
            provider=ai,
            history=history,
            mode=mode,
            extra_context=diary_ctx,
        )
    except Exception as e:
        reply = "Что-то пошло не так с подключением. Попробуй ещё раз через минуту."

    # Сохраняем ответ в историю
    history.append({"role": "assistant", "content": reply})

    # Ограничиваем историю последними 20 сообщениями (10 парами)
    if len(history) > 20:
        history = history[-20:]

    await state.update_data(history=history)
    await msg.answer(reply)


# ─── Callback для перехода в чат из других мест ──────────────────────────────

@router.callback_query(F.data == "go_menu")
async def go_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_reply_markup()
    await cb.message.answer("Я здесь, пиши когда нужно.", reply_markup=main_menu_kb())
