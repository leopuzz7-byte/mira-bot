from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    about       = State()
    breathing   = State()
    explanation = State()
    ready       = State()


class Diary(StatesGroup):
    before_emotion = State()
    before_custom  = State()   # свой вариант ДО
    after_emotion  = State()
    after_custom   = State()   # свой вариант ПОСЛЕ
    context        = State()


class Chat(StatesGroup):
    active = State()


class SOS(StatesGroup):
    choose_emotion = State()
    grounding      = State()   # упражнение заземления
    talking        = State()


class Menu(StatesGroup):
    help_choice = State()
