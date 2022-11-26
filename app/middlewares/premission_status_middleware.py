import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from app.services.telegram_user import TelegramUserService


class PermissionStatusMiddleware(BaseMiddleware):
    ADMIN_ID = 688136452
    # def __init__(self, service_telegram_user: TelegramUserService):
    #     self._service_telegram_user = service_telegram_user
    #     super(PermissionStatusMiddleware, self).__init__()

    async def check_user_permission_status(self, message: types.Message):
        if message.from_user.id != self.ADMIN_ID:
            raise CancelHandler()


