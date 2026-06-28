---
name: maintain-rolecraft-app
description: Maintain and extend the Rolecraft local job and resume assistant across its Next.js frontend, FastAPI backend, SQLite database, local file storage, scheduler, job analysis, matching, and DOCX generation. Use for Rolecraft feature work, bug fixes, UI changes, API or schema changes, job-source integrations, scoring changes, resume generation changes, and architecture documentation updates.
---

# Maintain Rolecraft App

## Workflow

1. Read the root `README.md` and `AGENTS.md`.
2. Read [references/architecture.md](references/architecture.md) for ownership and
   invariants.
3. Inspect the affected frontend page/component, API endpoint, service, and table before
   editing.
4. Identify whether the change alters an HTTP contract, SQLite schema, local file
   behavior, or scheduler behavior.
5. Implement the smallest coherent cross-layer change.
6. Add or update user-facing loading, empty, success, and error states.
7. Use `$verify-rolecraft-workflows` for the affected workflow.
8. Update `README.md`, agent guidance, or this skill when architecture or operating
   procedures change.

## Architectural Constraints

- Keep the application local-only with no login or cloud storage.
- Never auto-apply to jobs.
- Never bypass CAPTCHA, login, robots restrictions, or source terms.
- Keep analysis usable without an OpenAI key.
- Never invent candidate experience.
- Never overwrite a generated resume.
- Preserve source URLs and deduplicate fetched jobs.
- Keep FastAPI handlers thin and business logic in `backend/services/`.
- Keep browser API access in `frontend/src/lib/api.ts`.

## Change Routing

- **Landing page or workspace UI:** use the Frontend Engineer profile.
- **API, SQLite, scoring, fetching, or DOCX:** use the Backend and AI Engineer profile.
- **Cross-layer contract or storage change:** begin with the Principal Architect profile.
- **Runtime or regression check:** finish with the QA and DevOps Engineer profile.

## Required Validation

```bash
cd frontend
npm run lint
npm run build
```

Compile changed Python modules and run the relevant API workflow. Do not claim full
verification when a required service or browser check could not run.
