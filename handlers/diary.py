from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import Diary, Chat
from keyboards import (
    diary_before_kb, diary_after_kb,
    diary_context_kb, diary_after_save_kb, main_menu_kb,
)
from database import save_diary_entry, get_diary_count

router = Router()

BEFORE_LABELS = {
    "d_before_sad":     "Было грустно",
    "d_before_anxious": "Переживала, боялась",
    "d_before_angry":   "Злилась или обижалась",
    "d_before_guilt":   "Винила себя за что-то",
    "d_before_ok":      "Всё было хорошо",
}
AFTER_LABELS = {
    "d_after_guilt": "Винила себя",
    "d_after_angry": "Злилась на себя",
    "d_after_ok":    "Хорошо поела — сыта и довольна",
}


async def start_diary(target, state: FSMContext):
    await state.set_state(Diary.before_emotion)
    text = "Вспомни последний раз, когда ела.\nКак ты себя чувствовала до?"
    kb = diary_before_kb()
    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb)
    else:
        await target.message.answer(text, reply_markup=kb)


# ─── ДО: кнопки ──────────────────────────────────────────────────────────────

@router.callback_query(F.data.in_(set(BEFORE_LABELS)), Diary.before_emotion)
async def diary_before(cb: CallbackQuery, state: FSMContext):
    await state.update_data(before_emotion=BEFORE_LABELS[cb.data])
    await cb.message.edit_reply_markup()
    await state.set_state(Diary.after_emotion)
    await cb.message.answer("Хорошо. А после еды — что осталось?", reply_markup=diary_after_kb())


# ─── ДО: свой вариант ────────────────────────────────────────────────────────

@router.callback_query(F.data == "d_before_custom", Diary.before_emotion)
async def diary_before_custom_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    await state.set_state(Diary.before_custom)
    await cb.message.answer("Напиши как хочешь — своими словами 🌿")


@router.message(Diary.before_custom)
async def diary_before_custom_text(msg: Message, state: FSMContext):
    await state.update_data(before_emotion=msg.text or "")
    await state.set_state(Diary.after_emotion)
    await msg.answer("Хорошо. А после еды — что осталось?", reply_markup=diary_after_kb())


# ─── ПОСЛЕ: кнопки ───────────────────────────────────────────────────────────

@router.callback_query(F.data.in_(set(AFTER_LABELS)), Diary.after_emotion)
async def diary_after(cb: CallbackQuery, state: FSMContext):
    await state.update_data(after_emotion=AFTER_LABELS[cb.data])
    await cb.message.edit_reply_markup()
    await _after_saved(cb, state)


# ─── ПОСЛЕ: свой вариант ─────────────────────────────────────────────────────

@router.callback_query(F.data == "d_after_custom", Diary.after_emotion)
async def diary_after_custom_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    await state.set_state(Diary.after_custom)
    await cb.message.answer("Напиши как хочешь 💛")


@router.message(Diary.after_custom)
async def diary_after_custom_text(msg: Message, state: FSMContext):
    await state.update_data(after_emotion=msg.text or "")
    await _after_saved(msg, state)


# ─── Третий вопрос и сохранение ──────────────────────────────────────────────

async def _after_saved(target, state: FSMContext):
    user_id = (
        target.from_user.id
        if isinstance(target, CallbackQuery)
        else target.from_user.id
    )
    count = await get_diary_count(user_id)

    if count >= 1:
        # Со второго визита показываем третий вопрос
        await state.set_state(Diary.context)
        text = "И последнее — что сейчас происходит в жизни в целом? Есть что-то, что давит?"
        kb = diary_context_kb()
        if isinstance(target, Message):
            await target.answer(text, reply_markup=kb)
        else:
            await target.message.answer(text, reply_markup=kb)
    else:
        await _save_and_respond(target, state, life_context="")


@router.callback_query(F.data.in_({"d_ctx_yes", "d_ctx_no"}), Diary.context)
async def diary_context_cb(cb: CallbackQuery, state: FSMContext):
    ctx = "Да, есть кое-что" if cb.data == "d_ctx_yes" else "Нет, всё спокойно"
    await state.update_data(life_context=ctx)
    await cb.message.edit_reply_markup()
    await _save_and_respond(cb, state, life_context=ctx)


async def _save_and_respond(target, state: FSMContext, life_context: str):
    user_id = target.from_user.id
    data = await state.get_data()

    before = data.get("before_emotion", "")
    after  = data.get("after_emotion", "")

    await save_diary_entry(user_id, before, after, life_context)

    send = (
        target.message.answer
        if isinstance(target, CallbackQuery)
        else target.answer
    )

    all_ok = before == "Всё было хорошо" and after == "Хорошо поела — сыта и довольна"

    if all_ok:
        await state.clear()
        await send(
            "Хороший приём пищи — это тоже важно замечать. Запомним этот момент 🌿",
            reply_markup=main_menu_kb(),
        )
    else:
        await send(
            "Ты заметила — это уже кое-что важное.\n\n"
            "Со временем такие кусочки складываются в картину,\n"
            "и ты сможешь понять, что на самом деле происходит с тобой.\n"
            "Я здесь, чтобы помочь тебе с этим 💛\n\n"
            "Хочешь обсудить это со мной?",
            reply_markup=diary_after_save_kb(),
        )


@router.callback_query(F.data == "d_want_chat")
async def diary_want_chat(cb: CallbackQuery, state: FSMContext):
    from handlers.chat import start_chat
    await cb.message.edit_reply_markup()
    await start_chat(cb, state, mode="chat")


@router.callback_query(F.data == "d_done")
async def diary_done(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_reply_markup()
    await cb.message.answer("Хорошо, я здесь. Пиши, когда захочешь.", reply_markup=main_menu_kb())
