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