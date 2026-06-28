"""Lightweight, local structured resume parsing used for planning—not generation."""

from __future__ import annotations

import re

from utils.scoring import detect_skills


HEADINGS = {
    "summary": {"summary", "professional summary", "profile"},
    "skills": {"skills", "technical skills", "core competencies"},
    "experience": {"experience", "work experience", "professional experience"},
    "education": {"education"},
    "certifications": {"certifications", "certificates"},
    "projects": {"projects", "project experience"},
}


def _heading(value: str) -> str | None:
    normalized = re.sub(r"[:\s]+$", "", value.lower().strip())
    return next((key for key, names in HEADINGS.items() if normalized in names), None)


def _is_bullet(value: str) -> bool:
    return bool(re.match(r"^(?:[-•*]|\d+[.)])\s+", value.strip()))


def _queries(stack: list[str]) -> list[dict]:
    values = set(stack)
    queries = []
    if values & {"AWS", "Azure", "GCP"}:
        queries.append({"cluster": "cloud", "titles": ["Cloud Architect", "Cloud Solutions Architect", "Enterprise Cloud Architect"]})
    if values & {"CI/CD", "Kubernetes", "Docker", "Jenkins", "Ansible", "Terraform", "Azure DevOps", "Argo CD"}:
        queries.append({"cluster": "platform", "titles": ["DevOps Engineer", "Platform Engineer", "Site Reliability Engineer"]})
    if values & {"MLOps", "Machine Learning"}:
        queries.append({"cluster": "mlops", "titles": ["MLOps Engineer", "Data Platform Engineer"]})
    return queries


def parse_resume(text: str) -> dict:
    """Return a transparent best-effort structure without guessing employers or dates."""
    sections: dict[str, list[str]] = {key: [] for key in HEADINGS}
    other: list[str] = []
    current = "other"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        heading = _heading(line)
        if heading:
            current = heading
            continue
        (sections[current] if current in sections else other).append(line)

    experience = []
    current_client: dict | None = None
    for line in sections["experience"]:
        if _is_bullet(line):
            if current_client is None:
                current_client = {"employer": "Unlabeled experience", "role": "", "dates": "", "bullets": []}
                experience.append(current_client)
            current_client["bullets"].append(re.sub(r"^(?:[-•*]|\d+[.)])\s+", "", line))
        else:
            parts = re.split(r"\s*[|—–]\s*", line, maxsplit=2)
            current_client = {
                "employer": parts[0],
                "role": parts[1] if len(parts) > 1 else "",
                "dates": parts[2] if len(parts) > 2 else "",
                "bullets": [],
            }
            experience.append(current_client)
    for client in experience:
        client["stack"] = detect_skills("\n".join(client["bullets"]))

    clients = experience[:2]
    stack = list(dict.fromkeys(skill for client in clients for skill in client["stack"]))
    return {
        "contact": {},
        "summary": " ".join(sections["summary"]),
        "skills": detect_skills("\n".join(sections["skills"]) or text),
        "experience": experience,
        "education": sections["education"],
        "certifications": sections["certifications"],
        "projects": sections["projects"],
        "other": other,
        "clients": clients,
        "stack": stack,
        "search_queries": _queries(stack),
    }
