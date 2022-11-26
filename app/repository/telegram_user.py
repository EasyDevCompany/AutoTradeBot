from sqlalchemy import or_

from .base import RepositoryBase
from app.models.telegram_user import TelegramUser


class RepositoryTelegramUser(RepositoryBase[TelegramUser]):

    def check_user_permission_status(
            self,
            user_id: str,
            permission_statuses: tuple
    ):

        return self._session.query(self._model).filter(
            or_(
                self._model.permission_status == permission_statuses[0],
                self._model.permission_status == permission_statuses[1],
            ), self._model.user_id == user_id
        ).first()

    def get_managers_and_super_users(self):
        return self._session.query(self._model).filter(
            or_(
                self._model.permission_status == TelegramUser.PermissionStatus.manager,
                self._model.permission_status == TelegramUser.PermissionStatus.super_user
            )
        ).all()