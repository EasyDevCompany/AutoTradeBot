from aiogram import types


manager_buttons = ['Мои заказы💼', 'В работе🌋', 'Сформировать заказ📝', 'Написать отчет📊']
manager_buttons_2 = ['Осуществленные заказы', "Назад"]
driver_buttons = ['Все заказы👨‍💻', 'Собранные заказы💶']
financier_and_accounting_buttons = ['Просмотреть данные🗂', 'Обновить данные пользователей✅']
superuser = ['Сформировать заказ📝', 'Написать отчет📊', 'Просмотреть данные🗂', 'Обновить данные пользователей✅',
             'Все заказы👨‍💻',
             'Мои заказы💼', 'В работе🌋', 'Собранные заказы💶']


manager_keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True)
manager_keyboards_2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
driver_keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True)
financier_and_accounting_keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True)
superuser_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

manager_keyboards.add(*manager_buttons)
manager_keyboards_2.add(*manager_buttons_2)
driver_keyboards.add(*driver_buttons)
financier_and_accounting_keyboards.add(*financier_and_accounting_buttons)
superuser_keyboard.add(*superuser)