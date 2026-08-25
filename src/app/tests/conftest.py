from datetime import date, time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.working_hours import WorkingHours

engine = create_engine(settings.test_database_url)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture()
def doctor_and_patient(db_session):
    doctor = Doctor(name="Dr. Test")
    patient = Patient(name="Test Patient")
    db_session.add_all([doctor, patient])
    db_session.flush()

    test_date = date(2099, 1, 5)  # a Tuesday
    working_hours = WorkingHours(
        doctor_id=doctor.id,
        day_of_week=test_date.weekday(),
        time_start=time(9, 0),
        time_end=time(13, 0),
    )
    db_session.add(working_hours)
    db_session.commit()

    return {"doctor": doctor, "patient": patient, "date": test_date}

@pytest.fixture()
def two_doctors_and_patient(db_session):
    doctor_a = Doctor(name="Dr. A")
    doctor_b = Doctor(name="Dr. B")
    patient = Patient(name="Test Patient")
    db_session.add_all([doctor_a, doctor_b, patient])
    db_session.flush()

    # doctor_a works Tuesdays only; doctor_b works no days at all
    db_session.add(WorkingHours(
        doctor_id=doctor_a.id, day_of_week=1,  # Tuesday
        time_start=time(9, 0), time_end=time(13, 0),
    ))
    db_session.commit()

    return {"doctor_a": doctor_a, "doctor_b": doctor_b, "patient": patient}