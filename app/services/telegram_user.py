from app.repository.telegram_user import RepositoryTelegramUser


class TelegramUserService:

    def __init__(self, repository_telegram_user: RepositoryTelegramUser) -> None:
        self._repository_telegram_user = repository_telegram_user

    async def registration_user(self, phone_number: str, obj_in: dict) -> bool:
        user = self._repository_telegram_user.get(phone_number=phone_number)
        if user is None:
            return False

        elif user.user_id is None:
            self._repository_telegram_user.update(
                db_obj=user,
                obj_in=obj_in,
                commit=True
            )

        return True

    async def check_permission_status(self, user_id: str, permission_statuses: tuple) -> bool:
        user = self._repository_telegram_user.check_user_permission_status(
            user_id=user_id,
            permission_statuses=permission_statuses
        )

        if user is None:
            return False

        return True

    async def get_user(self, user_id):
        return self._repository_telegram_user.get(id=user_id)

    async def get_user_permission_status(self, user_id):
        return self._repository_telegram_user.get(user_id=user_id).permission_status

    async def create_users(self, users: dict):
        self._repository_telegram_user.create(obj_in=users)


