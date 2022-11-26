import enum
import datetime

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


class Images(Base):
    __tablename__ = "images"

    class ImageStatus(str, enum.Enum):
        in_work = "В работе"
        assembled = "Собран"
        delivered = "Доставлен"

    id = Column(Integer, primary_key=True)
    order_id = Column(
        Integer,
        ForeignKey("order.id")
    )
    image = Column(String(100))
    image_description = Column(String(200), nullable=True)
    image_status = Column(Enum(ImageStatus), default=ImageStatus.in_work)
    user_id = Column(Integer, ForeignKey("telegram_user.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("TelegramUser")
    order = relationship("Order")

    def __str__(self):
        return f"{self.id} {self.user_id} {self.order_id}"
