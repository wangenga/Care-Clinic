from datetime import date as date_
from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.working_hours import WorkingHours
from app.services.exceptions import (
    AppointmentAlreadyCancelledError,
    AppointmentInPastError,
    AppointmentNotFoundError,
    DoctorNotAvailableError,
    InvalidSlotAlignmentError,
    SlotAlreadyBookedError,
    SlotInPastError,
    SlotWithinBufferError,
)

SLOT_DURATION_MINUTES = 30
BOOKING_BUFFER = timedelta(hours=1)


def _generate_slots(time_start: time, time_end: time) -> list[time]:
    """All 30-minute slot start times that fully fit within [time_start, time_end)."""
    slots = []
    current = datetime.combine(date_.today(), time_start) # noqa: DTZ011 — single-timezone assumption
    end = datetime.combine(date_.today(), time_end) # noqa: DTZ011 — single-timezone assumption

    while current + timedelta(minutes=SLOT_DURATION_MINUTES) <= end:
        slots.append(current.time())
        current += timedelta(minutes=SLOT_DURATION_MINUTES)

    return slots

def _slot_end(time_start: time) -> time:
    dummy = datetime.combine(date_.today(), time_start) + timedelta( # noqa: DTZ011 — single-timezone assumption, see README
        minutes=SLOT_DURATION_MINUTES
    )
    return dummy.time()


def validate_not_in_past(date: date_, time_start: time) -> None:
    slot_start = datetime.combine(date, time_start)
    if slot_start < datetime.now():  # noqa
        raise SlotInPastError("Cannot book a slot in the past.")


def validate_not_within_buffer(date: date_, time_start: time) -> None:
    slot_start = datetime.combine(date, time_start)
    if slot_start < datetime.now() + BOOKING_BUFFER:  # noqa
        raise SlotWithinBufferError(
            "Cannot book a slot within 1 hour of the current time."
        )


def validate_within_working_hours(
    db: Session, doctor_id: int, date: date_, time_start: time, end_time: time
) -> None:
    working_hours = (
        db.query(WorkingHours)
        .filter(WorkingHours.doctor_id == doctor_id, WorkingHours.date == date)
        .first()
    )
    if working_hours is None:
        raise DoctorNotAvailableError(
            "Doctor has no working hours set for this date."
        )

    if time_start < working_hours.time_start or end_time > working_hours.time_end:
        raise DoctorNotAvailableError(
            "Requested slot falls outside the doctor's working hours."
        )

    valid_slots = _generate_slots(working_hours.time_start, working_hours.time_end)
    if time_start not in valid_slots:
        raise InvalidSlotAlignmentError(
            "Appointments must start on a 30-minute boundary (e.g. 09:00, 09:30)."
        )


def validate_slot_available(
    db: Session,
    doctor_id: int,
    date: date_,
    time_start: time,
    exclude_appointment_id: int | None = None,
) -> None:
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == date,
        Appointment.time_start == time_start,
        Appointment.status == "booked",
    )
    if exclude_appointment_id is not None:
        query = query.filter(Appointment.id != exclude_appointment_id)

    if query.first() is not None:
        raise SlotAlreadyBookedError("This slot is already booked.")


def validate_new_booking_slot(
    db: Session,
    doctor_id: int,
    date: date_,
    time_start: time,
    exclude_appointment_id: int | None = None,
) -> time:
    """Runs all checks required for a fresh booking and also used by
    reschedule for the new slot.Returns the computed end_time on success."""
    end_time = _slot_end(time_start)
    validate_not_in_past(date, time_start)
    validate_not_within_buffer(date, time_start)
    validate_within_working_hours(db, doctor_id, date, time_start, end_time)
    validate_slot_available(db, doctor_id, date, time_start, exclude_appointment_id)
    return end_time


def get_appointment_or_404(db: Session, appointment_id: int) -> Appointment:
    appointment = (
        db.query(Appointment).filter(Appointment.id == appointment_id).first()
    )
    if appointment is None:
        raise AppointmentNotFoundError("Appointment not found.")
    return appointment


def validate_not_already_cancelled(appointment: Appointment) -> None:
    if appointment.status == "cancelled":
        raise AppointmentAlreadyCancelledError("Appointment is already cancelled.")


def validate_appointment_not_in_past(appointment: Appointment) -> None:
    """Guards against cancelling or rescheduling an appointment whose
    original time has already passed — see README Decision 6."""
    original_start = datetime.combine(appointment.date, appointment.time_start)
    if original_start < datetime.now():  # noqa
        raise AppointmentInPastError(
            "Cannot modify an appointment that has already passed."
        )