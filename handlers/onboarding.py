"""
Онбординг — первый запуск бота.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from states import Onboarding, Diary
from keyboards import (
    onboarding_start_kb, onboarding_reason_kb,
    onboarding_how_kb, onboarding_try_kb, diary_before_kb,
)
from database import upsert_user, is_onboarded, set_onboarded
from handlers.menu import send_main_menu

router = Router()

REASON_LABELS = {
    "ob_reason_tired":   "Устала, нужна помощь",
    "ob_reason_guilt":   "Чувство вины после еды",
    "ob_reason_curious": "Просто интересно",
}


@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    user = msg.from_user
    await upsert_user(user.id, user.username or "", user.first_name or "")

    # Если уже прошёл онбординг — показываем повторное меню
    if await is_onboarded(user.id):
        await send_main_menu(msg, returning=True)
        return

    # Первый раз — онбординг
    await state.set_state(Onboarding.about)
    await msg.answer(
        "Привет! Я — Мира, твоя помощница по питанию.\n\n"
        "Никаких диет, запретов и марафонов — и ничего из того, "
        "от чего ты, скорее всего, уже устала. "
        "Просто поддержка и пространство, где можно выдохнуть.",
        reply_markup=onboarding_start_kb(),
    )


@router.callback_query(F.data == "ob_about", Onboarding.about)
async def ob_about(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    await state.set_state(Onboarding.breathing)
    await cb.message.answer(
        "Мы с тобой встретились не случайно.\n\n"
        "Может, ты устала от диет и подсчёта калорий. "
        "Или от того, что срываешься, а потом чувствуешь вину. "
        "Или просто надоело быть недовольной собой.\n\n"
        "Здесь всё по-другому. Я не буду тебя оценивать.",
        reply_markup=onboarding_reason_kb(),
    )


@router.callback_query(
    F.data.in_({"ob_reason_tired", "ob_reason_guilt", "ob_reason_curious"}),
    Onboarding.breathing,
)
async def ob_reason(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    await state.update_data(reason=REASON_LABELS.get(cb.data, ""))
    await state.set_state(Onboarding.explanation)
    await cb.message.answer(
        "Хорошо. Чем бы ты сейчас ни чувствовала — предлагаю на секунду выдохнуть.\n\n"
        "Со мной ты в безопасности. Я никуда не передаю то, что ты мне напишешь.\n"
        "Начиная с этого момента, ты можешь просто замечать — а я буду рядом.",
        reply_markup=onboarding_how_kb(),
    )


@router.callback_query(F.data == "ob_how", Onboarding.explanation)
async def ob_how(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup()
    await state.set_state(Onboarding.ready)
    await cb.message.answer(
        "Всё просто. Исследования показывают: люди чаще переедают не от голода, "
        "а от эмоций — тревоги, скуки, усталости, обиды.\n\n"
        "Поэтому работать нужно не с едой, а с состоянием. "
        "Замечать, что происходит внутри — до и после приёма пищи. "
        "Это и есть первый шаг.\n\nДавай попробуем прямо сейчас?",
        reply_markup=onboarding_try_kb(),
    )


@router.callback_query(F.data == "ob_try", Onboarding.ready)
async def ob_try(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    reason = data.get("reason", "")
    await set_onboarded(cb.from_user.id, reason)
    await cb.message.edit_reply_markup()
    await state.set_state(Diary.before_emotion)
    await cb.message.answer(
        "Вспомни свой последний приём пищи. Как ты себя чувствовала до него?",
        reply_markup=diary_before_kb(),
    )
