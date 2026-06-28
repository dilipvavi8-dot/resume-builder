# Resume Builder API

Resume Builder is a FastAPI backend for creating, validating, updating, exporting,
and improving structured resume data. The current `develop` branch contains the API
service only; no frontend application is tracked in this branch.

## What the app does

- Stores resumes in an in-memory service for local development.
- Validates contact information, work history, education, projects, skills, and
  certifications with Pydantic models.
- Exposes CRUD endpoints for resumes.
- Exports saved resumes as JSON or plain text.
- Provides rule-based "AI-style" suggestions for summary, bullet, and skills sections.
- Provides health and readiness endpoints for local and container checks.

## Local setup

Use Python 3.11 or 3.12. The pinned Pydantic version does not support Python 3.14.

```bash
python3.11 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
```

## Run locally

```bash
.venv/bin/uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Local URLs:

- API root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/v1/health`
- Readiness: `http://127.0.0.1:8000/api/v1/ready`

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API root message |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/ready` | Readiness check |
| `POST` | `/api/v1/resumes` | Create a resume |
| `GET` | `/api/v1/resumes` | List saved resumes |
| `GET` | `/api/v1/resumes/{resume_id}` | Read a saved resume |
| `PUT` | `/api/v1/resumes/{resume_id}` | Update a saved resume |
| `DELETE` | `/api/v1/resumes/{resume_id}` | Delete a saved resume |
| `GET` | `/api/v1/resumes/{resume_id}/export/json` | Export resume JSON |
| `GET` | `/api/v1/resumes/{resume_id}/export/text` | Export resume text |
| `POST` | `/api/v1/resumes/ai/suggest` | Generate rule-based writing suggestions |

## Test and quality checks

```bash
.venv/bin/python -m compileall src
.venv/bin/python -m black --check src tests
.venv/bin/python -m flake8 src tests
.venv/bin/python -m pytest
```

## Docker

```bash
docker compose up --build backend
```

The Docker Compose file currently starts the backend only, matching the files tracked
on `develop`.

## Safety notes

- Do not commit `.env`, virtual environments, caches, test output, node_modules, or
  build artifacts.
- `.env.example` is safe to commit because it contains placeholders only.
- Runtime resume storage is in memory in this branch; replacing it with a database should
  include migration and persistence tests.
