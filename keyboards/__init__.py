from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="📝 Мой дневник"),
            KeyboardButton(text="🆘 Мне сейчас плохо"),
            KeyboardButton(text="💬 Просто поговорим"),
        ]],
        resize_keyboard=True,
        persistent=True,
    )


# ─── Онбординг ────────────────────────────────────────────────────────────────

def onboarding_start_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Расскажи, как ты можешь помочь", callback_data="ob_about")
    return b.as_markup()

def onboarding_reason_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Да, я уже устала — мне нужна помощь", callback_data="ob_reason_tired")
    b.button(text="Я переела недавно, чувствую вину",     callback_data="ob_reason_guilt")
    b.button(text="Просто интересно, кто такая Мира :)",  callback_data="ob_reason_curious")
    b.adjust(1)
    return b.as_markup()

def onboarding_try_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Давай, я готова", callback_data="ob_try")
    return b.as_markup()


# ─── Дневник ─────────────────────────────────────────────────────────────────

def diary_before_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Было грустно",               callback_data="d_before_sad")
    b.button(text="Переживала, боялась",         callback_data="d_before_anxious")
    b.button(text="Злилась или обижалась",       callback_data="d_before_angry")
    b.button(text="Винила себя за что-то",       callback_data="d_before_guilt")
    b.button(text="Всё было хорошо",             callback_data="d_before_ok")
    b.button(text="✏️ Свой вариант",             callback_data="d_before_custom")
    b.adjust(1)
    return b.as_markup()

def diary_after_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Винила себя",                 callback_data="d_after_guilt")
    b.button(text="Злилась на себя",             callback_data="d_after_angry")
    b.button(text="Хорошо поела — сыта и довольна", callback_data="d_after_ok")
    b.button(text="✏️ Свой вариант",             callback_data="d_after_custom")
    b.adjust(1)
    return b.as_markup()

def diary_context_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Да, есть кое-что",  callback_data="d_ctx_yes")
    b.button(text="Нет, всё спокойно", callback_data="d_ctx_no")
    b.adjust(2)
    return b.as_markup()

def diary_after_save_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Да, давай поговорим",         callback_data="d_want_chat")
    b.button(text="Пока не готова, спасибо",     callback_data="d_done")
    b.button(text="Просто сохрани запись",        callback_data="d_done")
    b.adjust(1)
    return b.as_markup()


# ─── SOS ─────────────────────────────────────────────────────────────────────

def sos_emotion_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Стыд и вину",                     callback_data="sos_shame")
    b.button(text="Злость на себя",                  callback_data="sos_anger")
    b.button(text="Просто плохо, не могу объяснить", callback_data="sos_numb")
    b.button(text="Физически плохо",                 callback_data="sos_physical")
    b.adjust(1)
    return b.as_markup()

def sos_grounding_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Немного лучше",    callback_data="sos_ground_better")
    b.button(text="Всё ещё тяжело",   callback_data="sos_ground_still")
    b.adjust(2)
    return b.as_markup()

def sos_physical_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Просто дискомфорт от еды", callback_data="sos_phys_minor")
    b.button(text="Что-то серьёзное",         callback_data="sos_phys_serious")
    b.adjust(1)
    return b.as_markup()


# ─── Меню "Мне сейчас плохо" ─────────────────────────────────────────────────

def help_choice_kb():
    b = InlineKeyboardBuilder()
    b.button(text="Я переела — помоги",       callback_data="help_sos")
    b.button(text="Хочу поговорить с Мирой",  callback_data="help_chat")
    b.adjust(1)
    return b.as_markup()


# ─── Напоминания ──────────────────────────────────────────────────────────────

def remind_kb_simple():
    b = InlineKeyboardBuilder()
    b.button(text="Записать момент",  callback_data="remind_diary")
    b.button(text="Поговорим",        callback_data="remind_chat")
    b.button(text="Всё хорошо",       callback_data="remind_ok")
    b.adjust(2, 1)
    return b.as_markup()

def remind_kb_sos():
    b = InlineKeyboardBuilder()
    b.button(text="Мне сейчас плохо",  callback_data="remind_sos")
    b.button(text="Записать момент",   callback_data="remind_diary")
    b.button(text="Всё хорошо",        callback_data="remind_ok")
    b.adjust(1, 2)
    return b.as_markup()

def remind_kb_check():
    b = InlineKeyboardBuilder()
    b.button(text="Хорошо",            callback_data="remind_ok")
    b.button(text="Тяжеловато",        callback_data="remind_sos")
    b.button(text="Расскажу",          callback_data="remind_chat")
    b.adjust(2, 1)
    return b.as_markup()

def remind_kb_diary():
    b = InlineKeyboardBuilder()
    b.button(text="Записать",     callback_data="remind_diary")
    b.button(text="Не сейчас",    callback_data="remind_ok")
    b.adjust(2)
    return b.as_markup()


# ─── Общие ───────────────────────────────────────────────────────────────────

def stop_chat_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Завершить разговор")]],
        resize_keyboard=True,
    )
