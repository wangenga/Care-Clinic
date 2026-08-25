from fastapi import FastAPI

from app.routers import doctors

app = FastAPI(title="Care Clinic Booking System")

app.include_router(doctors.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}