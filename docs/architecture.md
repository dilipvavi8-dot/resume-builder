# Current architecture

## Purpose

Explain how Rolecraft's browser UI, local API, business services, database, and file storage
work together. This is the architecture currently present in the repository, not a proposed
cloud deployment design.

## Diagram

```mermaid
flowchart LR
    User[User in local browser] --> FE[Next.js frontend<br/>localhost:3001]
    FE -->|HTTP / multipart| API[FastAPI API<br/>127.0.0.1:8000]
    FE <-->|WebSocket events| WS[/ws/events]
    API --> Routes[Thin API routes<br/>backend/main.py]
    Routes --> Services[Domain services]
    Services --> SQLite[(SQLite database<br/>Application Support/Rolecraft)]
    Services --> Files[Local files<br/>profiles, drafts, DOCX/PDF]
    Services --> Scheduler[APScheduler<br/>daily local job refresh]
    Services --> Agents[Resume updater, tailorer,<br/>quality monitor]
    API --> WS
    Scheduler --> Services
```

## Step by step

1. A user opens the Next.js app at `http://localhost:3001`.
2. Client components call the FastAPI server only through `frontend/src/lib/api.ts`.
3. `backend/main.py` validates HTTP input and delegates work to `backend/services/`.
4. Services read/write local SQLite data and private local files.
5. The resume agents create a separate draft, then the quality monitor evaluates it.
6. The API returns JSON, a local-file download, or WebSocket progress updates to the UI.

## Important files

| File or directory | Why it matters |
|---|---|
| `frontend/src/app/` | Route-level pages for the workspace |
| `frontend/src/components/` | Interactive UI and WebSocket consumers |
| `frontend/src/lib/api.ts` | Browser API base URL, fetch behavior, download URLs |
| `backend/main.py` | FastAPI routes, CORS, app lifecycle, WebSocket endpoint |
| `backend/services/` | Business logic; route handlers remain thin |
| `backend/database/` | SQLite schema, migrations, connections |
| `backend/storage/` | Local resume profiles, drafts, and generated artifacts |
| `backend/services/scheduler.py` | Daily refresh scheduler |

## Failure behavior and verification

- If the API is unavailable, `api.ts` turns the response into a user-facing error.
- If SQLite or a local file is unavailable, the relevant FastAPI route returns an error.
- If the scheduler cannot start, `/health` reports its runtime status.

Verify locally:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/dashboard/summary
```

## Current boundary

There is no Docker, Kubernetes/WCNP, Helm, KITT, `.looper.yml`, deployment profile, cloud
secret manager, authentication provider, or external downstream service configured in this
repository. Job sources are currently mock/local handlers; portal interactions remain manual.
