"""Safe operations for versioned, generated resume artifacts."""

from pathlib import Path

from database.db import get_db


def delete_resume_versions(resume_ids: list[int]) -> dict:
    """Delete selected generated versions and their local artifacts only.

    Base profiles and review-only drafts live elsewhere and are intentionally out of
    scope. Application records are retained, with their optional version reference
    cleared so application history remains intact.
    """
    ids = sorted({value for value in resume_ids if isinstance(value, int) and value > 0})
    if not ids:
        raise ValueError("Select at least one generated resume to delete.")
    placeholders = ",".join("?" for _ in ids)
    with get_db() as db:
        rows = db.execute(
            f"SELECT id, docx_path, pdf_path FROM resume_versions WHERE id IN ({placeholders})",
            ids,
        ).fetchall()
        if not rows:
            raise ValueError("The selected generated resumes were not found.")
        found_ids = [row["id"] for row in rows]
        found_placeholders = ",".join("?" for _ in found_ids)
        db.execute(
            f"UPDATE applications SET resume_id=NULL WHERE resume_id IN ({found_placeholders})",
            found_ids,
        )
        db.execute(f"DELETE FROM resume_versions WHERE id IN ({found_placeholders})", found_ids)

    removed_files = 0
    for row in rows:
        for value in (row["docx_path"], row["pdf_path"]):
            if not value:
                continue
            path = Path(value)
            if path.exists() and path.is_file():
                path.unlink()
                removed_files += 1
    return {"deleted_versions": len(rows), "deleted_files": removed_files}
