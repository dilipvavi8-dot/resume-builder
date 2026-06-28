"""Human approval routing. Rolecraft deliberately never submits applications."""

from __future__ import annotations

from database.db import get_db
from services.notification_service import create as notify


def _is_fte(employment_type: str | None) -> bool:
    return (employment_type or "").lower() in {"full-time", "full time", "fte", "permanent"}


def route_high_match(job_id: int, score: int, employment_type: str | None, company: str, title: str) -> None:
    if score < 90 or not _is_fte(employment_type):
        return
    with get_db() as db:
        existing = db.execute("SELECT id FROM fte_approvals WHERE job_id=?", (job_id,)).fetchone()
        if existing:
            return
        db.execute("INSERT INTO fte_approvals (job_id, score) VALUES (?, ?)", (job_id, score))
    notify("fte_approval", "action", "Approval needed", f"{company} — {title} scored {score}%. Review it before you apply manually.", job_id)


def list_pending() -> list[dict]:
    with get_db() as db:
        return [dict(row) for row in db.execute(
            """SELECT f.*, j.company, j.title, j.location, j.source_url, j.employment_type
               FROM fte_approvals f JOIN jobs j ON j.id=f.job_id
               ORDER BY f.created_at DESC"""
        ).fetchall()]


def decide(approval_id: int, decision: str, reason: str = "") -> dict | None:
    if decision not in {"approved", "rejected"}:
        raise ValueError("Decision must be approved or rejected.")
    with get_db() as db:
        row = db.execute("SELECT * FROM fte_approvals WHERE id=?", (approval_id,)).fetchone()
        if not row:
            return None
        db.execute("UPDATE fte_approvals SET status=?, reason=?, decided_at=CURRENT_TIMESTAMP WHERE id=?", (decision, reason, approval_id))
        db.execute("UPDATE jobs SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", ("Ready to apply" if decision == "approved" else "Archived", row["job_id"]))
        result = dict(db.execute("SELECT * FROM fte_approvals WHERE id=?", (approval_id,)).fetchone())
    notify("fte_approval", "info", "Role approved for manual application" if decision == "approved" else "Role archived", "Open the source link and complete the application yourself." if decision == "approved" else (reason or "Archived from the review queue."), result["job_id"])
    return result
