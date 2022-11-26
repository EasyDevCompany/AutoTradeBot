from loguru import logger
from app.utils.states.create_oder_state import CreateOrder
from app.utils.keyboards import base

from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher


async def cancel_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.answer("Действия отменены❌")


async def back_button_create_order(callback_query: types.CallbackQuery, state: FSMContext):
    await CreateOrder.previous()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.answer("Вернулись на предыдущее действие↪️")

    get_current_state = await state.get_state()
    logger.info(get_current_state)

    if get_current_state == "CreateOrder:description":
        await callback_query.message.answer(
            "Введите описание к заказу: ",
            reply_markup=base.cancel_keyboard
        )

    elif get_current_state == "CreateOrder:image":
        await callback_query.message.answer(
            "Отправьте боту скрин к заказу: ",
            reply_markup=base.cancel_and_back_keyboard)


def register_base_handler(dp: Dispatcher, *args, **kwargs):
    dp.register_callback_query_handler(cancel_button, text="cancel", state="*")
    dp.register_callback_query_handler(back_button_create_order, text='back', state="*")
