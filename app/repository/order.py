from sqlalchemy import or_

from .base import RepositoryBase
from app.models.order import Order


class RepositoryOrder(RepositoryBase[Order]):

    def get_order_by_status(self,  statuses: tuple) -> list:
        return self._session.query(self._model).filter(
            or_(
                self._model.order_status == statuses[0],
                self._model.order_status == statuses[1],
            )
        ).all()

    def get_order_for_manager(self, user_id) -> list:
        return self._session.query(self._model).filter(
            or_(
                self._model.order_status == Order.OrderStatusWork.in_work,
                self._model.order_status == Order.OrderStatusWork.partially_assembled,
                self._model.order_status == Order.OrderStatusWork.assembled
            ), Order.user_id == user_id
        ).all()

    def get_order_by_date_all_managers(self, date: tuple):
        return self._session.query(self._model).filter(
            self._model.created_at >= date[0], self._model.created_at <= date[1],
        ).all()

    def get_order_by_date_filter_managers(self, date: tuple, user_id):
        return self._session.query(self._model).filter(
            self._model.created_at >= date[0],
            self._model.created_at <= date[1],
            self._model.user_id == user_id
        ).all()
