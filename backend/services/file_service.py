import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE = BASE_DIR / "storage"
MASTER_DIR = STORAGE / "master_resume"
LIBRARY_DIR = STORAGE / "resume_library"
ACTIVE_PATH = LIBRARY_DIR / "active.json"


def master_metadata_path() -> Path:
    return MASTER_DIR / "metadata.json"


def _profile_id(filename: str) -> str:
    stem = Path(filename).stem.lower()
    base = re.sub(r"[^a-z0-9]+", "-", stem).strip("-") or "resume"
    candidate = base
    counter = 2
    while (LIBRARY_DIR / candidate).exists():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


def _read_profile(profile_id: str) -> dict | None:
    path = LIBRARY_DIR / profile_id / "metadata.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def active_profile_id() -> str | None:
    if not ACTIVE_PATH.exists():
        return None
    return json.loads(ACTIVE_PATH.read_text(encoding="utf-8")).get("profile_id")


def list_resume_profiles() -> list[dict]:
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    active = active_profile_id()
    profiles = []
    for metadata_path in sorted(LIBRARY_DIR.glob("*/metadata.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["active"] = metadata["id"] == active
        profiles.append(metadata)
    return sorted(profiles, key=lambda item: item["created_at"], reverse=True)


def get_master_resume() -> dict | None:
    profile_id = active_profile_id()
    if profile_id:
        metadata = _read_profile(profile_id)
        if metadata:
            metadata["active"] = True
            metadata["profiles"] = list_resume_profiles()
            return metadata

    path = master_metadata_path()
    if path.exists():
        metadata = json.loads(path.read_text(encoding="utf-8"))
        metadata["active"] = True
        metadata["profiles"] = []
        return metadata
    return None


def save_master_resume(filename: str, content: bytes, text: str) -> dict:
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    profile_id = _profile_id(filename)
    profile_dir = LIBRARY_DIR / profile_id
    profile_dir.mkdir(parents=True)
    suffix = Path(filename).suffix.lower() or ".txt"
    target = profile_dir / f"source{suffix}"
    target.write_bytes(content)
    text_path = profile_dir / "extracted.txt"
    text_path.write_text(text, encoding="utf-8")
    metadata = {
        "id": profile_id,
        "name": re.sub(r"[_-]+", " ", Path(filename).stem).strip(),
        "filename": filename,
        "path": str(target),
        "text_path": str(text_path),
        "characters": len(text),
        "preview": text[:1200],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (profile_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    select_master_resume(profile_id)
    metadata["active"] = True
    return metadata


def select_master_resume(profile_id: str) -> dict:
    metadata = _read_profile(profile_id)
    if not metadata:
        raise ValueError("Resume profile not found.")
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_PATH.write_text(
        json.dumps({"profile_id": profile_id}, indent=2),
        encoding="utf-8",
    )
    metadata["active"] = True
    return metadata


def master_text() -> str:
    profile_id = active_profile_id()
    if profile_id:
        metadata = _read_profile(profile_id)
        if metadata:
            path = Path(metadata["text_path"])
            return path.read_text(encoding="utf-8") if path.exists() else ""
    path = MASTER_DIR / "master_resume.txt"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def active_resume_source() -> Path | None:
    metadata = get_master_resume()
    if not metadata:
        return None
    path = Path(metadata["path"])
    return path if path.exists() else None
