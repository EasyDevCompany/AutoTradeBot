import asyncio

from aiogram.utils.exceptions import RetryAfter
from dependency_injector.wiring import Provide, inject
from loguru import logger

from aiogram import types, Dispatcher
from aiogram.utils.markdown import hbold
from aiogram.dispatcher.storage import FSMContext

from app.core.containers import Container
from loader import bot

from app.models.telegram_user import TelegramUser

from app.services.order import OrderService
from app.services.images import ImagesService
from app.services.telegram_user import TelegramUserService

from app.utils.keyboards.form_inline_keyboard import FormInlineKeyboardService
from app.utils.keyboards.callback_data import manager_callback, orders_callback, watch_next_callback
from app.utils.keyboards import base
from app.utils.keyboards.manager import image_edit_keyboard
from app.utils.states.manager_states import EditOrder, EditImages


@inject
async def managers_orders(
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
            TelegramUser.PermissionStatus.manager,
            TelegramUser.PermissionStatus.super_user
        )
    ):
        return await message.answer("⛔️У вас нет прав для совершения этого действия")

    orders = await order_service.get_order_for_manager(user_id=user_id)

    if not orders:
        return await message.answer("Список заказов пуст")

    try:
        for order in orders[0*5:0*5+5]:
            await message.answer(f"💡{hbold('Мой заказ:')}\n"
                                 f"📄{hbold('Описание')}:  {order.description}\n"
                                 f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                 f"{hbold('Дата формирования')}: {order.created_at}",
                                 reply_markup=await keyboard_service.order_edit_keyboard(
                                     order_id=order.id
                                    )
                                 )
            for image in await images_service.get_image_for_manager(
                    order_id=order.id
            ):
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
    logger.info("Закончили")
    await message.answer(
        "Чтобы просмотреть следущие заказы, нажмите на кнопку ниже",
        reply_markup=await keyboard_service.watch_next_keyboard(
            last_num=0,
            type_orders="watch_my_orders_manager"
        )
    )


@inject
async def watch_next_my_orders_managers(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        order_service: OrderService = Provide[Container.order_service],
        images_service: ImagesService = Provide[Container.images_service],
        keyboard_service: FormInlineKeyboardService = Provide[Container.keyboard_service]
):
    await callback_query.message.edit_reply_markup()
    last_num = int(callback_data.get("data"))
    last_num += 1
    user_id = callback_query.from_user.id
    orders = await order_service.get_order_for_manager(user_id=user_id)
    try:
        for order in orders[last_num * 5:last_num * 5 + 5]:
            await callback_query.message.answer(f"💡{hbold('Мой заказ:')}\n"
                                 f"📄{hbold('Описание')}:  {order.description}\n"
                                 f"❗️{hbold('Статус')}:  {order.order_status}\n\n"
                                 f"{hbold('Дата формирования')}: {order.created_at}",
                                 reply_markup=await keyboard_service.order_edit_keyboard(
                                     order_id=order.id
                                 )
                                 )
            for image in await images_service.get_image_for_manager(
                    order_id=order.id
            ):
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

    await callback_query.message.answer(
        "Чтобы просмотреть следущие заказы, нажмите на кнопку ниже",
        reply_markup=await keyboard_service.watch_next_keyboard(
            last_num=last_num,
            type_orders="watch_my_orders_manager"
        )
    )


@inject
async def get_order_details(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        images_service: ImagesService = Provide[Container.images_service]
):
    await callback_query.message.edit_reply_markup()
    user_id = callback_query.from_user.id
    order_id = callback_data.get("data")
    images = await images_service.get_image_for_manager(order_id=order_id)

    for image in images:
        await bot.send_photo(
            user_id,
            image.image,
            f"{hbold('📄Описание: ')} {image.image_description}",
        )


async def edit_order(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    await callback_query.message.edit_reply_markup()
    order_id = callback_data.get("data")
    async with state.proxy() as data:
        data["order_id"] = order_id

    await callback_query.message.answer(
        "Введите новое описание: ",
        reply_markup=base.cancel_keyboard
    )

    await EditOrder.description.set()


@inject
async def get_and_save_new_order_description(
        message: types.Message,
        state: FSMContext,
        order_service: OrderService = Provide[Container.order_service],
):
    async with state.proxy() as data:
        order_id = data.get("order_id")

    await order_service.update_order(
        order_id=order_id,
        description=message.text
    )

    await message.answer("Описание заказа обновлено✅")
    await state.finish()


async def start_edit_image(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    await callback_query.message.edit_reply_markup()
    image_id = callback_data.get("data")
    async with state.proxy() as data:
        data["image_id"] = image_id

    await callback_query.message.answer(
        "Выберите то, что хотите отредактировать: ",
        reply_markup=image_edit_keyboard
    )

    await EditImages.edit_answer.set()


async def get_edit_answer(callback_query: types.CallbackQuery, state: FSMContext):
    callback_data = callback_query.data

    async with state.proxy() as data:
        data["edit_answer"] = callback_data

    if callback_data == "image":
        await callback_query.message.answer(
            "Отправьте боту новый скрин",
            reply_markup=base.cancel_keyboard
        )
        await EditImages.image.set()

    elif callback_data == "image_description":
        await callback_query.message.answer(
            "Отправьте боту новое описание",
            reply_markup=base.cancel_keyboard
        )
        await EditImages.image_description.set()

    else:
        await callback_query.message.answer("Действия отменены❌")
        await state.finish()


@inject
async def edit_image(
        message: types.Message,
        state: FSMContext,
        image_service: ImagesService = Provide[Container.images_service]
):
    async with state.proxy() as data:
        image_id = data.get("image_id")
        edit_answer = data.get("edit_answer")

    logger.info(image_id)
    await image_service.update_images(
        edit_obj=message.photo[0].file_id,
        edit_answer=edit_answer,
        image_id=image_id
    )

    await message.answer("Скрин успешно обновлен✅")
    await state.finish()


@inject
async def edit_image_description(
        message: types.Message,
        state: FSMContext,
        image_service: ImagesService = Provide[Container.images_service]
):
    async with state.proxy() as data:
        image_id = data.get("image_id")
        edit_answer = data.get("edit_answer")

    await image_service.update_images(
        edit_obj=message.text,
        edit_answer=edit_answer,
        image_id=image_id
    )

    await message.answer("Описание успешно обновлено✅")
    await state.finish()


def register_manager_handlers(dp: Dispatcher, *args, **kwargs):
    dp.register_message_handler(managers_orders, lambda message: message.text == "Мои заказы💼")
    dp.register_callback_query_handler(
        get_order_details,
        orders_callback.filter(type="orders_details")
    )
    dp.register_callback_query_handler(
        edit_order,
        orders_callback.filter(type="orders_edit")
    )
    dp.register_message_handler(get_and_save_new_order_description, state=EditOrder.description)
    dp.register_callback_query_handler(
        start_edit_image,
        manager_callback.filter(type="manager_keyboard_edit")
    )
    dp.register_callback_query_handler(get_edit_answer, state=EditImages.edit_answer)
    dp.register_message_handler(
        edit_image,
        state=EditImages.image,
        content_types=types.ContentTypes.PHOTO
    )
    dp.register_message_handler(edit_image_description, state=EditImages.image_description)
    dp.register_callback_query_handler(
        watch_next_my_orders_managers,
        watch_next_callback.filter(type="watch_my_orders_manager")
    )