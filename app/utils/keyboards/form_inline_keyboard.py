import calendar

from datetime import datetime, timedelta
from aiogram.types import CallbackQuery
from .callback_data import (
    images_callback,
    manager_callback,
    report_callback,
    orders_callback,
    calendar_callback,
    view_managers_callback,
    watch_next_callback
)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.repository.telegram_user import RepositoryTelegramUser


class FormInlineKeyboardService:

    def __init__(self, repository_telegram_user: RepositoryTelegramUser):
        self._repository_telegram_user = repository_telegram_user

    @classmethod
    async def forming_image_keyboard(cls, image_id: str, text: str, type_img: str):
        images_keyboard_assembled = InlineKeyboardMarkup(row_width=5)
        return images_keyboard_assembled.add(
            InlineKeyboardButton(
                text=f"{text}",
                callback_data=images_callback.new(
                    type=f"{type_img}",
                    data=f"{image_id}"
                )
            )
        )

    @classmethod
    async def forming_manager_keyboard(cls, image_id: str):
        manager_keyboard = InlineKeyboardMarkup(row_width=5)
        delivered_manager = InlineKeyboardButton(
            text="Доставлен💨",
            callback_data=images_callback.new(
                type="image_delivered",
                data=f"{image_id}"
            )
        )
        edit_manager = InlineKeyboardButton(
            text="Редактировать запись🖊",
            callback_data=manager_callback.new(
                type="manager_keyboard_edit",
                data=f"{image_id}"
            )
        )

        return manager_keyboard.add(delivered_manager).add(edit_manager)

    @classmethod
    async def report_keyboard_non_active(cls, report_id: str):
        report_keyboard = InlineKeyboardMarkup(row_width=5)
        deactivate_report = InlineKeyboardButton(
            text="Завершить",
            callback_data=report_callback.new(
                type="deactivate_report",
                data=f"{report_id}"
            )
        )

        return report_keyboard.add(deactivate_report)

    @classmethod
    async def report_keyboard_activate(cls, report_id: str):
        report_keyboard = InlineKeyboardMarkup(row_width=5)
        activate_report = InlineKeyboardButton(
            text="Перевести в активное",
            callback_data=report_callback.new(
                type="activate_report",
                data=f"{report_id}"
            )
        )

        return report_keyboard.add(activate_report)

    @classmethod
    async def order_details_keyboard(cls, order_id: int):
        order_details_keyboard = InlineKeyboardMarkup(row_width=5)
        return order_details_keyboard.add(
            InlineKeyboardButton(
                text="Просмотреть детали🔍",
                callback_data=orders_callback.new(
                    type="orders_details",
                    data=f"{order_id}"
                )
            )
        )

    @classmethod
    async def order_edit_keyboard(cls, order_id: int):
        order_details_keyboard = InlineKeyboardMarkup(row_width=5)
        return order_details_keyboard.add(
            InlineKeyboardButton(
                text="Редактировать заказ🖊",
                callback_data=orders_callback.new(
                    type="orders_edit",
                    data=f"{order_id}"
                )
            )
        )

    async def manager_keyboard(self):
        managers = self._repository_telegram_user.get_managers_and_super_users()
        managers_keyboard = InlineKeyboardMarkup(row_width=1)
        for manager in managers:
            managers_keyboard.add(
                InlineKeyboardButton(
                    text=f"{manager.last_name}⚪️",
                    callback_data=view_managers_callback.new(
                        type="views_managers",
                        data=f"{manager.id}"
                    )
                )
            )
        managers_keyboard.add(
            InlineKeyboardButton(
                text="Все менеджеры👨‍👨‍👦‍👦",
                callback_data=view_managers_callback.new(
                    data="all_managers",
                    type="views_managers"
                )
            )
        ).add(
            InlineKeyboardButton(
                text="Продолжить⏩",
                callback_data=view_managers_callback.new(
                    data="next",
                    type="views_managers"
                )
            )
        ).add(
            InlineKeyboardButton(
                text="Вернуться к предыдущему шагу⏪",
                callback_data=view_managers_callback.new(
                    data="back_button",
                    type="views_managers"
                )
            )
        ).add(
            InlineKeyboardButton(
                text="Отменить❌",
                callback_data=view_managers_callback.new(
                    data="cancel",
                    type="views_managers"
                )
            )
        )

        return managers_keyboard

    @classmethod
    async def watch_next_keyboard(cls, last_num, type_orders):
        watch_next = InlineKeyboardMarkup(row_width=1)
        return watch_next.add(
            InlineKeyboardButton(
                text="Смотреть дальше",
                callback_data=watch_next_callback.new(
                    data=f"{last_num}",
                    type=f"{type_orders}",
                )
            )
        )

    @classmethod
    async def start_calendar(
            cls,
            year: int = datetime.now().year,
            month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:

        inline_kb = InlineKeyboardMarkup(row_width=7)
        ignore_callback = calendar_callback.new("IGNORE", year, month, 0)
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            "<<",
            callback_data=calendar_callback.new("PREV-YEAR", year, month, 1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            f'{calendar.month_name[month]} {str(year)}',
            callback_data=ignore_callback
        ))
        inline_kb.insert(InlineKeyboardButton(
            ">>",
            callback_data=calendar_callback.new("NEXT-YEAR", year, month, 1)
        ))
        inline_kb.row()
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            inline_kb.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            inline_kb.row()
            for day in week:
                if day == 0:
                    inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
                    continue
                inline_kb.insert(InlineKeyboardButton(
                    str(day), callback_data=calendar_callback.new("DAY", year, month, day)
                ))

        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            "<", callback_data=calendar_callback.new("PREV-MONTH", year, month, day)
        ))
        inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
        inline_kb.insert(InlineKeyboardButton(
            ">", callback_data=calendar_callback.new("NEXT-MONTH", year, month, day)
        ))

        return inline_kb

    async def process_selection(self, query: CallbackQuery, data: dict) -> tuple:
        return_data = (False, None)
        temp_date = datetime(int(data['year']), int(data['month']), 1)

        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)

        if data['act'] == "DAY":
            await query.message.delete_reply_markup()
            return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']))

        if data['act'] == "PREV-YEAR":
            prev_date = datetime(int(data['year']) - 1, int(data['month']), 1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))

        if data['act'] == "NEXT-YEAR":
            next_date = datetime(int(data['year']) + 1, int(data['month']), 1)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))

        if data['act'] == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))

        if data['act'] == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))

        return return_data






