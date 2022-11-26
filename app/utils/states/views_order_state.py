from aiogram.dispatcher.filters.state import StatesGroup, State


class ViewOrderOrReportFilter(StatesGroup):
    type_of_view = State()
    type_date = State()
    date = State()
    date_start = State()
    date_end = State()
    managers = State()
    report_status = State()
    view_info = State()
