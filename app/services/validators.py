import re

from loguru import logger
from aiogram.utils.markdown import hbold
from phonenumbers import format_number, parse
from phonenumbers import PhoneNumberFormat
from phonenumbers.phonenumberutil import NumberParseException
from itertools import groupby


class ValidateInformationService:

    @classmethod
    async def validate_phone_number(cls, phone_number: str) -> str:
        error_message = "⛔️Неправильный формат номера телефона.\n" \
                        "Проверьте правильность написания и отправьте боту снова:\n\n" \
                        f"{hbold(f'Отправленный нмер телефона: {phone_number}')}"

        if not re.compile("^[0-9+().,-]+$").search(string=phone_number) is not None:
            return error_message

        try:
            number = parse(number=phone_number, region='RU')
            valid_number = format_number(number, PhoneNumberFormat.E164)

            if len(valid_number) < 12:
                return error_message

        except NumberParseException:
            return error_message

        return valid_number

    @classmethod
    async def delete_copy_manager_id(cls, managers: str) -> list:
        manager_list = []
        clear_manager_list = [manager_id for manager_id in groupby(managers.split())]
        for mng in clear_manager_list:
            manager_list.append(mng[0])
        logger.info(manager_list)

        return manager_list

    @classmethod
    async def validate_input_info(
            cls,
            data: str,
            type_view: str,
            date: str,
            date_start: str,
            date_end: str,
    ) -> str:
        answer = ""
        if data == "cancel":
            return "cancel"

        elif data == "back_button":
            return "back_button"

        if date:
            answer = "{type_view}_{managers}_{date}".format(
                type_view=type_view,
                managers=data,
                date="one_date"
            )

        elif date_end and date_start:
            answer = "{type_view}_{managers}_{date}".format(
                type_view=type_view,
                managers=data,
                date="two_date"
            )

        return answer

    @classmethod
    async def validate_date(cls, date_end, date_start):
        if date_start <= date_end:
            return True


# answers:
# 1) order_all_managers_one_date
# 2) order_all_managers_two_date
# 3) report_all_managers_one_date
# 4) report_all_managers_two_date
# 5) order_next_one_date
# 6) order_next_two_date
# 7) report_next_one_date
# 8) report_next_two_date




