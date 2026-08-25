from datetime import date, time

from pydantic import BaseModel, ConfigDict


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date: date
    time_start: time


class AppointmentCancel(BaseModel):
    reason: str

class AppointmentReschedule(BaseModel):
    date: date
    time_start: time

class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    date: date
    time_start: time
    end_time: time
    status: str
    cancelation_reason: str | None = None

class AvailabilityOut(BaseModel):
    doctor_id: int
    date: date
    available_slots: list[time]