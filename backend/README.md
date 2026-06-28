# Backend

FastAPI, SQLite, APScheduler, and local DOCX generation for Rolecraft.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

API documentation is available at `http://localhost:8000/docs`.
