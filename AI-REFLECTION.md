# AI Reflection
 
**1. What did you use AI for across the four sections?**
 
- Section 1: talking through the system design out loud — models, entity relationships, and specifically stress-testing my own draft for contradictions and missing edge cases (e.g. the composite-primary-key bug in my first schema draft, the working-hours cardinality mismatch).

- Section 2: Writing SQLAlchemy models and Alembic migrations, drafting the validation and availability logic, and debugging errors as they came up (Ruff warnings, packaging config, a timezone-parsing crash, a Docker build failure).

- Section 3: step-by-step guidance through GCP setup (Cloud SQL, Cloud Run, Artifact Registry), writing the Dockerfile and GitHub Actions workflow, and debugging deploy failures.

- Throughout: keeping the README's Decisions section in sync with the actual code as the design evolved.


**2. Give one example where an AI suggestion improved your work. What did you prompt it with?**
 
When wiring up the booking endpoint, I asked how to handle the case where two requests might try to book the same slot at the same time. The AI pointed out that my proactive "is this slot free" check in the validation layer, on its own, doesn't actually close the race condition — two requests could both pass that check before either commits. It suggested wrapping the actual database insert in a try/except for `IntegrityError` and catching it as a backstop against the partial unique index at the DB level, translating that into the same clean `409` response a client would get from the proactive check. This gave me a genuine two-layer defense (a friendly proactive check, plus a real database-level guarantee) instead of relying on a check that looked correct but had a timing gap.
 
**3. Give one example where AI output was wrong or incomplete and how you caught it.**
 
Early in Section 2, the AI-generated `Appointment` model used a plain `UniqueConstraint` on `(doctorID, date, timeStart)` — even though my own design doc had already called for a *partial* unique index scoped to `status = 'booked'`, specifically so a cancelled appointment's slot could be rebooked. The generated code didn't match the documented decision, and I caught the mismatch by comparing the two side by side rather than assuming the code was correct because it ran without errors. I fixed it using an Alembic migration using a partial index instead. Separately, I found a real bug myself through manual testing : booking a slot at `15:35` and then a second appointment at `15:32` both succeeded, even though their 30-minute windows genuinely overlapped — because the validation only checked for an *exact* time match, not overlapping ranges.
 
**4. Name two decisions you made without AI. Why did you trust your own judgment there?**
 
- Spotting that reschedule/cancel had no guard against acting on an appointment whose time had already passed. This came from thinking through the feature from a user's perspective, not from a code review — it's the kind of "wait, what if someone does *this*" instinct that comes from imagining real misuse.
- Catching the overlapping-slot double-booking bug described above. I trusted my own judgment here because it came from actually testing the running system with realistic inputs, rather than trusting that code which passed a few obvious test cases was necessarily correct — the bug only showed up because I tried a value that wasn't perfectly aligned to the slot grid, which is exactly the kind of "unexpected user input" testing that catches gaps in an AI-generated implementation.
 