from aiogram.dispatcher.filters.state import State, StatesGroup


class ReportState(StatesGroup):
    report = State()
