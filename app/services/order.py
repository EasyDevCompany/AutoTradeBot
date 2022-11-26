from loguru import logger

from loader import bot
from app.models.order import Order

from app.repository.telegram_user import RepositoryTelegramUser
from app.repository.order import RepositoryOrder


class OrderService:

    def __init__(
            self,
            repository_telegram_user: RepositoryTelegramUser,
            repository_order: RepositoryOrder,
    ):
        self._repository_telegram_user = repository_telegram_user
        self._repository_order = repository_order

    async def create_order(self, user_id, description: str) -> Order:
        user = self._repository_telegram_user.get(user_id=user_id)

        if user is None:
            return await bot.send_message(user_id, "Вы не вошли в систему и не имеете права создать объявление")

        obj_in = {
            "user_id": user_id,
            "description": description,
            "order_status": Order.OrderStatusWork.in_work,
            "user": user
        }
        order = self._repository_order.create(obj_in=obj_in)

        return order

    async def get_order_active_or_partially_assembled(self, statuses: tuple) -> list[Order]:
        orders = self._repository_order.get_order_by_status(statuses=statuses)
        return orders

    async def get_order_for_manager(self, user_id: str) -> list[Order]:
        user = self._repository_telegram_user.get(user_id=user_id)
        return self._repository_order.get_order_for_manager(user_id=user.id)

    async def update_order(self, order_id, description: str):
        db_obj = self._repository_order.get(id=order_id)
        obj_in = {"description": description}

        return self._repository_order.update(
            db_obj=db_obj,
            obj_in=obj_in,
            commit=True
        )

    async def get_order_all_manager_by_date(self, date):
        if not isinstance(date, tuple):
            orders = self._repository_order.list(created_at=date)
        else:
            orders = self._repository_order.get_order_by_date_all_managers(date=date)

        return orders

    async def get_order_filter_managers_by_date(self, date, users_id):
        orders_list = []
        if not isinstance(date, tuple):
            for user in users_id:
                orders = self._repository_order.list(created_at=date, user_id=user)
                for order in orders:
                    orders_list.append(order)
        else:
            for user in users_id:
                orders = self._repository_order.get_order_by_date_filter_managers(date=date, user_id=user)
                for order in orders:
                    orders_list.append(order)

        return orders_list

    async def get_all_orders(self):
        return self._repository_order.list()





