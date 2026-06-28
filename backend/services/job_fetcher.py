from datetime import date, timedelta

from database.db import get_db
from services.file_service import master_text
from utils.scoring import analyze_text


def fetch_greenhouse_jobs() -> list[dict]:
    return []


def fetch_lever_jobs() -> list[dict]:
    return []


def fetch_generic_public_jobs() -> list[dict]:
    return []


def fetch_mock_jobs() -> list[dict]:
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    return [
        {
            "title": "Senior Site Reliability Engineer",
            "company": "Northstar Systems",
            "location": "Remote, USA",
            "remote_type": "Remote",
            "employment_type": "Full-time",
            "posted_date": date.today().isoformat(),
            "source_url": "https://example.com/jobs/northstar-sre",
            "source_type": "mock",
            "experience_required": "6+ years",
            "job_description": "Build reliable AWS and Kubernetes platforms using Terraform, Python, Prometheus, Grafana, OpenTelemetry, incident management, SLOs, security, and GitHub Actions CI/CD.",
        },
        {
            "title": "Cloud Platform Engineer",
            "company": "Layerworks",
            "location": "Chicago, IL",
            "remote_type": "Hybrid",
            "employment_type": "Full-time",
            "posted_date": yesterday,
            "source_url": "https://example.com/jobs/layerworks-platform",
            "source_type": "mock",
            "experience_required": "5+ years",
            "job_description": "Design Azure and AWS cloud infrastructure with Terraform, Kubernetes, Helm, Argo CD, GitHub Actions, Linux, networking, security and observability.",
        },
        {
            "title": "AI Infrastructure Automation Engineer",
            "company": "SignalForge AI",
            "location": "Austin, TX / Remote",
            "remote_type": "Remote",
            "employment_type": "Full-time",
            "posted_date": date.today().isoformat(),
            "source_url": "https://example.com/jobs/signalforge-ai-infra",
            "source_type": "mock",
            "experience_required": "4+ years",
            "job_description": "Automate GenAI infrastructure across GCP and AWS with Python, Terraform, Docker, Kubernetes, OpenAI APIs, Datadog, CI/CD, and cost optimization.",
        },
    ]


def run_fetch() -> dict:
    jobs = fetch_mock_jobs()
    saved = duplicates = 0
    resume = master_text()
    with get_db() as db:
        for job in jobs:
            analysis = analyze_text(
                job["job_description"],
                resume,
                title=job["title"],
                location=job["location"],
            )
            existing = db.execute("SELECT id FROM jobs WHERE source_url = ?", (job["source_url"],)).fetchone()
            if existing:
                duplicates += 1
                db.execute(
                    """UPDATE jobs SET posted_date=?, job_description=?, experience_required=?,
                    required_skills=?, preferred_skills=?, cloud_platform=?, role_type=?,
                    match_score=?, missing_keywords=?, recommendation=?,
                    updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                    (
                        job["posted_date"], job["job_description"], job["experience_required"],
                        ",".join(analysis["required_skills"]), "",
                        analysis["cloud_platform"], analysis["role_type"],
                        analysis["match_score"], ",".join(analysis["missing_keywords"]),
                        analysis["recommendation"], existing["id"],
                    ),
                )
                continue
            db.execute(
                """INSERT INTO jobs (
                  title, company, location, remote_type, employment_type, posted_date,
                  source_url, source_type, job_description, experience_required,
                  required_skills, preferred_skills, cloud_platform, role_type,
                  match_score, missing_keywords, recommendation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    job["title"], job["company"], job["location"], job["remote_type"],
                    job["employment_type"], job["posted_date"], job["source_url"],
                    job["source_type"], job["job_description"], job["experience_required"],
                    ",".join(analysis["required_skills"]), "", analysis["cloud_platform"],
                    analysis["role_type"], analysis["match_score"],
                    ",".join(analysis["missing_keywords"]), analysis["recommendation"],
                ),
            )
            saved += 1
        db.execute(
            "INSERT INTO daily_fetch_logs (fetch_date, jobs_found, jobs_saved, duplicates_removed, errors) VALUES (?, ?, ?, ?, ?)",
            (date.today().isoformat(), len(jobs), saved, duplicates, ""),
        )
    return {"jobs_found": len(jobs), "jobs_saved": saved, "duplicates_removed": duplicates}
