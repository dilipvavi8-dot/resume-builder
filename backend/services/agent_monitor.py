"""Persisted, transparent telemetry for Rolecraft's local analysis pipeline."""

from __future__ import annotations

from database.db import get_db
from services.realtime import event_hub

AGENTS = [
    ("JD Scanner", "Extracts role requirements and employment details."),
    ("Match Scorer", "Calculates evidence-based resume alignment."),
    ("Resume Tailoring Agent", "Rewrites only supported resume content."),
    ("Resume Quality Monitor", "Checks evidence, metrics, and layout preservation."),
]


def record(agent_name: str, status: str, detail: str, job_id: int | None = None) -> None:
    with get_db() as db:
        db.execute(
            "INSERT INTO agent_events (job_id, agent_name, status, detail) VALUES (?, ?, ?, ?)",
            (job_id, agent_name, status, detail),
        )
    event_hub.publish({"type": "agent_event", "agent_name": agent_name, "status": status, "detail": detail, "job_id": job_id})


def snapshot() -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            """SELECT e.agent_name, e.status, e.detail, e.created_at
               FROM agent_events e INNER JOIN (
                 SELECT agent_name, MAX(id) AS latest_id FROM agent_events GROUP BY agent_name
               ) latest ON e.id = latest.latest_id"""
        ).fetchall()
    latest = {row["agent_name"]: dict(row) for row in rows}
    return [
        {"name": name, "role": role, **latest.get(name, {"status": "idle", "detail": "Waiting for a local workflow.", "created_at": None})}
        for name, role in AGENTS
    ]
