"""Local persisted notification feed; no external delivery or cloud service."""

from __future__ import annotations

from database.db import get_db
from services.realtime import event_hub


def create(category: str, severity: str, title: str, body: str, job_id: int | None = None) -> dict:
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO notifications (category, severity, title, body, job_id) VALUES (?, ?, ?, ?, ?)",
            (category, severity, title, body, job_id),
        )
        item = dict(db.execute("SELECT * FROM notifications WHERE id=?", (cursor.lastrowid,)).fetchone())
    event_hub.publish({"type": "notification", "notification": item})
    return item


def list_notifications(limit: int = 30) -> list[dict]:
    with get_db() as db:
        return [dict(row) for row in db.execute("SELECT * FROM notifications ORDER BY created_at DESC, id DESC LIMIT ?", (limit,)).fetchall()]


def mark_read(notification_id: int) -> bool:
    with get_db() as db:
        return bool(db.execute("UPDATE notifications SET is_read=1 WHERE id=?", (notification_id,)).rowcount)
