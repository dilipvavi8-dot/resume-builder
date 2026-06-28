from fastapi.testclient import TestClient

from src.main import app
from src.services.resume_service import ResumeService


client = TestClient(app)


def sample_resume_payload() -> dict:
    return {
        "contact": {
            "full_name": "Test Candidate",
            "email": "candidate@example.com",
            "phone": "555-0100",
            "location": "Remote",
            "linkedin": "https://www.linkedin.com/in/test-candidate",
            "github": "https://github.com/test-candidate",
        },
        "summary": "Platform engineer focused on reliable API delivery.",
        "work_experience": [
            {
                "company": "Example Corp",
                "title": "Senior Engineer",
                "start_date": "Jan 2021",
                "end_date": "Present",
                "location": "Remote",
                "bullets": [
                    "Built FastAPI services with CI/CD automation.",
                    "Improved service reliability through monitoring.",
                ],
            }
        ],
        "education": [
            {
                "institution": "Example University",
                "degree": "BS",
                "field_of_study": "Computer Science",
                "end_date": "2020",
            }
        ],
        "skills": ["Python", "FastAPI", "AWS", "Docker"],
        "projects": [
            {
                "name": "Resume Builder",
                "description": "API for structured resume management.",
                "technologies": ["FastAPI", "Pydantic"],
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Developer",
                "issuer": "AWS",
                "date_issued": "2024",
            }
        ],
        "template": "modern",
    }


def setup_function():
    ResumeService._store.clear()


def test_health_ready_and_root():
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["message"] == "Resume Builder API is running"

    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    ready = client.get("/api/v1/ready")
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}


def test_resume_crud_export_and_delete_flow():
    created = client.post("/api/v1/resumes", json=sample_resume_payload())
    assert created.status_code == 201
    resume_id = created.json()["id"]

    listed = client.get("/api/v1/resumes")
    assert listed.status_code == 200
    assert listed.json()["count"] == 1
    assert listed.json()["resumes"][0]["name"] == "Test Candidate"

    fetched = client.get(f"/api/v1/resumes/{resume_id}")
    assert fetched.status_code == 200
    assert fetched.json()["data"]["contact"]["email"] == "candidate@example.com"

    updated_payload = sample_resume_payload()
    updated_payload["contact"]["full_name"] = "Updated Candidate"
    updated = client.put(f"/api/v1/resumes/{resume_id}", json=updated_payload)
    assert updated.status_code == 200
    assert updated.json()["data"]["contact"]["full_name"] == "Updated Candidate"

    exported_json = client.get(f"/api/v1/resumes/{resume_id}/export/json")
    assert exported_json.status_code == 200
    assert exported_json.json()["contact"]["full_name"] == "Updated Candidate"

    exported_text = client.get(f"/api/v1/resumes/{resume_id}/export/text")
    assert exported_text.status_code == 200
    assert "UPDATED CANDIDATE" in exported_text.text
    assert "WORK EXPERIENCE" in exported_text.text

    deleted = client.delete(f"/api/v1/resumes/{resume_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/resumes/{resume_id}")
    assert missing.status_code == 404


def test_validation_and_missing_resume_errors():
    invalid = client.post(
        "/api/v1/resumes",
        json={
            "contact": {
                "full_name": "",
                "email": "not-an-email",
            }
        },
    )
    assert invalid.status_code == 422

    missing = client.get("/api/v1/resumes/not-found")
    assert missing.status_code == 404
    assert "not found" in missing.json()["detail"]

    missing_export = client.get("/api/v1/resumes/not-found/export/text")
    assert missing_export.status_code == 404


def test_ai_suggestions_for_supported_sections():
    summary = client.post(
        "/api/v1/resumes/ai/suggest",
        json={
            "section": "summary",
            "context": "cloud platform engineering and reliable APIs",
        },
    )
    assert summary.status_code == 200
    assert summary.json()["section"] == "summary"
    assert len(summary.json()["suggestions"]) == 3

    skills = client.post(
        "/api/v1/resumes/ai/suggest",
        json={
            "section": "skills",
            "context": "python fastapi aws docker",
        },
    )
    assert skills.status_code == 200
    assert {"Python", "FastAPI", "AWS", "Docker"}.issubset(set(skills.json()["suggestions"]))
