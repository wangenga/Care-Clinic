from datetime import date, time

from pydantic import BaseModel, ConfigDict, field_validator


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date: date
    time_start: time

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patient_id": 0,
                "doctor_id": 0,
                "date": "2026-08-30",
                "time_start": "14:00:00",
            }
        }
    )
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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2026-08-30",
                "time_start": "10:00:00",
            }
        }
    )
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
    cancellation_reason: str | None = None

class AvailabilityOut(BaseModel):
    doctor_id: int
    date: date
    available_slots: list[time]