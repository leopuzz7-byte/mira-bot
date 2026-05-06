"""
SOS — режим помощи при срыве.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import SOS, Chat
from keyboards import sos_emotion_kb, sos_physical_kb, main_menu_kb
from handlers.chat import start_chat

router = Router()

EMOTION_LABELS = {
    "sos_shame":    "Стыд и вина",
    "sos_anger":    "Злость на себя",
    "sos_numb":     "Просто плохо — не могу объяснить",
}


async def start_sos(target, state: FSMContext):
    """Запускает SOS-режим. target — Message или CallbackQuery."""
    await state.set_state(SOS.choose_emotion)
    text = (
        "Я здесь. Дыши.\n\n"
        "То, что случилось — уже случилось, и это не делает тебя плохим человеком.\n\n"
        "Что сейчас чувствуешь больше всего?"
    )
    if isinstance(target, Message):
        await target.answer(text, reply_markup=sos_emotion_kb())
    else:
        await target.message.answer(text, reply_markup=sos_emotion_kb())


@router.callback_query(
    F.data.in_({"sos_shame", "sos_anger", "sos_numb"}),
    SOS.choose_emotion,
)
async def sos_emotion(cb: CallbackQuery, state: FSMContext):
    label = EMOTION_LABELS[cb.data]
    await cb.message.edit_reply_markup()
    await state.update_data(sos_emotion=label)

    opening = (
        f"Понимаю тебя. {label.lower().capitalize()} в такие моменты — это очень тяжело.\n\n"
        "Можешь рассказать, что происходило сегодня до этого? "
        "Иногда переедание — просто ответ на что-то, что накопилось."
    )
    await start_chat(cb, state, mode="sos", opening_text=opening)


@router.callback_query(F.data == "sos_physical", SOS.choose_emotion)
async def sos_physical(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    await cb.message.answer(
        "Это физический дискомфорт от еды — или что-то более серьёзное?",
        reply_markup=sos_physical_kb(),
    )


@router.callback_query(F.data == "sos_phys_minor", SOS.choose_emotion)
async def sos_phys_minor(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    opening = (
        "Понятно, это неприятно, но пройдёт.\n\n"
        "Хочешь поговорить о том, как ты себя сейчас чувствуешь?"
    )
    await start_chat(cb, state, mode="sos", opening_text=opening)


@router.callback_query(F.data == "sos_phys_serious", SOS.choose_emotion)
async def sos_phys_serious(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_reply_markup()
    await cb.message.answer(
        "Если тебе физически плохо — пожалуйста, обратись за медицинской помощью "
        "или позвони близким. Это важнее нашего разговора.\n\n"
        "Когда всё будет в порядке — я здесь.",
        reply_markup=main_menu_kb(),
    )
