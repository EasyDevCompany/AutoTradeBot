from .base import RepositoryBase
from app.models.report import Report


class RepositoryReport(RepositoryBase[Report]):

    def report_date_filter(self, date, status: bool):
        return self._session.query(self._model).filter(
            date[0] >= self._model.created_at,
            date[1] <= self._model.created_at,
            self._model.status == status
        ).all()

    def report_manager_and_date_filter(self, date, user_id, status: bool):
        print(date)
        return self._session.query(self._model).filter(
            date[0] >= self._model.created_at,
            date[1] <= self._model.created_at,
            self._model.user_id == user_id,
            self._model.status == status
        ).all()
