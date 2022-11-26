from datetime import datetime

from sqlalchemy import (
    String,
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Boolean
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("telegram_user.id")
    )
    report = Column(String(3000))
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now().date())
    user = relationship("TelegramUser")

    def __str__(self):
        return f"{self.id} {self.user_id}"
