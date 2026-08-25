from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import appointments, doctors
from app.services.exceptions import BookingError

app = FastAPI(title="Care Clinic Booking System")

app.include_router(doctors.router)
app.include_router(appointments.router)

@app.exception_handler(BookingError)
def booking_error_handler(request: Request, exc: BookingError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

@app.get("/health")
def health_check():
    return {"status": "ok"}