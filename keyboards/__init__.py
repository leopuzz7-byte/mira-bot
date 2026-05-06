"""
Все клавиатуры бота в одном месте.
"""
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ─── Главное меню (постоянная клавиатура внизу) ───────────────────────────────

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Внести запись"),
                KeyboardButton(text="🆘 Помоги мне!"),
                KeyboardButton(text="💬 Поболтаем"),
            ]
        ],
        resize_keyboard=True,
        persistent=True,
    )


# ─── Онбординг ────────────────────────────────────────────────────────────────

def onboarding_start_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Привет! Расскажи подробнее о себе", callback_data="ob_about")
    return b.as_markup()


def onboarding_reason_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Да, я уже устала — мне нужна помощь", callback_data="ob_reason_tired")
    b.button(text="Я переела недавно, чувствую вину",     callback_data="ob_reason_guilt")
    b.button(text="Просто интересно, кто такая Мира :)",  callback_data="ob_reason_curious")
    b.adjust(1)
    return b.as_markup()


def onboarding_how_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Как ты можешь помочь?", callback_data="ob_how")
    return b.as_markup()


def onboarding_try_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Давай попробуем", callback_data="ob_try")
    return b.as_markup()


# ─── Дневник ─────────────────────────────────────────────────────────────────

def diary_before_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Было грустно",               callback_data="d_before_sad")
    b.button(text="Злилась или раздражалась",   callback_data="d_before_angry")
    b.button(text="Переживала, тревожилась",    callback_data="d_before_anxious")
    b.button(text="Винила себя за что-то",      callback_data="d_before_guilt")
    b.button(text="Всё хорошо — просто поела",  callback_data="d_before_ok")
    b.adjust(1)
    return b.as_markup()


def diary_after_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Недовольна собой, злюсь",        callback_data="d_after_bad")
    b.button(text="Хорошо поела — сыта и довольна", callback_data="d_after_ok")
    b.adjust(1)
    return b.as_markup()


def diary_context_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Да, есть кое-что",   callback_data="d_ctx_yes")
    b.button(text="Нет, всё спокойно",  callback_data="d_ctx_no")
    b.adjust(2)
    return b.as_markup()


def diary_after_save_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Хочу поговорить с Мирой", callback_data="d_want_chat")
    b.button(text="Пока достаточно, спасибо", callback_data="d_done")
    b.adjust(1)
    return b.as_markup()


# ─── SOS ─────────────────────────────────────────────────────────────────────

def sos_emotion_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Стыд и вину",                    callback_data="sos_shame")
    b.button(text="Злость на себя",                 callback_data="sos_anger")
    b.button(text="Просто плохо, не могу объяснить",callback_data="sos_numb")
    b.button(text="Физически плохо",                callback_data="sos_physical")
    b.adjust(1)
    return b.as_markup()


def sos_physical_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Просто дискомфорт от еды",  callback_data="sos_phys_minor")
    b.button(text="Что-то серьёзное",          callback_data="sos_phys_serious")
    b.adjust(1)
    return b.as_markup()


# ─── Меню "Помоги мне!" ───────────────────────────────────────────────────────

def help_choice_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Я переела — помоги",      callback_data="help_sos")
    b.button(text="Хочу поговорить с Мирой", callback_data="help_chat")
    b.adjust(1)
    return b.as_markup()


# ─── Общие ───────────────────────────────────────────────────────────────────

def back_to_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="← В главное меню", callback_data="go_menu")
    return b.as_markup()


def stop_chat_kb() -> ReplyKeyboardMarkup:
    """Кнопка завершения чата в reply-клавиатуре."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Завершить разговор")]],
        resize_keyboard=True,
    )
