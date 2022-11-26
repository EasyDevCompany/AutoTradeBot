from app.repository.telegram_user import RepositoryTelegramUser
from app.repository.report import RepositoryReport

from loader import bot


class ReportService:

    def __init__(
            self,
            repository_telegram_user: RepositoryTelegramUser,
            repository_report: RepositoryReport
    ):
        self._repository_telegram_user = repository_telegram_user
        self._repository_report = repository_report

    async def create_report(self, user_id: str, report: str):
        user = self._repository_telegram_user.get(user_id=user_id)

        if user is None:
            return await bot.send_message(user_id, "Вы не вошли в систему и не имеете права создать отчет")

        obj_in = {
            "user_id": user_id,
            "report": report,
            "status": True,
            "user": user
        }
        report = self._repository_report.create(obj_in=obj_in)
        return report

    async def get_report_with_all_managers(self, date, status: bool):
        if isinstance(date, tuple):
            return self._repository_report.report_date_filter(date=date, status=status)
        else:
            return self._repository_report.list(created_at=date, status=status)

    async def get_managers_with_filter_managers(self, date, users_id, status):
        report_list = []
        if not isinstance(date, tuple):
            for user in users_id:
                reports = self._repository_report.list(
                    created_at=date,
                    user_id=user,
                    status=status
                )
                for report in reports:
                    report_list.append(report)
        else:
            for user in users_id:
                reports = self._repository_report.report_manager_and_date_filter(
                    date=date,
                    user_id=user,
                    status=status
                )
                for report in reports:
                    report_list.append(report)

        return report_list

    async def update_report_status(self, status: bool, repost_id):
        db_obj = self._repository_report.get(id=repost_id)
        obj_in = {"status": status}

        return self._repository_report.update(
            db_obj=db_obj,
            obj_in=obj_in
        )
