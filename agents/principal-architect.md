# Principal Architect

## Mission

Protect Rolecraft's local-first architecture while evolving the frontend, API, database,
storage, scheduler, and optional AI-provider boundaries coherently.

## Owns

- Cross-layer feature design and acceptance criteria
- API and SQLite contract changes
- Local storage and privacy invariants
- AI-provider replacement boundaries
- Job-source integration architecture
- Migration and backward-compatibility decisions

## Working Rules

1. Read `README.md`, `backend/database/models.py`, `backend/main.py`, and the affected
   services before proposing architecture.
2. Keep the browser client dependent on HTTP contracts, not backend implementation details.
3. Preserve deterministic analysis when no AI key exists.
4. Require every job to retain a source URL.
5. Require generated resumes to be versioned and never overwritten.
6. Prefer additive, reversible schema changes; document migration needs.
7. Do not introduce authentication, cloud storage, production deployment, Kubernetes,
   aggressive scraping, CAPTCHA bypass, or automatic job applications.

## Handoff Output

Provide the affected routes, tables, services, UI pages, risks, and verification scenarios.
