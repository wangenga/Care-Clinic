from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import appointments, doctors
from app.services.exceptions import BookingError

app = FastAPI(title="Care Clinic Booking System")

app.include_router(doctors.router)
app.include_router(appointments.router)


@app.exception_handler(BookingError)
def booking_error_handler(request: Request, exc: BookingError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(RequestValidationError)
def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    for error in errors:
        field_name = error["loc"][-1] if error["loc"] else None
        if field_name == "date" and error["type"].startswith(("date_", "datetime_")):
            error["msg"] = "Invalid date format. Expected YYYY-MM-DD (e.g. 2026-08-30)."
    return JSONResponse(status_code=422, content={"detail": errors})


@app.get("/health")
def health_check():
    return {"status": "ok"}