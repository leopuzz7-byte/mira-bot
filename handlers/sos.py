from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import SOS
from keyboards import sos_emotion_kb, sos_grounding_kb, sos_physical_kb, main_menu_kb

router = Router()

EMOTION_LABELS = {
    "sos_shame": "стыд и вина",
    "sos_anger": "злость на себя",
    "sos_numb":  "просто плохо — сложно объяснить",
}


async def start_sos(target, state: FSMContext):
    await state.set_state(SOS.choose_emotion)
    text = (
        "Я здесь. Дыши 🌬️\n\n"
        "То, что случилось — уже случилось.\n"
        "Это не делает тебя плохим человеком.\n"
        "Прямо сейчас ты в безопасности.\n\n"
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
    await state.update_data(sos_emotion=label)
    await cb.message.edit_reply_markup()
    await state.set_state(SOS.grounding)
    await cb.message.answer(
        f"Понимаю тебя. {label.capitalize()} в такие моменты — это очень тяжело.\n\n"
        "Прежде чем говорить — давай на 30 секунд просто побудем здесь. 🌬️\n\n"
        "Найди 3 вещи, которые видишь прямо сейчас.\n"
        "Назови их про себя. Медленно.\n\n"
        "...\n\n"
        "Как ты сейчас?",
        reply_markup=sos_grounding_kb(),
    )


@router.callback_query(
    F.data.in_({"sos_ground_better", "sos_ground_still"}),
    SOS.grounding,
)
async def sos_after_grounding(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    data = await state.get_data()
    opening = (
        "Хорошо, что немного полегче. Я здесь.\n\n"
        "Можешь рассказать, что происходило сегодня до этого?"
        if cb.data == "sos_ground_better"
        else
        "Ничего. Я рядом, никуда не тороплюсь.\n\n"
        "Хочешь рассказать, что случилось сегодня?"
    )
    from handlers.chat import start_chat
    await start_chat(cb, state, mode="sos", opening_text=opening)


@router.callback_query(F.data == "sos_physical", SOS.choose_emotion)
async def sos_physical(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    await cb.message.answer(
        "Это физический дискомфорт от еды — или что-то более серьёзное?",
        reply_markup=sos_physical_kb(),
    )


@router.callback_query(F.data == "sos_phys_minor")
async def sos_phys_minor(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    from handlers.chat import start_chat
    await start_chat(cb, state, mode="sos",
                     opening_text="Понятно, это неприятно, но пройдёт.\nХочешь поговорить о том, как ты сейчас?")


@router.callback_query(F.data == "sos_phys_serious")
async def sos_phys_serious(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_reply_markup()
    await cb.message.answer(
        "Если тебе физически плохо — пожалуйста, обратись за медицинской помощью "
        "или позвони близким. Это важнее нашего разговора.\n\n"
        "Когда всё будет в порядке — я здесь.",
        reply_markup=main_menu_kb(),
    )
