from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hbold

from dependency_injector.wiring import Provide, inject

from app.services.telegram_user import TelegramUserService
from app.services.validators import ValidateInformationService

from app.core.containers import Container

from app.utils.states.start_handler import StartState
from app.utils.keyboards.start import (
    superuser_keyboard,
    manager_keyboards,
    financier_and_accounting_keyboards,
    driver_keyboards
)
from app.models.telegram_user import TelegramUser


@inject
async def get_phone_number(message: types.Message):
    await message.answer("📱Отправьте номер телефона для авторизации: ")
    await StartState.phone_number.set()


@inject
async def start_command(
        message: types.Message,
        state: FSMContext,
        telegram_user_service: TelegramUserService = Provide[Container.service_telegram_user],
        validate_service: ValidateInformationService = Provide[Container.validate_service],
):
    phone = message.text
    correct_phone_number = await validate_service.validate_phone_number(phone_number=phone)

    if len(correct_phone_number) > 12:
        await message.answer(f"⛔️Не правильный номер телефона, проверьте его написанрие: {correct_phone_number}")

    else:
        tg_user_dict = {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
        }
        print(correct_phone_number)
        message_out = await telegram_user_service.registration_user(
            obj_in=tg_user_dict,
            phone_number=correct_phone_number
        )

        if message_out:
            user_perm_status = await telegram_user_service.get_user_permission_status(user_id=message.from_user.id)
            if user_perm_status == TelegramUser.PermissionStatus.super_user:
                await message.answer(f"{hbold('Вы успешно авторизовались в системе✅')}\n\n"
                                     f"Добро пожаловать, {hbold(message.from_user.first_name)}!\n"
                                     f"Перед вами меню:", reply_markup=superuser_keyboard)
            elif user_perm_status == TelegramUser.PermissionStatus.driver:
                await message.answer(f"{hbold('Вы успешно авторизовались в системе✅')}\n\n"
                                     f"Добро пожаловать, {hbold(message.from_user.first_name)}!\n"
                                     f"Перед вами меню:", reply_markup=driver_keyboards)
            elif user_perm_status == TelegramUser.PermissionStatus.manager:
                await message.answer(f"{hbold('Вы успешно авторизовались в системе✅')}\n\n"
                                     f"Добро пожаловать, {hbold(message.from_user.first_name)}!\n"
                                     f"Перед вами меню:", reply_markup=manager_keyboards)
            elif user_perm_status == TelegramUser.PermissionStatus.financier:
                await message.answer(f"{hbold('Вы успешно авторизовались в системе✅')}\n\n"
                                     f"Добро пожаловать, {hbold(message.from_user.first_name)}!\n"
                                     f"Перед вами меню:", reply_markup=financier_and_accounting_keyboards)
            await state.finish()
        else:
            await message.answer("⛔️Такого номера нет в базе данных! Проверьте корректность его написания.")


def register_start_handler(dp: Dispatcher):
    dp.register_message_handler(get_phone_number, commands=["start"])
    dp.register_message_handler(start_command, state=StartState.phone_number)