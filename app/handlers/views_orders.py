import asyncio

from aioredis import Redis
from aiogram.utils.exceptions import RetryAfter
from dependency_injector.wiring import Provide, inject
from loguru import logger

from aiogram import types, Dispatcher
from aiogram.utils.markdown import hbold
from aiogram.dispatcher.storage import FSMContext

from app.core.containers import Container
from app.models.order import Order
from loader import bot

from app.models.telegram_user import TelegramUser

from app.services.order import OrderService
from app.services.images import ImagesService
from app.services.telegram_user import TelegramUserService
from app.services.report import ReportService
from app.services.validators import ValidateInformationService

from app.utils.keyboards.form_inline_keyboard import FormInlineKeyboardService
from app.utils.keyboards.callback_data import (
    calendar_callback,
    report_callback,
    view_managers_callback,
    watch_next_callback
)
from app.utils.keyboards.view_orders_keyboard import (
    views_keyboard,
    report_status_keyboard,
    date_keyboard
)
from app.utils.states.views_order_state import ViewOrderOrReportFilter


@inject
async def start_view_orders_or_report(
        message: types.Message,
        service_telegram_user: TelegramUserService = Provide[Container.service_telegram_user],
):
    user_id = message.from_user.id
    if not await service_telegram_user.check_permission_status(
            user_id=user_id,
            permission_statuses=(
                    TelegramUser.PermissionStatus.financier,
                    TelegramUser.PermissionStatus.super_user
            )
    ):
        return await message.answer("⛔️У вас нет прав для совершения этого действия")

    await message.answer("Выберите один пункт из меню нижe: ", reply_markup=views_keyboard)
    await ViewOrderOrReportFilter.type_of_view.set()


async def get_type_of_view(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup()
    callback_data = callback_query.data

    async with state.proxy() as data:
        data["view_type"] = callback_data
    await callback_query.message.answer(
        "Выберите промежуток за который хотите просмотреть заказы: ",
        reply_markup=date_keyboard
    )
    await ViewOrderOrReportFilter.type_date.set()


@inject
async def get_type_date(
        callback_query: types.CallbackQuery,
        state: FSMContext,
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service]
):
    await callback_query.message.edit_reply_markup()
    callback_data = callback_query.data

    if callback_data == "cancel":
        await callback_query.message.answer("Действие отменено")
        await state.finish()

    if callback_data == "other_date":
        await callback_query.message.answer(
            f"{hbold('🗓Выберите дату в календаре ниже: ')}\n\n"
            f"Для просмотра заказов/отчетов за один день"
            f"на втором календаре нажмите на ту же дату!",
            reply_markup=await keyboard_service.start_calendar()
        )
        return await ViewOrderOrReportFilter.date_start.set()

    async with state.proxy() as data:
        data["date"] = callback_data

    await callback_query.message.answer(
        "Выберите менеджеров: ",
        reply_markup=await keyboard_service.manager_keyboard()
    )
    await ViewOrderOrReportFilter.managers.set()


@inject
async def get_other_date(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service]
):
    selected, date = await keyboard_service.process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data["date_start"] = date
        await callback_query.message.answer(
            f"{hbold('🗓Выберите дату в календаре ниже: ')}\n\n"
            f"Для просмотра заказов/отчетов за один день"
            f"на втором календаре нажмите на ту же дату!",
            reply_markup=await keyboard_service.start_calendar()
        )
        await ViewOrderOrReportFilter.date_end.set()


@inject
async def save_end_date(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service],
        validate_service: ValidateInformationService = Provide[Container.validate_service]
):
    async with state.proxy() as data:
        start_date = data.get("date_start")
        selected, date = await keyboard_service.process_selection(callback_query, callback_data)
        if selected:
            logger.info(f"{start_date} {date}")
            data["date_end"] = date
            if await validate_service.validate_date(date_end=data["date_end"], date_start=start_date):
                await callback_query.message.answer(
                    "Выберите менеджеров: ",
                    reply_markup=await keyboard_service.manager_keyboard()
                )
                await ViewOrderOrReportFilter.managers.set()
            else:
                await callback_query.message.answer("Ваша начальная дата не должа быть меньше конечной даты,"
                                                    "повторите ввод даты: ",
                                                    reply_markup=await keyboard_service.start_calendar()
                                                    )


@inject
async def save_managers_and_send_answer(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        redis: Redis = Provide[Container.redis],
        order_service: OrderService = Provide[Container.order_service],
        image_service: ImagesService = Provide[Container.images_service],
        service_telegram_user: TelegramUserService = Provide[Container.service_telegram_user],
        validate_service: ValidateInformationService = Provide[Container.validate_service]

):
    user_id = callback_query.from_user.id
    data = callback_data.get("data")
    check_value = await redis.exists(f"manager_{user_id}")

    async with state.proxy() as state_data:
        type_view = state_data.get("view_type")
        date = state_data.get("date")
        date_start = state_data.get("date_start")
        date_end = state_data.get("date_end")

    if not check_value and data.isdigit():
        await redis.set(f"manager_{user_id}", data)
        await callback_query.message.answer(
            f"Вы добавили к фильтру менеджера:"
            f" {await service_telegram_user.get_user(user_id=data)}"
        )

    elif data.isdigit():
        await redis.append(f"manager_{user_id}", f" {data}")
        await callback_query.message.answer(
            f"Вы добавили к фильтру менеджера:"
            f" {await service_telegram_user.get_user(user_id=data)}"
        )

    if not data.isdigit():
        await callback_query.message.edit_reply_markup()
        if check_value:
            managers = await redis.get(f"manager_{user_id}")
            users_id = await validate_service.delete_copy_manager_id(managers=managers)
            logger.info(f"{users_id}")
        else:
            users_id = None
        validate_information = await validate_service.validate_input_info(
            data=data,
            type_view=type_view,
            date=date,
            date_start=date_start,
            date_end=date_end,
        )
        logger.info(validate_information)
        if validate_information == "cancel" or validate_information == "back_button":
            if check_value:
                logger.info("here")
                await redis.delete(f"manager_{user_id}")
            print("тут")
            if validate_information == "cancel":
                await callback_query.message.answer("Действия отменены❌")
                return await state.finish()

            elif validate_information == "back_button":
                logger.info("here")
                await ViewOrderOrReportFilter.type_date.set()
                await callback_query.message.answer("Возращаемся к педыдущему шагу⏪")
                await callback_query.message.answer(
                    "Выберите промежуток за который хотите просмотреть заказы: ",
                    reply_markup=date_keyboard
                )

        elif (
                validate_information == "order_all_managers_one_date"
                or validate_information == "order_all_managers_two_date"
        ):

            if validate_information == "order_all_managers_one_date":
                orders = await order_service.get_order_all_manager_by_date(date=date)
            else:
                orders = await order_service.get_order_all_manager_by_date(date=(date_start, date_end))

            if not orders:
                await state.finish()
                await redis.delete(f"manager_{user_id}")
                await callback_query.message.answer("Список заказов пуст")

            try:
                for order in orders:
                    await callback_query.message.answer(f"{hbold('💡Заказ')}\n\n"
                                                        f"{hbold('📄Описание')}: {order.description}\n"
                                                        f"{hbold('Создан')}: {order.created_at}"
                                                        f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                                        f"🧑🏾‍💻{hbold('Менеджер')}:  {order.user.last_name}")
                    images = await image_service.get_image_for_manager(order_id=order.id)
                    for image in images:
                        await bot.send_photo(
                            user_id,
                            image.image,
                            f"{hbold('📄Описание')}: {image.image_description}"
                        )
            except RetryAfter as retry:
                logger.info(f"Flood is Active: {retry}")
                await asyncio.sleep(retry.timeout)

            await state.finish()
        elif (
                validate_information == "order_next_one_date" or
                validate_information == "order_next_two_date"
        ):
            if validate_information == "order_next_one_date":
                orders = await order_service.get_order_filter_managers_by_date(
                    date=date,
                    users_id=users_id
                )
            else:
                orders = await order_service.get_order_filter_managers_by_date(
                    date=(date_start, date_end),
                    users_id=users_id
                )

            if not orders:
                await state.finish()
                await redis.delete(f"manager_{user_id}")
                await callback_query.message.answer("Список заказов пуст")

            await redis.delete(f"manager_{user_id}")
            try:
                for order in orders:
                    await callback_query.message.answer(f"{hbold('💡Заказ')}\n\n"
                                                        f"{hbold('📄Описание')}: {order.description}\n"
                                                        f"{hbold('Создан')}: {order.created_at}"
                                                        f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                                        f"🧑🏾‍💻{hbold('Менеджер')}:  {order.user.last_name}")
                    images = await image_service.get_image_for_manager(order_id=order.id)
                    for image in images:
                        await bot.send_photo(
                            user_id,
                            image.image,
                            f"{hbold('📄Описание')}: {image.image_description}"
                        )
            except RetryAfter as retry:
                logger.info(f"Flood is Active: {retry}")
                await asyncio.sleep(retry.timeout)

            await state.finish()

        elif (
            validate_information == "report_all_managers_one_date" or
            validate_information == "report_all_managers_two_date" or
            validate_information == "report_next_one_date" or
            validate_information == "report_next_two_date"
        ):
            async with state.proxy() as data:
                data["report_filter"] = validate_information
                data["users_id"] = users_id

            await callback_query.message.answer(
                "Выберите тип отчетов, которые вы хотите посмотреть:",
                reply_markup=report_status_keyboard
            )
            await ViewOrderOrReportFilter.report_status.set()


@inject
async def filter_and_send_report(
        callback_query: types.CallbackQuery,
        state: FSMContext,
        report_service: ReportService = Provide[Container.report_service],
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service],
        # redis: Redis = Provide[Container.redis]
):
    async with state.proxy() as state_data:
        date = state_data.get("date")
        date_start = state_data.get("date_start")
        date_end = state_data.get("date_end")
        validate_information = state_data.get("report_filter")
        users_id = state_data["users_id"]

    callback_data = callback_query.data
    logger.info(callback_query.data)
    report_status = False
    user_id = callback_query.from_user.id

    if callback_data == "active":
        report_status = True

    elif callback_data == "cancel":
        await state.finish()
        await callback_query.message.answer("Действия отменены❌")
        await callback_query.message.edit_reply_markup()

    if (
        validate_information == "report_all_managers_one_date" or
        validate_information == "report_all_managers_two_date"
    ):

        if validate_information == "report_all_managers_one_date":
            reports = await report_service.get_report_with_all_managers(
                date=date,
                status=report_status
            )
        else:
            reports = await report_service.get_report_with_all_managers(
                date=(date_start, date_end),
                status=report_status
            )

        if not reports:
            await callback_query.message.edit_reply_markup()
            await state.finish()
            return await callback_query.message.answer("Список отчетов пуст")

        for report in reports:

            if callback_data == "active":
                report_keyboard = await keyboard_service.report_keyboard_non_active(report_id=report.id)
            else:
                report_keyboard = await keyboard_service.report_keyboard_activate(report_id=report.id)
            try:
                await callback_query.message.answer(
                    f"{hbold('Отчет')}\n\n"
                    f"{report.report}\n"
                    f"{hbold('Дата')}: {report.created_at}\n"
                    f"{hbold('Менеджер')}: {report.user.last_name}",
                    reply_markup=report_keyboard
                )
            except RetryAfter as retry:
                logger.info(f"Flood Control: {retry}")
                await asyncio.sleep(retry.timeout)

        await state.finish()

    elif (
            validate_information == "report_next_one_date" or
            validate_information == "report_next_two_date"
    ):
        if validate_information == "report_next_one_date":
            reports = await report_service.get_managers_with_filter_managers(
                date=date,
                users_id=users_id,
                status=report_status
            )

        else:
            reports = await report_service.get_managers_with_filter_managers(
                date=(date_start, date_end),
                users_id=users_id,
                status=report_status
            )

        if not reports:
            await callback_query.message.edit_reply_markup()
            await state.finish()
            return await callback_query.message.answer("Список отчетов пуст")

        # await redis.remove_value(user_id=user_id)
        for report in reports:

            if callback_data == "active":
                report_keyboard = await keyboard_service.report_keyboard_non_active(report_id=report.id)
            else:
                report_keyboard = await keyboard_service.report_keyboard_activate(report_id=report.id)
            try:
                await callback_query.message.answer(
                    f"{hbold('Отчет')}\n\n"
                    f"{report.report}\n"
                    f"{hbold('Дата')}: {report.created_at}\n"
                    f"{hbold('Менеджер')}: {report.user.last_name}",
                    reply_markup=report_keyboard
                )
            except RetryAfter as retry:
                logger.info(f"Flood Control: {retry}")
                await asyncio.sleep(retry.timeout)

        await state.finish()
    await callback_query.message.edit_reply_markup()


@inject
async def in_work(
        message: types.Message,
        service_telegram_user: TelegramUserService = Provide[Container.service_telegram_user],
        order_service: OrderService = Provide[Container.order_service],
        images_service: ImagesService = Provide[Container.images_service],
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service]
):
    user_id = message.from_user.id
    if not await service_telegram_user.check_permission_status(
        user_id=user_id,
        permission_statuses=(
            TelegramUser.PermissionStatus.super_user,
            TelegramUser.PermissionStatus.manager
        )
    ):
        return await message.answer("⛔️У вас нет прав для совершения этого действия")

    orders = await order_service.get_order_active_or_partially_assembled(statuses=(
            Order.OrderStatusWork.partially_assembled,
            Order.OrderStatusWork.assembled
        ))
    if not orders:
        return await message.answer("Список заказов в работе пуст!")

    try:
        for order in orders[0*5:0*5+5]:
            await message.answer(f"💡{hbold('Активный заказа')}\n"
                                 f"📄{hbold('Описание')}:  {order.description}\n"
                                 f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                 f"🧑🏾‍💻{hbold('Менеджер')}:  {order.user.last_name}")
            images = await images_service.get_images_assembled_or_in_work()
            for image in images:
                await bot.send_photo(
                    user_id,
                    image.image,
                    f"{hbold('📄Описание: ')} {image.image_description}",
                    reply_markup=await keyboard_service.forming_manager_keyboard(
                        image_id=image.id,
                    )
                )
    except RetryAfter as retry:
        logger.info(f"Flood is Active: {retry}")
        await asyncio.sleep(retry.timeout)

    await message.answer(
        "Чтобы просмотреть следущие заказы, нажмите на кнопку ниже",
        reply_markup=await keyboard_service.watch_next_keyboard(
            last_num=0,
            type_orders="watch_orders_next_all"
        )
    )


@inject
async def watch_next_all_orders(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        image_service: ImagesService = Provide[Container.keyboard_service],
        order_service: OrderService = Provide[Container.order_service],
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service]
):
    await callback_query.message.edit_reply_markup()
    last_num = int(callback_data.get("data"))
    last_num += 1
    user_id = callback_query.from_user.id
    orders = await order_service.get_order_active_or_partially_assembled(statuses=(
        Order.OrderStatusWork.partially_assembled,
        Order.OrderStatusWork.assembled
    ))
    try:
        for order in orders[last_num * 5:last_num * 5 + 5]:
            await callback_query.message.answer(f"💡{hbold('Активный заказа')}\n"
                                 f"📄{hbold('Описание')}:  {order.description}\n"
                                 f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                 f"🧑🏾‍💻{hbold('Менеджер')}:  {order.user.last_name}")
            images = await image_service.get_images_assembled_or_in_work()
            for image in images:
                await bot.send_photo(
                    user_id,
                    image.image,
                    f"{hbold('📄Описание: ')} {image.image_description}",
                    reply_markup=await keyboard_service.forming_manager_keyboard(
                        image_id=image.id,
                    )
                )
    except RetryAfter as retry:
        await asyncio.sleep(retry.timeout)
        logger.info(f"Flood is Active: {retry}")

    await callback_query.message.answer(
        "Чтобы просмотреть следущие заказы, нажмите на кнопку ниже",
        reply_markup=await keyboard_service.watch_next_keyboard(
            last_num=0,
            type_orders="watch_orders_next_all"
        )
    )


@inject
async def update_report_status(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        report_service: ReportService = Provide[Container.report_service],
):
    report_id = callback_data.get("data")
    type_report = callback_data.get("type")

    if type_report == "deactivate_report":
        await report_service.update_report_status(
            repost_id=report_id,
            status=False
        )
    elif type_report == "activate_report":
        await report_service.update_report_status(
            repost_id=report_id,
            status=True
        )

    await callback_query.message.answer("Статус отчета обновлен✅")
    await callback_query.message.delete()
    await state.finish()


def register_views_orders_handlers(dp: Dispatcher, *args, **kwargs):
    dp.register_message_handler(start_view_orders_or_report, lambda message: message.text == "Просмотреть данные🗂")
    dp.register_callback_query_handler(get_type_of_view, state=ViewOrderOrReportFilter.type_of_view)
    dp.register_callback_query_handler(get_type_date, state=ViewOrderOrReportFilter.type_date)
    dp.register_callback_query_handler(
        get_other_date,
        calendar_callback.filter(),
        state=ViewOrderOrReportFilter.date_start
    )
    dp.register_callback_query_handler(
        save_end_date,
        calendar_callback.filter(),
        state=ViewOrderOrReportFilter.date_end
    )
    dp.register_callback_query_handler(
        save_managers_and_send_answer,
        view_managers_callback.filter(type="views_managers"),
        state=ViewOrderOrReportFilter.managers
    )
    dp.register_message_handler(in_work, lambda message: message.text == 'В работе🌋')
    dp.register_callback_query_handler(
        watch_next_all_orders,
        watch_next_callback.filter(type="watch_orders_next_all")
    )
    dp.register_callback_query_handler(filter_and_send_report, state=ViewOrderOrReportFilter.report_status)
    dp.register_callback_query_handler(update_report_status, report_callback.filter(type="activate_report"))
    dp.register_callback_query_handler(update_report_status, report_callback.filter(type="deactivate_report"))