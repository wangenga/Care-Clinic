from datetime import date as date_
from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.working_hours import WorkingHours
from app.services.validation import BOOKING_BUFFER, SLOT_DURATION_MINUTES


def _generate_slots(time_start: time, time_end: time) -> list[time]:
    """All 30-minute slot start times that fully fit within [time_start, time_end)."""
    slots = []
    current = datetime.combine(date_.today(), time_start) # noqa: DTZ011 — single-timezone assumption
    end = datetime.combine(date_.today(), time_end) # noqa: DTZ011 — single-timezone assumption

    while current + timedelta(minutes=SLOT_DURATION_MINUTES) <= end:
        slots.append(current.time())
        current += timedelta(minutes=SLOT_DURATION_MINUTES)

    return slots


def get_available_slots(db: Session, doctor_id: int, date: date_) -> list[time]:
    working_hours = (
        db.query(WorkingHours)
        .filter(WorkingHours.doctor_id == doctor_id, WorkingHours.date == date)
        .first()
    )
    if working_hours is None:
        return []  # doctor has no hours set for this date — not an error, just nothing to show

    all_slots = _generate_slots(working_hours.time_start, working_hours.time_end)

    booked_times = {
        appt.time_start
        for appt in db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date,
            Appointment.status == "booked",
        )
        .all()
    }

    now = datetime.now()  # noqa: DTZ005 — single-timezone assumption, see README
    cutoff = now + BOOKING_BUFFER

    available = [
        slot
        for slot in all_slots
        if slot not in booked_times
        and (date > now.date() or datetime.combine(date, slot) >= cutoff)
    ]

    return available