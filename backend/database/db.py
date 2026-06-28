from contextlib import contextmanager
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[1]
LEGACY_DB_PATH = BASE_DIR / "storage" / "job_resume_ai.db"
DB_PATH = Path.home() / "Library" / "Application Support" / "Rolecraft" / "job_resume_ai.db"


def _ensure_local_database() -> None:
    """Keep SQLite outside Desktop/iCloud providers, which can hold write locks."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists() or not LEGACY_DB_PATH.exists():
        return
    source = sqlite3.connect(LEGACY_DB_PATH)
    destination = sqlite3.connect(DB_PATH)
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()


def connect() -> sqlite3.Connection:
    _ensure_local_database()
    # Resume drafting emits monitor and notification events while it persists a draft.
    # Give concurrent local writers time to finish instead of surfacing a generic
    # browser-side "Failed to fetch" error.
    connection = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 30000")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


@contextmanager
def get_db():
    connection = connect()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
