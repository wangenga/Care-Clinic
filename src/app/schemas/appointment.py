from datetime import date, time

from pydantic import BaseModel, ConfigDict, field_validator


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date: date
    time_start: time

    @field_validator("time_start")
    @classmethod
    def reject_tz_aware(cls, v: time) -> time:
        if v.tzinfo is not None:
            raise ValueError(
                "time_start must not include timezone info — only local clinic time is supported."
            )
        return v

class AppointmentCancel(BaseModel):
    reason: str

class AppointmentReschedule(BaseModel):
    date: date
    time_start: time

    @field_validator("time_start")
    @classmethod
    def reject_tz_aware(cls, v: time) -> time:
        if v.tzinfo is not None:
            raise ValueError(
                "time_start must not include timezone info — only local clinic time is supported."
            )
        return v

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