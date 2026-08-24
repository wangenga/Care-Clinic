from fastapi import FastAPI

app = FastAPI(title="Care Clinic Booking System")

@app.get("/health")
def health_check():
    return {"status": "ok"}