from database.db import get_db
from database.models import SCHEMA


def init_db() -> None:
    with get_db() as db:
        db.executescript(SCHEMA)
        resume_columns = {
            row["name"] for row in db.execute("PRAGMA table_info(resume_versions)").fetchall()
        }
        migrations = {
            "generation_status": "TEXT DEFAULT 'completed'",
            "requirement_coverage": "INTEGER DEFAULT 0",
            "truthfulness_score": "INTEGER DEFAULT 0",
            "generation_report": "TEXT",
        }
        for column, definition in migrations.items():
            if column not in resume_columns:
                db.execute(
                    f"ALTER TABLE resume_versions ADD COLUMN {column} {definition}"
                )
        draft_columns = {row["name"] for row in db.execute("PRAGMA table_info(resume_drafts)").fetchall()}
        if "ats_score" not in draft_columns:
            db.execute("ALTER TABLE resume_drafts ADD COLUMN ats_score INTEGER DEFAULT 0")
        existing = db.execute("SELECT COUNT(*) AS count FROM job_sources").fetchone()["count"]
        if not existing:
            db.executemany(
                "INSERT INTO job_sources (source_name, source_url, source_type) VALUES (?, ?, ?)",
                [
                    ("Demo Greenhouse", "https://boards.greenhouse.io/", "greenhouse"),
                    ("Demo Lever", "https://jobs.lever.co/", "lever"),
                    ("Local curated samples", "local://mock-jobs", "mock"),
                ],
            )


if __name__ == "__main__":
    init_db()
