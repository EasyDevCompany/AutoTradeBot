from loguru import logger
from dependency_injector.wiring import Provide, inject

from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher

from app.models.telegram_user import TelegramUser

from app.utils.states.create_oder_state import CreateOrder
from app.utils.keyboards import base
from app.utils.keyboards import create_order

from app.services.telegram_user import TelegramUserService
from app.services.order import OrderService
from app.services.images import ImagesService

from app.core.containers import Container


@inject
async def start_creating_order(
        message: types.Message,
        service_telegram_user: TelegramUserService = Provide[Container.service_telegram_user]
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

    await message.answer("📄Введите описание к заказу: ", reply_markup=base.cancel_keyboard)
    await CreateOrder.next()


async def check_description_and_save(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
    await message.answer("📷Отправьте боту скрин к заказу: ", reply_markup=base.cancel_and_back_keyboard)
    await CreateOrder.next()


async def get_images_and_save(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["image"] = message.photo[0].file_id
    await message.answer("📄Напишите описание к скрину: ", reply_markup=base.cancel_and_back_keyboard)
    await CreateOrder.next()


@inject
async def get_image_description_and_save(
        message: types.Message,
        state: FSMContext,
        images_service: ImagesService = Provide[Container.images_service]
):
    user_id = message.from_user.id

    async with state.proxy() as data:
        data["image_description"] = message.text
        image = data["image"]

        order_id = data.get("order_id")

        if order_id:
            await images_service.create_images(
                image_description=message.text,
                image=image,
                order_id=order_id,
            )

    await message.answer("Выберите один пункт из меню ниже: ", reply_markup=create_order.public_keyboard)
    await CreateOrder.next()


@inject
async def waite_next_answer(
        callback_query: types.CallbackQuery,
        state: FSMContext,
        order_service: OrderService = Provide[Container.order_service],
        images_service: ImagesService = Provide[Container.images_service]
):
    await callback_query.message.edit_reply_markup()

    callback_data = callback_query.data
    logger.info(callback_data)
    user_id = callback_query.from_user.id

    if callback_data != "cancel" and callback_data != "back":
        async with state.proxy() as data:
            image = data["image"]
            description = data["description"]
            image_description = data["image_description"]

            logger.info(f"{data.get('order_id')}")

            if not data.get("order_id"):
                order = await order_service.create_order(
                    user_id=user_id,
                    description=description,
                )

                await images_service.create_images(
                    order_id=order.id,
                    image_description=image_description,
                    image=image
                )

                data["order_id"] = order.id

        if callback_data == "public":
            await callback_query.message.answer("Заказ успешно опубликован✔️")
            await state.finish()

        elif callback_data == "add_image":
            await callback_query.message.answer("📷Отправьте боту еще один скрин: ")
            await CreateOrder.image.set()

    elif callback_data == "cancel":
        await callback_query.message.answer("Действия отменены❌")
        await state.finish()

    elif callback_data == "back":
        await CreateOrder.previous()
        await callback_query.message.answer("Вернулись на предыдущее действие↪️")
        await callback_query.message.answer(
            "Напишите описание к скрину: ",
            reply_markup=base.cancel_and_back_keyboard
        )


def register_create_order_handler(dp: Dispatcher, *args, **kwargs):
    dp.register_message_handler(start_creating_order, lambda message: message.text == 'Сформировать заказ📝')
    dp.register_message_handler(check_description_and_save, state=CreateOrder.description)
    dp.register_message_handler(get_images_and_save, state=CreateOrder.image, content_types=types.ContentTypes.PHOTO)
    dp.register_message_handler(get_image_description_and_save, state=CreateOrder.image_description)
    dp.register_callback_query_handler(waite_next_answer, state=CreateOrder.waite_next_answer)
    dp.message_handler()

