from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from states import Onboarding, Diary
from keyboards import onboarding_start_kb, onboarding_reason_kb, onboarding_try_kb, diary_before_kb
from database import upsert_user, is_onboarded, set_onboarded
from handlers.menu import send_main_menu

router = Router()

REASON_LABELS = {
    "ob_reason_tired":   "Устала, нужна помощь",
    "ob_reason_guilt":   "Чувство вины после еды",
    "ob_reason_curious": "Просто интересно",
}

STEP2_TEXT = (
    "Всё начинается с одного простого шага —\nпросто замечать.\n\n"
    "— Что ты чувствовала до того, как потянулась к еде?\n"
    "— Что было после?\n\n"
    '<a href="https://pubmed.ncbi.nlm.nih.gov/28918456/">Исследования показывают</a>: '
    "само это осознание снижает риск срыва почти вдвое. Без запретов и диет.\n\n"
    "Давай попробуем прямо сейчас — займёт 2 минуты 🩵"
)


@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    user = msg.from_user
    await upsert_user(user.id, user.username or "", user.first_name or "")

    if await is_onboarded(user.id):
        await send_main_menu(msg, returning=True)
        return

    await state.set_state(Onboarding.about)
    await msg.answer(
        "Привет 🌿\nЯ Мира — твоя помощница в питании.\n\n"
        "Я не про диеты и не про цифры на весах. Я про то, что происходит "
        "внутри, когда еда становится способом справиться с чем-то тяжёлым.\n\n"
        "Я понимаю, как ты устала от бесконечных попыток похудеть, подсчёта "
        "калорий, чувства вины. Устала ненавидеть своё отражение в зеркале.\n\n"
        "Со мной можно просто выдохнуть. Здесь безопасно 💛",
        reply_markup=onboarding_start_kb(),
    )


@router.callback_query(F.data == "ob_about", Onboarding.about)
async def ob_about(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    await state.set_state(Onboarding.breathing)
    await cb.message.answer(STEP2_TEXT, parse_mode="HTML", reply_markup=onboarding_reason_kb())


@router.callback_query(
    F.data.in_({"ob_reason_tired", "ob_reason_guilt", "ob_reason_curious"}),
    Onboarding.breathing,
)
async def ob_reason(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    await state.update_data(reason=REASON_LABELS.get(cb.data, ""))
    await state.set_state(Onboarding.ready)
    await cb.message.answer(
        "Хорошо. Прямо сейчас, чем бы ты ни чувствовала — предлагаю на секунду выдохнуть.\n\n"
        "Со мной ты в безопасности. Я никуда не передаю то, что ты пишешь.\n"
        "Начиная с этого момента — просто замечай, а я буду рядом 💛",
        reply_markup=onboarding_try_kb(),
    )


@router.callback_query(F.data == "ob_try", Onboarding.ready)
async def ob_try(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await set_onboarded(cb.from_user.id, data.get("reason", ""))
    await cb.message.edit_reply_markup()
    await state.set_state(Diary.before_emotion)
    await cb.message.answer(
        "Вспомни последний раз, когда ела.\nКак ты себя чувствовала до приёма пищи?",
        reply_markup=diary_before_kb(),
    )
