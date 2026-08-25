from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.schemas.appointment import AppointmentOut
from app.services.appointments import get_upcoming_appointments

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}/appointments", response_model=list[AppointmentOut])
def read_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return get_upcoming_appointments(db, patient_id)