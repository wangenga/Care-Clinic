# Care Clinic Booking System


**Interactive API docs:** https://care-clinic-642962786433.us-central1.run.app/docs

## Goals

Ensure smooth booking of appointments at our clinic.

## Scope

- The clinic has 5 doctors.
- A patient can book an appointment online.
- A patient can see a doctor's free slots on a given day.
- A patient can pick a slot and book it.
- A slot is not available after being booked.
- A patient can cancel or reschedule an appointment.
- A patient cannot reschedule a cancelled appointment.
- A slot becomes available again after a cancellation or reschedule.
- A patient cannot book an appointment starting less than one hour from now.
- A doctor's working hours cannot be edited through the API once set.
- A patient can view their own upcoming, booked appointments, sorted by date.

## Constraints

- Doctors cannot be added through the system; this is handled manually.
- The one-hour booking buffer cannot be overridden by a doctor, even if the doctor is open to appointments within that window.
- There is no authentication in this version.
- The patient and clinic are assumed to be in the same timezone.

## Key Stakeholders

- Doctor
- Patient

## High-Level Flow

Patient actions: book appointment, cancel appointment, reschedule appointment, view appointments.
Doctor actions: view schedule.

**Book appointment:**
select doctor → select date → view available slots → select a slot → verify booking → success


**Cancel appointment:**
view appointments → select an appointment → verify cancellation → success

**Reschedule appointment:**
view appointments → select an appointment → verify reschedule → select new date → view available slots → select a slot → verify new booking → success

Cancel and reschedule follow the same shape as the last three steps of the booking flow above (select → confirm → success), just starting from an existing appointment instead of a fresh doctor/date selection.

**View appointments:**
select view appointments → view list of own upcoming, booked appointments, sorted by date

This is also the entry point for cancel and reschedule — a patient sees their appointments here first, then picks one to act on.

## Database Schema

**Patient**
- `patientID` (PK)
- `name`

**Doctor**
- `doctorID` (PK)
- `name`

**WorkingHours**
- `workingHoursID` (PK)
- `doctorID` (FK)
- `dayOfWeek` (0 = Monday ... 6 = Sunday)
- `timeStart`
- `timeEnd`

**Appointment**
- `appointmentID` (PK)
- `patientID` (FK)
- `doctorID` (FK)
- `date`
- `timeStart`
- `endTime`
- `status` (booked, cancelled, rescheduled)
- `cancellationReason`

### Entity–Relationship

- A patient can have 0 or many appointments.
- An appointment belongs to exactly 1 patient and exactly 1 doctor.
- A doctor can have 0 or many appointments.
- A doctor can have up to one working-hours record per day of the week (Monday–Sunday), enforced by a unique constraint on `(doctorID, dayOfWeek)`.
- Each working-hours record belongs to exactly 1 doctor.

```mermaid
erDiagram
  DOCTOR ||--o{ WORKINGHOURS : defines
  DOCTOR ||--o{ APPOINTMENT : has
  PATIENT ||--o{ APPOINTMENT : books
  PATIENT {
    int patientID PK
    string name
  }
  DOCTOR {
    int doctorID PK
    string name
  }
  WORKINGHOURS {
    int workingHoursID PK
    int doctorID FK
    date date
    time timeStart
    time timeEnd
  }
  APPOINTMENT {
    int appointmentID PK
    int patientID FK
    int doctorID FK
    date date
    time timeStart
    time endTime
    string status
    string cancellationReason
  }
```

## Components
 
- **API layer** — exposes the REST endpoints (booking, availability, cancel, reschedule, view appointments) and handles request/response shape and status codes.
- **Availability engine** — computes a doctor's free 30-minute slots for a given date by taking their `WorkingHours` for that date and subtracting any slots already covered by a `booked` `Appointment`.
- **Validation layer** — enforces the booking rules before a write ever hits the database: slot falls within working hours, not in the past, not within the one-hour buffer, and not already taken.
- **Persistence layer** — the database and its constraints, including the partial unique index on `(doctorID, date, timeStart)` that prevents double-booking at the data layer as a last line of defense, independent of the validation layer above.

## Design Decisions

1. **Doctors cannot manage their own working hours through the API.**
   Allowing edits would require handling the case where a doctor changes their hours after a patient has already booked outside the new timeframe — that needs more time to implement properly, so it's deferred to v2.

2. **Chose a unique DB constraint on `Appointment` table's `(doctorID, date, timeStart)` over transaction-based row locking for booking validation.**
   A separate table of precomputed available slots would introduce write contention and risk deadlocks under high traffic as the clinic grows. This means cancellation and rescheduling must be handled carefully: the constraint is implemented as a partial unique index (unique only where `status = 'booked'`), so a slot becomes bookable again as soon as its appointment is cancelled or rescheduled.

3. **Cancelled and rescheduled appointments free up their slot.** Their rows remain in the `Appointment` table for history, but the slot itself is shown as available again.

4. **A reschedule updates the existing appointment row** rather than creating a new one — meaning reschedule history isn't preserved in v1.

5. **Slots within the next hour are filtered out at generation time**, rather than being shown and then rejected at booking time. This keeps the experience smoother — patients only ever see slots they can actually book.

6. **Cancelling and rescheduing of past appointments.**
   Without this check, a patient could reschedule or cancel an appointment that already happened — which doesn't reflect reality and could be used to manipulate historical booking data.I chose not to introduce a status "completed" that would require deciding who or what transitions an appointment out of booked once its time passes. Rather I choose a simple fix, checking the appointment's own date/time against "now" directly inside cancel and reschedule validation — covers the actual risk

7. **Working hours are modeled per day of the week (`dayOfWeek`, 0–6), not per specific date.** 
    The original per-date design meant a doctor's availability would only exist as far into the future as someone manually seeded rows — directly at odds with "we're starting small but want to grow." A recurring weekly schedule is seeded once per doctor and holds indefinitely. The trade-off: this version can't express one-off exceptions (a public holiday, a doctor's single sick day) — that requires a separate overrides/exceptions table layered on top, noted under V2 rather than built now.
8. **Malformed date input returns a specific, actionable error message**
    (e.g. "Invalid date format. Expected YYYY-MM-DD.") rather than Pydantic's default generic parsing error. This is handled via a global `RequestValidationError` handler that rewrites messages for `date`-typed fields, so the fix applies consistently across the availability query parameter and both appointment request bodies rather than being patched endpoint-by-endpoint.

## V2 Improvements

1. Allow doctors to make adjustments to their working hours.
2. If a doctor changes working hours after a patient has already booked: if the doctor can still accommodate the existing appointment, keep it and shift the remaining slots; otherwise, notify the patient and prompt them to reschedule.
3. Add an urgency column to appointments.
4. Introduce a `completed` status transitioned automatically once an appointment's time passes, replacing the direct date/time checks in cancel and reschedule with a single status check.
5. Support one-off exceptions to a doctor's recurring weekly schedule (e.g. a public holiday or a single day off), likely via a separate date-specific overrides table that takes precedence over the weekly `WorkingHours` record when present.

## Prerequisites
 
- [uv](https://docs.astral.sh/uv/) (Python package/project manager)
- [Docker](https://www.docker.com/) and Docker Compose (for local Postgres)
- Python 3.12+ (uv will manage this automatically via `uv sync` if not already installed)
## How to Run Locally
 
1. **Clone the repo and enter the project directory:**
```bash
   git clone <repo-url>
   cd Care-Clinic
```
 
2. **Start Postgres locally via Docker Compose:**
```bash
   docker compose up -d
```
   This starts a Postgres 16 container on `localhost:5432` with the credentials defined in `docker-compose.yml`.
 
3. **Create a `.env` file** in the project root (see `.env.example` for the required variables):

 
4. **Create the test database** (only needed once, for running the test suite):
```bash
   docker exec -it care-clinic-db-1 psql -U care_clinic -d care_clinic -c "CREATE DATABASE care_clinic_test;"
```
 
5. **Install dependencies:**
```bash
   uv sync
```
 
6. **Run database migrations:**
```bash
   uv run alembic upgrade head
```
 
7. **Seed sample data** (5 doctors with varied working hours, plus a test patients):
```bash
   uv run python src/app/seed.py
```
 
8. **Start the API:**
```bash
   uv run fastapi dev src/app/main.py
```
   The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.
 
9. **Run the test suite:**
```bash
   uv run pytest src/app/tests/ -v
```