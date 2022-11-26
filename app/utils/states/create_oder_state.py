from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateOrder(StatesGroup):
    description = State()
    image = State()
    image_description = State()
    waite_next_answer = State()
