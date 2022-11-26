from datetime import datetime
import enum

from sqlalchemy import (
    String,
    Column,
    Integer,
    ForeignKey,
    Enum,
    DateTime
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class Order(Base):
    __tablename__ = "order"

    class OrderStatusWork(str, enum.Enum):
        in_work = "В работе"
        partially_assembled = "Частично собран"
        assembled = "Собран"
        delivered = "Доставлен"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("telegram_user.id")
    )
    description = Column(String(2000), nullable=False)
    order_status = Column(Enum(OrderStatusWork), default=OrderStatusWork.in_work)
    created_at = Column(DateTime, default=datetime.now().date())
    user = relationship("TelegramUser")

    def __str__(self):
        return f"{self.id} {self.user}"


