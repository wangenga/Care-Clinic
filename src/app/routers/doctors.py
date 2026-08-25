from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.doctor import Doctor
from app.schemas.appointment import AvailabilityOut
from app.services.availability import get_available_slots

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/{doctor_id}/availability", response_model=AvailabilityOut)
def read_doctor_availability(
    doctor_id: int,
    date: date,
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found.")

    available_slots = get_available_slots(db, doctor_id, date)

    return AvailabilityOut(
        doctor_id=doctor_id,
        date=date,
        available_slots=available_slots,
    )