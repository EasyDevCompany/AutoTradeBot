from aiogram.dispatcher.filters.state import State, StatesGroup


class StartState(StatesGroup):
    phone_number = State()