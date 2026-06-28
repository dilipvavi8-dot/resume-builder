# Rolecraft Agent Guide

Read [README.md](README.md) for setup and architecture before changing the application.

Project-specific agent profiles live in [agents/](agents/README.md). Choose the smallest
set of roles needed for the task:

- `principal-architect`: cross-system design, contracts, storage, and major changes
- `frontend-engineer`: Next.js UI, accessibility, responsive design, and API integration
- `backend-ai-engineer`: FastAPI, SQLite, analysis, fetching, and resume generation
- `qa-devops-engineer`: local runtime, validation, regression testing, and documentation

Runtime resume generation uses:

- `resume-tailoring-agent`: evidence-constrained summary, skills, and bullet rewriting
- `resume-quality-monitor`: independent verification and corrective revision requests

Reusable Codex skills live in [skills/](skills/README.md):

- `$maintain-rolecraft-app` for implementation and maintenance
- `$verify-rolecraft-workflows` for end-to-end verification

## Required Practices

1. Preserve local-first behavior: no authentication, cloud storage, or auto-apply.
2. Never invent resume experience or silently overwrite generated resumes.
3. Keep frontend API calls in `frontend/src/lib/api.ts`.
4. Keep backend business logic in `backend/services/`; keep route handlers thin.
5. Update SQLite schema and API documentation together when contracts change.
6. Run frontend lint/build and relevant backend workflow checks before finishing.
7. Do not commit `.env`, local resumes, generated resumes, SQLite data, virtual
   environments, `node_modules`, or `.next`.
