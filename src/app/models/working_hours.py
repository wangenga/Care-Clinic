from datetime import date as date_
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.doctor import Doctor


class WorkingHours(Base):
    __tablename__ = "working_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    date: Mapped[date_] = mapped_column(Date, nullable=False)
    time_start: Mapped[time] = mapped_column(Time, nullable=False)
    time_end: Mapped[time] = mapped_column(Time, nullable=False)

    doctor: Mapped["Doctor"] = relationship(back_populates="working_hours")