from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    about         = State()   # нажал "расскажи о себе"
    breathing     = State()   # выбрал боль
    explanation   = State()   # нажал "как ты поможешь"
    ready         = State()   # нажал "давай попробуем"


class Diary(StatesGroup):
    before_emotion = State()  # как чувствовала ДО
    after_emotion  = State()  # как чувствовала ПОСЛЕ
    context        = State()  # что сейчас в жизни


class Chat(StatesGroup):
    active = State()          # свободный ИИ-чат


class SOS(StatesGroup):
    choose_emotion = State()  # выбор эмоции после срыва
    talking        = State()  # ИИ-разговор в SOS-контексте


class Menu(StatesGroup):
    help_choice = State()     # уточнение "Помоги мне!"
