from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.appointment import (
    AppointmentCancel,
    AppointmentCreate,
    AppointmentOut,
    AppointmentReschedule,
)
from app.services.appointments import (
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentOut, status_code=201)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    if db.query(Patient).filter(Patient.id == payload.patient_id).first() is None:
        raise HTTPException(status_code=404, detail="Patient not found.")
    if db.query(Doctor).filter(Doctor.id == payload.doctor_id).first() is None:
        raise HTTPException(status_code=404, detail="Doctor not found.")

    return book_appointment(
        db, payload.patient_id, payload.doctor_id, payload.date, payload.time_start
    )


@router.patch("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel(appointment_id: int, payload: AppointmentCancel, db: Session = Depends(get_db)):
    return cancel_appointment(db, appointment_id, payload.reason)


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentOut)
def reschedule(
    appointment_id: int, payload: AppointmentReschedule, db: Session = Depends(get_db)
):
    return reschedule_appointment(db, appointment_id, payload.date, payload.time_start)