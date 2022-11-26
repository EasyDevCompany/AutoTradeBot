from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .base import cancel_button

report_button = InlineKeyboardButton(text="Отчеты📊", callback_data="report")
order_button = InlineKeyboardButton(text="Заказы📦", callback_data="order")

date_today = InlineKeyboardButton(text="Сегодня", callback_data=f"{datetime.now().date()}")
date_yesterday = InlineKeyboardButton(text="Вчера", callback_data=f"{datetime.now().date() - timedelta(days=1)}")
other_date = InlineKeyboardButton(text="Другая дата", callback_data=f"other_date")
back_button_report = InlineKeyboardButton(text="Вернуться к предыдущему пункту↪️", callback_data="back")

report_status_active = InlineKeyboardButton(text="Активные🔔", callback_data="active")
report_status_non_active = InlineKeyboardButton(text="Завершенные🔕", callback_data="non_active")

views_keyboard = InlineKeyboardMarkup().add(report_button, order_button).add(cancel_button)
report_status_keyboard = InlineKeyboardMarkup().add(
    report_status_active,
    report_status_non_active
).add(cancel_button)
date_keyboard = InlineKeyboardMarkup().add(date_today, date_yesterday).add(other_date)

