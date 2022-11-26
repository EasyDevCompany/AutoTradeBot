from aiogram.dispatcher.filters.state import State, StatesGroup


class EditImages(StatesGroup):
    edit_answer = State()
    image = State()
    image_description = State()


class EditOrder(StatesGroup):
    description = State()