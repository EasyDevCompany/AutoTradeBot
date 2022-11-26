from aiogram import Dispatcher
from .throttling import ThrottlingMiddleware
from .premission_status_middleware import PermissionStatusMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(PermissionStatusMiddleware())