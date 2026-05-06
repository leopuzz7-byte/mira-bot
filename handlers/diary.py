"""
Дневник состояния — записи до/после еды.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import Diary, Chat
from keyboards import (
    diary_before_kb, diary_after_kb,
    diary_context_kb, diary_after_save_kb, main_menu_kb,
)
from database import save_diary_entry

router = Router()

BEFORE_LABELS = {
    "d_before_sad":     "Было грустно",
    "d_before_angry":   "Злилась или раздражалась",
    "d_before_anxious": "Переживала, тревожилась",
    "d_before_guilt":   "Винила себя за что-то",
    "d_before_ok":      "Всё хорошо — просто поела",
}
AFTER_LABELS = {
    "d_after_bad": "Недовольна собой, злюсь",
    "d_after_ok":  "Хорошо поела — сыта и довольна",
}


# ─── Запуск дневника из главного меню ────────────────────────────────────────

async def start_diary(target, state: FSMContext):
    """Запускает дневник. target — Message или CallbackQuery."""
    await state.set_state(Diary.before_emotion)
    text = "Расскажи, как был последний приём пищи.\nКак ты себя чувствовала до?"
    if isinstance(target, Message):
        await target.answer(text, reply_markup=diary_before_kb())
    else:
        await target.message.answer(text, reply_markup=diary_before_kb())


# ─── Шаг 1 — эмоция ДО ───────────────────────────────────────────────────────

@router.callback_query(
    F.data.in_(set(BEFORE_LABELS.keys())),
    Diary.before_emotion,
)
async def diary_before(cb: CallbackQuery, state: FSMContext):
    label = BEFORE_LABELS[cb.data]
    await state.update_data(before_emotion=label)
    await cb.message.edit_reply_markup()
    await state.set_state(Diary.after_emotion)
    await cb.message.answer("А после еды?", reply_markup=diary_after_kb())


# ─── Шаг 2 — эмоция ПОСЛЕ ────────────────────────────────────────────────────

@router.callback_query(
    F.data.in_(set(AFTER_LABELS.keys())),
    Diary.after_emotion,
)
async def diary_after(cb: CallbackQuery, state: FSMContext):
    label = AFTER_LABELS[cb.data]
    await state.update_data(after_emotion=label)
    await cb.message.edit_reply_markup()
    await state.set_state(Diary.context)
    await cb.message.answer(
        "И последний вопрос — что сейчас происходит в жизни в целом?\n"
        "Есть что-то, что давит или беспокоит?",
        reply_markup=diary_context_kb(),
    )


# ─── Шаг 3 — контекст жизни ──────────────────────────────────────────────────

@router.callback_query(F.data.in_({"d_ctx_yes", "d_ctx_no"}), Diary.context)
async def diary_context(cb: CallbackQuery, state: FSMContext):
    ctx = "Да, есть кое-что" if cb.data == "d_ctx_yes" else "Нет, всё спокойно"
    await state.update_data(life_context=ctx)
    data = await state.get_data()

    await save_diary_entry(
        user_id=cb.from_user.id,
        before_emotion=data["before_emotion"],
        after_emotion=data["after_emotion"],
        life_context=ctx,
    )

    await cb.message.edit_reply_markup()

    # Ветка — если всё было хорошо
    if data["before_emotion"] == "Всё хорошо — просто поела" \
            and data["after_emotion"] == "Хорошо поела — сыта и довольна":
        await state.clear()
        await cb.message.answer(
            "Как здорово, что этот приём пищи прошёл спокойно! "
            "Это уже кое-что значит.\n\n"
            "Если вдруг в следующий раз станет по-другому — напиши мне. "
            "Я всегда здесь.",
            reply_markup=main_menu_kb(),
        )
        return

    # Ветка — было тяжело
    await cb.message.answer(
        "Ты только что сделала кое-что важное — заметила, что происходило внутри.\n\n"
        "Само осознание триггера снижает риск следующего срыва. "
        "Просто замечай — пока это всё, что нужно.\n\n"
        "Запись сохранена. Хочешь поговорить об этом подробнее?",
        reply_markup=diary_after_save_kb(),
    )


# ─── После сохранения — выбор пользователя ───────────────────────────────────

@router.callback_query(F.data == "d_want_chat")
async def diary_want_chat(cb: CallbackQuery, state: FSMContext):
    from handlers.chat import start_chat
    await cb.message.edit_reply_markup()
    await start_chat(cb, state, mode="chat")


@router.callback_query(F.data == "d_done")
async def diary_done(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_reply_markup()
    await cb.message.answer(
        "Хорошо, я здесь. Пиши, когда захочешь.",
        reply_markup=main_menu_kb(),
    )
