from aiogram import types
from .base import cancel_button, back_button

public_button = types.InlineKeyboardButton(callback_data='public', text="Опубликовать заказ✅")
add_image = types.InlineKeyboardButton(callback_data="add_image", text="Добавить еще скрин➕")

public_keyboard = types.InlineKeyboardMarkup().add(add_image).add(public_button).add(back_button).add(cancel_button)