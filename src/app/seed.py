from datetime import time

from app.database import SessionLocal
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.working_hours import WorkingHours

PATIENTS = [
    "John Mwangi",
    "Sarah Wambui",
    "David Ochieng",
]

# day_of_week: 0=Monday ... 6=Sunday
DOCTORS = [
    {
        "name": "Dr. Aisha Njoroge",
        "hours": {
            0: (time(8, 0), time(17, 0)),
            1: (time(8, 0), time(17, 0)),
            2: (time(8, 0), time(17, 0)),
            3: (time(8, 0), time(17, 0)),
            4: (time(8, 0), time(17, 0)),
        },  # Mon–Fri mornings
    },
    {
        "name": "Dr. Brian Otieno",
        "hours": {
            1: (time(13, 0), time(23, 0)),
            2: (time(13, 0), time(23, 0)),
            3: (time(13, 0), time(23, 0)),
            4: (time(13, 0), time(23, 0)),
            5: (time(13, 0), time(23, 0)),
        },  #  Tue-Sat Evening
    },
    {
        "name": "Dr. Grace Wanjiru",
        "hours": {
            2: (time(8, 0), time(17, 0)),
            3: (time(8, 0), time(17, 0)),
            4: (time(8, 0), time(17, 0)),
            5: (time(8, 0), time(17, 0)),
            6: (time(8, 0), time(17, 0)),
        },  # Wed-Sun Morning
    },
    {
        "name": "Dr. Kevin Mutua",
        "hours": {
            2: (time(1, 0), time(10, 0)),
            3: (time(1, 0), time(10, 0)),
            4: (time(1, 0), time(10, 0)),
            5: (time(1, 0), time(10, 0)),
            6: (time(1, 0), time(10, 0)),
        },  # Wed-Sun early mornings
    },
    {
        "name": "Dr. Fatuma Hassan",
        "hours": {
            0: (time(1, 0), time(10, 0)),
            1: (time(1, 0), time(10, 0)),
            2: (time(1, 0), time(10, 0)),
            3: (time(1, 0), time(10, 0)),
            4: (time(1, 0), time(10, 0)),
        },  # Mon–Fri early mornings
    },
]


def seed():
    db = SessionLocal()
    try:
        # Fixed indentation here
        for patient_name in PATIENTS:
            patient = db.query(Patient).filter_by(name=patient_name).first()
            if patient is None:
                patient = Patient(name=patient_name)
                db.add(patient)
                db.flush()
                print(f"Seeded patient id={patient.id}: {patient.name}")

        for doctor_data in DOCTORS:
            doctor = db.query(Doctor).filter_by(name=doctor_data["name"]).first()
            if doctor is None:
                doctor = Doctor(name=doctor_data["name"])
                db.add(doctor)
                db.flush()
                print(f"Seeded doctor id={doctor.id}: {doctor.name}")

            for day, (start, end) in doctor_data["hours"].items():
                existing_hours = (
                    db.query(WorkingHours)
                    .filter_by(doctor_id=doctor.id, day_of_week=day)
                    .first()
                )
                
                if not existing_hours:
                    db.add(WorkingHours(
                        doctor_id=doctor.id,
                        day_of_week=day,
                        time_start=start,
                        time_end=end,
                    ))
                else:
                    # Updates existing schedules in the database to match the new shifts
                    existing_hours.time_start = start
                    existing_hours.time_end = end

        db.commit()
        print("Seeding complete.")
        
        print("\nCurrent Patients in Database:")
        for patient in db.query(Patient).all():
            print(f"  id={patient.id}: {patient.name}")

        print("\nCurrent Doctors in Database:")
        for doctor in db.query(Doctor).all():
            print(f"  id={doctor.id}: {doctor.name}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()