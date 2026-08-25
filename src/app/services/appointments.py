from datetime import date as date_
from datetime import datetime, time

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.services.exceptions import SlotAlreadyBookedError
from app.services.validation import (
    get_appointment_or_404,
    validate_appointment_not_in_past,
    validate_new_booking_slot,
    validate_not_already_cancelled,
)


def book_appointment(
    db: Session, patient_id: int, doctor_id: int, date: date_, time_start: time
) -> Appointment:
    end_time = validate_new_booking_slot(db, doctor_id, date, time_start)

    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        date=date,
        time_start=time_start,
        end_time=end_time,
        status="booked",
    )
    db.add(appointment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # backstop against the race condition our proactive check can't fully close
        raise SlotAlreadyBookedError("This slot was just booked by someone else.")

    db.refresh(appointment)
    return appointment


def cancel_appointment(db: Session, appointment_id: int, reason: str) -> Appointment:
    appointment = get_appointment_or_404(db, appointment_id)
    validate_not_already_cancelled(appointment)
    validate_appointment_not_in_past(appointment)

    appointment.status = "cancelled"
    appointment.cancellation_reason = reason
    db.commit()
    db.refresh(appointment)
    return appointment


def reschedule_appointment(
    db: Session, appointment_id: int, new_date: date_, new_time_start: time
) -> Appointment:
    appointment = get_appointment_or_404(db, appointment_id)
    validate_not_already_cancelled(appointment)
    validate_appointment_not_in_past(appointment)

    new_end_time = validate_new_booking_slot(
        db,
        doctor_id=appointment.doctor_id,
        date=new_date,
        time_start=new_time_start,
        exclude_appointment_id=appointment.id,
    )

    appointment.date = new_date
    appointment.time_start = new_time_start
    appointment.end_time = new_end_time
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise SlotAlreadyBookedError("This slot was just booked by someone else.")

    db.refresh(appointment)
    return appointment

def get_upcoming_appointments(db: Session, patient_id: int) -> list[Appointment]:
    today = date_.today()  # noqa: DTZ011 — single-timezone assumption, see README
    now = datetime.now()  # noqa: DTZ005 — single-timezone assumption, see README

    candidates = (
        db.query(Appointment)
        .filter(
            Appointment.patient_id == patient_id,
            Appointment.status == "booked",
            Appointment.date >= today,
        )
        .order_by(Appointment.date, Appointment.time_start)
        .all()
    )

    # Exclude today's appointments whose time has already passed —
    # the date >= today filter alone isn't enough for same-day precision.
    return [
        appt
        for appt in candidates
        if appt.date > today or datetime.combine(appt.date, appt.time_start) >= now
    ]