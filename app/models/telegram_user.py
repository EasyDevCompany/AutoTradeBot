import enum

from sqlalchemy import String, Column, Integer, Enum, BigInteger
from app.db.base import Base


class TelegramUser(Base):
    __tablename__ = "telegram_user"

    class WorkingStatus(str, enum.Enum):
        worked = "worked"
        on_vacation = "on_vacation"
        dismissed = "dismissed"

    class PermissionStatus(str, enum.Enum):
        driver = "driver"
        financier = "financier"
        accountant = "accountant"
        manager = "manager"
        super_user = "super_user"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    username = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    patronymic = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    working_status = Column(Enum(WorkingStatus), nullable=True)
    permission_status = Column(Enum(PermissionStatus), nullable=True)

    def __str__(self):
        return f"{self.last_name}"




