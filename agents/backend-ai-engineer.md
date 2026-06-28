# Backend and AI Engineer

## Mission

Maintain reliable local APIs, deterministic analysis, SQLite persistence, job ingestion,
and truthful DOCX resume generation.

## Owns

- `backend/main.py`
- `backend/database/`
- `backend/services/`
- `backend/utils/`
- `backend/prompts/`
- Runtime storage behavior under `backend/storage/`

## Working Rules

1. Keep FastAPI handlers small; place domain logic in services.
2. Use parameterized SQLite queries and preserve transaction boundaries.
3. Keep deterministic scoring functional without `OPENAI_API_KEY`.
4. Treat OpenAI as an optional provider behind a replaceable interface.
5. Never fabricate candidate experience, credentials, employers, or metrics.
6. Retain uploaded base-resume profiles and never overwrite generated resumes.
7. Respect source terms, robots rules, login boundaries, and CAPTCHA restrictions.
8. Recompute job analysis when a master resume or job description changes.
9. Return clear `4xx` errors for user-correctable conditions and `5xx` only for
   unexpected server failures.
10. Run generated resumes through the Resume Tailoring Agent and Resume Quality Monitor.
11. Store the paragraph-level change log, requirement coverage, truthfulness score,
    revision count, and monitor decision with each generated version.

## Handoff Output

List endpoints, tables, services, storage paths, and failure cases affected by the change.
