from loguru import logger
from dependency_injector.wiring import Provide, inject

from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher

from app.models.telegram_user import TelegramUser

from app.utils.states.report_state import ReportState
from app.utils.keyboards import base

from app.services.report import ReportService
from app.services.telegram_user import TelegramUserService

from app.core.containers import Container


@inject
async def start_create_report(
        message: types.Message,
        service_telegram_user: TelegramUserService = Provide[Container.service_telegram_user],
):
    user_id = message.from_user.id

    if not await service_telegram_user.check_permission_status(
            user_id=user_id,
            permission_statuses=(
                    TelegramUser.PermissionStatus.super_user,
                    TelegramUser.PermissionStatus.manager,
            )
    ):
        return await message.answer("У вас недостаточно прав для совершения этих действий.")

    await message.answer(
        "📄Напишите боту отчет: ",
        reply_markup=base.cancel_keyboard
    )

    await ReportState.report.set()


@inject
async def get_and_save_report(
        message: types.Message,
        state: FSMContext,
        report_service: ReportService = Provide[Container.report_service]
):

    user_id = message.from_user.id
    await report_service.create_report(
        user_id=user_id,
        report=message.text
    )

    await message.answer("Отчет успешно сохранен!✅")
    await state.finish()


def register_report_handler(dp: Dispatcher, *args, **kwargs):
    dp.register_message_handler(start_create_report, lambda message: message.text == 'Написать отчет📊')
    dp.register_message_handler(get_and_save_report, state=ReportState.report)
