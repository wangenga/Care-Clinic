from datetime import date, time

from app.database import SessionLocal
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.working_hours import WorkingHours


def seed():
    db = SessionLocal()
    try:
        doctor = db.query(Doctor).first()
        if doctor is None:
            doctor = Doctor(name="Dr. Aisha Njoroge")
            db.add(doctor)
            db.flush()
            print(f"Seeded doctor id={doctor.id}")

        patient = db.query(Patient).first()
        if patient is None:
            patient = Patient(name="John Mwangi")
            db.add(patient)
            db.flush()
            print(f"Seeded patient id={patient.id}")

        future_date = date(2026, 8, 30)
        if not db.query(WorkingHours).filter_by(doctor_id=doctor.id, date=future_date).first():
            db.add(WorkingHours(
                doctor_id=doctor.id, date=future_date,
                time_start=time(9, 0), time_end=time(13, 0),
            ))
            print(f"Seeded working hours for {future_date}")

        today = date.today()  # noqa: DTZ011 — single-timezone assumption, see README
        if not db.query(WorkingHours).filter_by(doctor_id=doctor.id, date=today).first():
            db.add(WorkingHours(
                doctor_id=doctor.id, date=today,
                time_start=time(0, 0), time_end=time(23, 59),
            ))
            print(f"Seeded working hours for today ({today}), full day")

        db.commit()
        print(f"Doctor id: {doctor.id}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()