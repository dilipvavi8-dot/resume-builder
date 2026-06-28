---
name: verify-rolecraft-workflows
description: Verify Rolecraft end to end across Next.js pages, FastAPI endpoints, SQLite persistence, local storage, job fetching, JD analysis, match scoring, DOCX generation, downloads, and application tracking. Use after Rolecraft code changes, before handoff, when a page or API is broken, or when confirming local setup and responsive UI behavior.
---

# Verify Rolecraft Workflows

## Preparation

1. Read [references/verification-matrix.md](references/verification-matrix.md).
2. Check whether ports `3000` and `8000` are already in use before starting services.
3. Use a clearly labeled test resume fixture, never private user data.
4. Preserve existing SQLite and generated files unless the user explicitly requests a
   clean reset.

## Verification Order

1. Compile changed Python modules.
2. Run frontend lint and production build.
3. Start or identify the frontend and backend services.
4. Verify backend health and dashboard summary.
5. Verify the affected API flow and persisted records.
6. Verify generated files exist and are non-empty.
7. Inspect affected pages in a browser at desktop and phone widths.
8. Check loading, empty, success, disabled, and error states.
9. Re-run the exact failed scenario after any fix.

## Minimum Commands

```bash
cd frontend
npm run lint
npm run build
```

```bash
cd backend
.venv/bin/python -m compileall main.py database services utils
```

Use `GET /health` as the authoritative backend readiness check.

## Evidence

Report:

- commands that passed or failed
- endpoint results relevant to the change
- database or file artifacts created
- routes and viewport sizes inspected
- remaining limitations, including unavailable MCP or browser surfaces

Do not treat a successful server startup as proof that the user workflow works.
