from datetime import time

from app.database import SessionLocal
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.working_hours import WorkingHours

# day_of_week: 0=Monday ... 6=Sunday
DOCTORS = [
    {
        "name": "Dr. Aisha Njoroge",
        "hours": {
            0: (time(9, 0), time(13, 0)),
            1: (time(9, 0), time(13, 0)),
            2: (time(9, 0), time(13, 0)),
            3: (time(9, 0), time(13, 0)),
            4: (time(9, 0), time(13, 0)),
        },  # Mon–Fri mornings
    },
    {
        "name": "Dr. Brian Otieno",
        "hours": {
            0: (time(8, 0), time(16, 0)),
            1: (time(8, 0), time(16, 0)),
            2: (time(8, 0), time(16, 0)),
            3: (time(8, 0), time(16, 0)),
            4: (time(8, 0), time(16, 0)),
        },  # Mon–Fri full day
    },
    {
        "name": "Dr. Grace Wanjiru",
        "hours": {
            1: (time(10, 0), time(14, 0)),
            3: (time(10, 0), time(14, 0)),
            5: (time(9, 0), time(12, 0)),
        },  # Tue, Thu afternoons + Sat morning
    },
    {
        "name": "Dr. Kevin Mutua",
        "hours": {
            0: (time(14, 0), time(18, 0)),
            2: (time(14, 0), time(18, 0)),
            4: (time(14, 0), time(18, 0)),
        },  # Mon, Wed, Fri afternoons/evenings
    },
    {
        "name": "Dr. Fatuma Hassan",
        "hours": {
            5: (time(8, 0), time(13, 0)),
            6: (time(8, 0), time(13, 0)),
        },  # Weekends only
    },
]


def seed():
    db = SessionLocal()
    try:
        patient = db.query(Patient).first()
        if patient is None:
            patient = Patient(name="John Mwangi")
            db.add(patient)
            db.flush()
            print(f"Seeded patient id={patient.id}")

        for doctor_data in DOCTORS:
            doctor = db.query(Doctor).filter_by(name=doctor_data["name"]).first()
            if doctor is None:
                doctor = Doctor(name=doctor_data["name"])
                db.add(doctor)
                db.flush()
                print(f"Seeded doctor id={doctor.id}: {doctor.name}")

            for day, (start, end) in doctor_data["hours"].items():
                exists = (
                    db.query(WorkingHours)
                    .filter_by(doctor_id=doctor.id, day_of_week=day)
                    .first()
                )
                if not exists:
                    db.add(WorkingHours(
                        doctor_id=doctor.id,
                        day_of_week=day,
                        time_start=start,
                        time_end=end,
                    ))

        db.commit()
        print("Seeding complete.")

        for doctor in db.query(Doctor).all():
            print(f"  id={doctor.id}: {doctor.name}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()