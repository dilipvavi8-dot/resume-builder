# Rolecraft Architecture Reference

## System

```text
Browser
  -> Next.js App Router frontend
  -> FastAPI JSON and multipart API
  -> services
  -> SQLite plus backend/storage
```

## Frontend Ownership

- `src/app/page.tsx`: cinematic landing page
- `src/app/dashboard/page.tsx`: workspace overview
- `src/app/jobs/page.tsx`: job feed
- `src/app/manual-jd/page.tsx`: manual analysis workflow
- `src/app/resumes/page.tsx`: generated resume history
- `src/app/tracker/page.tsx`: application tracking
- `src/components/`: interactive UI implementations
- `src/lib/api.ts`: backend URL, request handling, and download URLs

## Backend Ownership

- `main.py`: API contracts, validation, and CORS
- `database/models.py`: SQLite schema
- `database/db.py`: connections and transactions
- `services/job_fetcher.py`: source handlers, deduplication, persistence
- `services/jd_analyzer.py`: analysis entry point
- `services/resume_matcher.py`: matching entry point
- `services/resume_generator.py`: DOCX output and naming
- `services/file_service.py`: resume library persistence and active-profile selection
- `services/scheduler.py`: daily fetch schedule
- `utils/scoring.py`: deterministic extraction and scoring
- `utils/text_parser.py`: TXT, DOCX, and PDF extraction

## Persistent Tables

`jobs`, `manual_jds`, `resume_versions`, `applications`, `job_sources`, and
`daily_fetch_logs`.

## Runtime Files

All private runtime data belongs under `backend/storage/`. Do not move it into the
frontend or commit it to source control.

## Core Invariants

1. Many retained base resumes, exactly one active main resume, and many generated versions.
2. Every generated resume has a database record and unique filename.
3. Every fetched job has a source URL.
4. A refresh updates duplicates and recalculates their analysis.
5. The deterministic analyzer works without external AI.
6. The scheduler defaults to 8:00 AM local time.
