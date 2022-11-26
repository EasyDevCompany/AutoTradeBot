from aiogram import types

cancel_button = types.InlineKeyboardButton(callback_data="cancel", text="Отмена❌")
back_button = types.InlineKeyboardButton(callback_data="back", text="Вернуться к предыдущему пункту↪️")

cancel_and_back_keyboard = types.InlineKeyboardMarkup().add(back_button).add(cancel_button)
cancel_keyboard = types.InlineKeyboardMarkup().add(cancel_button)
back_keyboard = types.InlineKeyboardMarkup().add(back_button)