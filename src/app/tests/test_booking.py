

def test_book_appointment_success(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date = doctor_and_patient["date"]

    response = client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date),
        "time_start": "09:00:00",
    })

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "booked"
    assert body["end_time"] == "09:30:00"


def test_double_booking_rejected(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date = doctor_and_patient["date"]
    payload = {
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date),
        "time_start": "09:00:00",
    }

    first = client.post("/appointments", json=payload)
    assert first.status_code == 201

    second = client.post("/appointments", json=payload)
    assert second.status_code == 409


def test_slot_outside_working_hours_rejected(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date = doctor_and_patient["date"]

    response = client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date),
        "time_start": "08:00:00",
    })

    assert response.status_code == 400
    assert "working hours" in response.json()["detail"].lower()


def test_misaligned_slot_rejected(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date = doctor_and_patient["date"]

    response = client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date),
        "time_start": "09:15:00",
    })

    assert response.status_code == 400
    assert "30-minute boundary" in response.json()["detail"]


def test_cancel_appointment(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date = doctor_and_patient["date"]

    booked = client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date),
        "time_start": "09:00:00",
    }).json()

    response = client.patch(f"/appointments/{booked['id']}/cancel", json={"reason": "test"})

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    assert response.json()["cancellation_reason"] == "test"


def test_cancel_already_cancelled_rejected(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date = doctor_and_patient["date"]

    booked = client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date),
        "time_start": "09:00:00",
    }).json()

    client.patch(f"/appointments/{booked['id']}/cancel", json={"reason": "test"})
    second = client.patch(f"/appointments/{booked['id']}/cancel", json={"reason": "again"})

    assert second.status_code == 400


def test_reschedule_success(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date = doctor_and_patient["date"]

    booked = client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date),
        "time_start": "09:00:00",
    }).json()

    response = client.patch(f"/appointments/{booked['id']}/reschedule", json={
        "date": str(date),
        "time_start": "10:00:00",
    })

    assert response.status_code == 200
    assert response.json()["time_start"] == "10:00:00"


def test_reschedule_cancelled_rejected(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date = doctor_and_patient["date"]

    booked = client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date),
        "time_start": "09:00:00",
    }).json()

    client.patch(f"/appointments/{booked['id']}/cancel", json={"reason": "test"})

    response = client.patch(f"/appointments/{booked['id']}/reschedule", json={
        "date": str(date),
        "time_start": "10:00:00",
    })

    assert response.status_code == 400



# --- Day-of-week working hours ---

def test_availability_empty_on_non_working_day(client, two_doctors_and_patient):
    doctor_a = two_doctors_and_patient["doctor_a"]
    # 2099-01-05 is a Wednesday; doctor_a only works Tuesdays
    response = client.get(f"/doctors/{doctor_a.id}/availability?date=2099-01-05")

    assert response.status_code == 200
    assert response.json()["available_slots"] == []


def test_availability_has_slots_on_working_day(client, two_doctors_and_patient):
    doctor_a = two_doctors_and_patient["doctor_a"]
    # 2099-01-06 is a Tuesday
    response = client.get(f"/doctors/{doctor_a.id}/availability?date=2099-01-06")

    assert response.status_code == 200
    assert "09:00:00" in response.json()["available_slots"]


def test_availability_empty_for_doctor_with_no_working_hours(client, two_doctors_and_patient):
    doctor_b = two_doctors_and_patient["doctor_b"]
    response = client.get(f"/doctors/{doctor_b.id}/availability?date=2099-01-06")

    assert response.status_code == 200
    assert response.json()["available_slots"] == []


# --- Friendly date-format error ---

def test_availability_malformed_date_returns_helpful_message(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    response = client.get(f"/doctors/{doctor.id}/availability?date=not-a-date")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("YYYY-MM-DD" in err["msg"] for err in detail)


# --- Reschedule into a conflicting slot ---

def test_reschedule_into_conflict_rejected(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date_ = doctor_and_patient["date"]

    client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date_),
        "time_start": "09:00:00",
    }).json()

    second = client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date_),
        "time_start": "10:00:00",
    }).json()

    # try to move the second appointment into the first one's slot
    response = client.patch(f"/appointments/{second['id']}/reschedule", json={
        "date": str(date_),
        "time_start": "09:00:00",
    })

    assert response.status_code == 409


# --- Bonus endpoint: patient's upcoming appointments ---

def test_patient_appointments_lists_booked_upcoming(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date_ = doctor_and_patient["date"]

    client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date_),
        "time_start": "09:00:00",
    })

    response = client.get(f"/patients/{patient.id}/appointments")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["status"] == "booked"


def test_patient_appointments_excludes_cancelled(client, doctor_and_patient):
    doctor = doctor_and_patient["doctor"]
    patient = doctor_and_patient["patient"]
    date_ = doctor_and_patient["date"]

    booked = client.post("/appointments", json={
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "date": str(date_),
        "time_start": "09:00:00",
    }).json()

    client.patch(f"/appointments/{booked['id']}/cancel", json={"reason": "test"})

    response = client.get(f"/patients/{patient.id}/appointments")

    assert response.status_code == 200
    assert response.json() == []


def test_patient_appointments_404_for_missing_patient(client, doctor_and_patient):
    response = client.get("/patients/999/appointments")
    assert response.status_code == 404