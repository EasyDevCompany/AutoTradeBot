from dependency_injector import containers, providers

from app import redis_init
from app.core.config import Settings

from app.models.telegram_user import TelegramUser
from app.models.order import Order
from app.models.images import Images
from app.models.report import Report

from app.repository.telegram_user import RepositoryTelegramUser
from app.repository.order import RepositoryOrder
from app.repository.images import RepositoryImages
from app.repository.report import RepositoryReport

from app.services.validators import ValidateInformationService
from app.services.telegram_user import TelegramUserService
from app.services.order import OrderService
from app.services.images import ImagesService
from app.services.report import ReportService

from app.utils.keyboards.form_inline_keyboard import FormInlineKeyboardService


class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Settings)

    repository_telegram_user = providers.Singleton(RepositoryTelegramUser, model=TelegramUser)
    repository_order = providers.Singleton(RepositoryOrder, model=Order)
    repository_images = providers.Singleton(RepositoryImages, model=Images)
    repository_report = providers.Singleton(RepositoryReport, model=Report)

    redis = providers.Resource(redis_init.init_redis_pool, host=config.provided.REDIS_HOST)

    keyboard_service = providers.Factory(
        FormInlineKeyboardService,
        repository_telegram_user=repository_telegram_user
    )
    validate_service = providers.Factory(ValidateInformationService)
    service_telegram_user = providers.Factory(
        TelegramUserService,
        repository_telegram_user=repository_telegram_user
    )
    images_service = providers.Factory(
        ImagesService,
        repository_images=repository_images,
        repository_telegram_user=repository_telegram_user,
        repository_order=repository_order,
        keyboard_service=keyboard_service
    )
    order_service = providers.Factory(
        OrderService,
        repository_telegram_user=repository_telegram_user,
        repository_order=repository_order
    )
    report_service = providers.Factory(
        ReportService,
        repository_telegram_user=repository_telegram_user,
        repository_report=repository_report
    )

