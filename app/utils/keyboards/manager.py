from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .base import cancel_button

image_button = InlineKeyboardButton(text="Скрин🏞", callback_data="image")
image_description_button = InlineKeyboardButton(text="Описание к срину📄", callback_data="image_description")


image_edit_keyboard = InlineKeyboardMarkup().add(image_button).add(image_description_button).add(cancel_button)

