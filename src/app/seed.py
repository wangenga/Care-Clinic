from datetime import date, time

from app.database import SessionLocal
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.working_hours import WorkingHours


def seed():
    db = SessionLocal()
    try:
        # Avoid duplicate seeding on repeat runs
        if db.query(Doctor).first() is not None:
            print("Data already seeded, skipping.")
            return

        doctor = Doctor(name="Dr. Aisha Njoroge")
        patient = Patient(name="John Mwangi")
        db.add_all([doctor, patient])
        db.flush()  # assigns IDs without committing yet

        working_hours = WorkingHours(
            doctor_id=doctor.id,
            date=date(2026, 8, 30),
            time_start=time(9, 0),
            time_end=time(13, 0),
        )
        db.add(working_hours)
        db.commit()

        print(f"Seeded doctor id={doctor.id}, patient id={patient.id}")
        print(f"Working hours: {working_hours.date} {working_hours.time_start}-{working_hours.time_end}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()