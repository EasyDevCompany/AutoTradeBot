import asyncio

from aiogram.utils.exceptions import RetryAfter
from dependency_injector.wiring import Provide, inject
from loguru import logger

from aiogram import types, Dispatcher
from aiogram.utils.markdown import hbold

from app.core.containers import Container
from loader import bot

from app.models.telegram_user import TelegramUser
from app.models.images import Images
from app.models.order import Order

from app.services.order import OrderService
from app.services.images import ImagesService
from app.services.telegram_user import TelegramUserService

from app.utils.keyboards.form_inline_keyboard import FormInlineKeyboardService
from app.utils.keyboards.callback_data import images_callback, watch_next_callback


@inject
async def images_assembled(
        message: types.Message,
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service],
        images_service: ImagesService = Provide[Container.images_service],
        order_service: OrderService = Provide[Container.order_service],
        telegram_user_service: TelegramUserService = Provide[Container.service_telegram_user]
):
    user_id = message.from_user.id
    if not await telegram_user_service.check_permission_status(
            user_id=user_id,
            permission_statuses=(
                    TelegramUser.PermissionStatus.driver,
                    TelegramUser.PermissionStatus.super_user,
            )
    ):
        return await message.answer("⛔️У вас нет прав для совершения этого действия")

    orders = await order_service.get_order_active_or_partially_assembled(
        statuses=(
            Order.OrderStatusWork.in_work,
            Order.OrderStatusWork.partially_assembled
        )
    )

    if not orders:
        return await message.answer("Список заказов пуст")

    try:
        for order in orders[0*5:0*5+5]:
            await message.answer(f"💡{hbold('Активный заказа')}\n"
                                 f"📄{hbold('Описание')}:  {order.description}\n"
                                 f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                 f"🧑🏾‍💻{hbold('Менеджер')}:  {order.user.last_name}")

            for image in await images_service.get_images_by_order(
                    image_status=Images.ImageStatus.in_work,
                    order_id=order.id
            ):
                await bot.send_photo(
                    user_id,
                    image.image,
                    f"{hbold('📄Описание')}: {image.image_description}",
                    reply_markup=await keyboard_service.forming_image_keyboard(
                        image_id=image.id,
                        text="Собран📥",
                        type_img="image_assembled"
                    )
                )
    except RetryAfter as retry:
        logger.info(f"Flood is Active: {retry}")
        await asyncio.sleep(retry.timeout)

    await message.answer(
        "Чтобы просмотреть следущие заказы, нажмите на кнопку ниже",
        reply_markup=await keyboard_service.watch_next_keyboard(
            last_num=0,
            type_orders="orders_next_in_work"
        )
    )


@inject
async def update_image_status_on_assembled(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        image_service: ImagesService = Provide[Container.images_service]
):
    await callback_query.message.delete()
    user_id = callback_query.from_user.id
    image_id = callback_data.get("data")
    await image_service.update_images_status(
        image_id=image_id,
        image_status=Images.ImageStatus.assembled,
        image_status_past=Images.ImageStatus.in_work,
        user_id=user_id
    )


@inject
async def delivered_images(
        message: types.Message,
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service],
        images_service: ImagesService = Provide[Container.images_service],
        order_service: OrderService = Provide[Container.order_service],
        telegram_user_service: TelegramUserService = Provide[Container.service_telegram_user]
):
    user_id = message.from_user.id
    if not await telegram_user_service.check_permission_status(
            user_id=user_id,
            permission_statuses=(
                    TelegramUser.PermissionStatus.driver,
                    TelegramUser.PermissionStatus.super_user,
            )
    ):
        return await message.answer("⛔️У вас нет прав для совершения этого действия")

    orders = await order_service.get_order_active_or_partially_assembled(
        statuses=(
            Order.OrderStatusWork.partially_assembled,
            Order.OrderStatusWork.assembled
        )
    )

    if not orders:
        return await message.answer("Список заказов пуст")

    try:
        for order in orders[0*5:0*5+5]:
            await message.answer(f"💡{hbold('Активный заказа')}\n"
                                 f"📄{hbold('Описание')}:  {order.description}\n"
                                 f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                 f"🧑🏾‍💻{hbold('Менеджер')}:  {order.user.last_name}")

            for image in await images_service.get_images_by_order(
                    image_status=Images.ImageStatus.assembled,
                    order_id=order.id
            ):
                await bot.send_photo(
                    user_id,
                    image.image,
                    f"{hbold('📄Описание')}: {image.image_description}",
                    reply_markup=await keyboard_service.forming_image_keyboard(
                        image_id=image.id,
                        text="Доставлен💨",
                        type_img="image_delivered"
                    )
                )
    except RetryAfter as retry:
        logger.info(f"Flood is Active: {retry}")
        await asyncio.sleep(retry.timeout)

    await message.answer(
        "Чтобы просмотреть следущие заказы, нажмите на кнопку ниже",
        reply_markup=await keyboard_service.watch_next_keyboard(
            last_num=0,
            type_orders="watch_orders_next_assembled"
        )
    )


@inject
async def watch_next_orders_in_work(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service],
        order_service: OrderService = Provide[Container.order_service],
        images_service: ImagesService = Provide[Container.images_service]
):
    user_id = callback_query.from_user.id
    last_num = int(callback_data.get("data"))
    last_num += 1
    orders = await order_service.get_order_active_or_partially_assembled(
        statuses=(
            Order.OrderStatusWork.in_work,
            Order.OrderStatusWork.partially_assembled
        )
    )

    try:
        for order in orders[last_num * 5:last_num * 5 + 5]:
            await callback_query.message.answer(f"💡{hbold('Активный заказа')}\n"
                                 f"📄{hbold('Описание')}:  {order.description}\n"
                                 f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                 f"🧑🏾‍💻{hbold('Менеджер')}:  {order.user.last_name}")

            for image in await images_service.get_images_by_order(
                    image_status=Images.ImageStatus.in_work,
                    order_id=order.id
            ):
                await bot.send_photo(
                    user_id,
                    image.image,
                    f"{hbold('📄Описание')}: {image.image_description}",
                    reply_markup=await keyboard_service.forming_image_keyboard(
                        image_id=image.id,
                        text="Доставлен💨",
                        type_img="image_delivered"
                    )
                )
    except RetryAfter as retry:
        await asyncio.sleep(retry.timeout)
        logger.info(f"Flood is Active: {retry}")

    await callback_query.message.answer(
        "Чтобы просмотреть следущие заказы, нажмите на кнопку ниже",
        reply_markup=await keyboard_service.watch_next_keyboard(
            last_num=last_num,
            type_orders="orders_next_in_work"
        )
    )


@inject
async def watch_next_orders_assembled(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service],
        order_service: OrderService = Provide[Container.order_service],
        images_service: ImagesService = Provide[Container.images_service]
):
    user_id = callback_query.from_user.id
    last_num = int(callback_data.get("data"))
    last_num += 1
    orders = await order_service.get_order_active_or_partially_assembled(
        statuses=(
            Order.OrderStatusWork.partially_assembled,
            Order.OrderStatusWork.assembled
        )
    )
    try:
        for order in orders[last_num * 5:last_num * 5 + 5]:
            await callback_query.message.answer(f"💡{hbold('Активный заказа')}\n"
                                 f"📄{hbold('Описание')}:  {order.description}\n"
                                 f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                 f"🧑🏾‍💻{hbold('Менеджер')}:  {order.user.last_name}")

            for image in await images_service.get_images_by_order(
                    image_status=Images.ImageStatus.assembled,
                    order_id=order.id
            ):
                await bot.send_photo(
                    user_id,
                    image.image,
                    f"{hbold('📄Описание')}: {image.image_description}",
                    reply_markup=await keyboard_service.forming_image_keyboard(
                        image_id=image.id,
                        text="Доставлен💨",
                        type_img="image_delivered"
                    )
                )
    except RetryAfter as retry:
        logger.info(f"Flood is Active: {retry}")
        await asyncio.sleep(retry.timeout)

    await callback_query.message.answer(
        "Чтобы просмотреть следущие заказы, нажмите на кнопку ниже",
        reply_markup=await keyboard_service.watch_next_keyboard(
            last_num=last_num,
            type_orders="watch_orders_next_assembled"
        )
    )


@inject
async def update_message_status_on_delivered(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        image_service: ImagesService = Provide[Container.images_service]
):
    await callback_query.message.delete()
    user_id = callback_query.from_user.id
    image_id = callback_data.get("data")
    return await image_service.update_images_status(
        image_id=image_id,
        image_status=Images.ImageStatus.delivered,
        image_status_past=Images.ImageStatus.assembled,
        user_id=user_id
    )


def register_driver_handler(dp: Dispatcher, *args, **kwargs):
    dp.register_message_handler(images_assembled, lambda message: message.text == "Все заказы👨‍💻")
    dp.register_message_handler(delivered_images, lambda message: message.text == 'Собранные заказы💶')
    dp.register_callback_query_handler(
        update_image_status_on_assembled,
        images_callback.filter(type="image_assembled")
    )
    dp.register_callback_query_handler(
        update_message_status_on_delivered,
        images_callback.filter(type="image_delivered")
    )
    dp.register_callback_query_handler(
        watch_next_orders_in_work,
        watch_next_callback.filter(type="orders_next_in_work")
    )
    dp.register_callback_query_handler(
        watch_next_orders_assembled,
        watch_next_callback.filter(type="watch_orders_next_assembled")
    )
