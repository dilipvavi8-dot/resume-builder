from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_job_does_not_lock_database():
    jobs = client.get("/jobs").json()
    assert jobs, "Expected at least one seeded job for regression coverage."
    job_id = jobs[0]["id"]
    response = client.post(f"/jobs/{job_id}/analyze")
    assert response.status_code == 200
    assert "match_score" in response.json()


def test_manual_jd_generate_and_approve_flow():
    analysis = client.post(
        "/manual-jd/analyze",
        json={
            "title": "DevOps Engineer",
            "company": "Backend Test Co",
            "location": "Remote",
            "jd_text": "DevOps engineer with AWS, Kubernetes, Terraform, GitHub Actions, Python, Prometheus, and Grafana.",
        },
    )
    assert analysis.status_code == 200
    manual_jd_id = analysis.json()["id"]

    draft = client.post(f"/manual-jd/generate-resume/{manual_jd_id}")
    assert draft.status_code == 200
    body = draft.json()
    if body["status"] != "pending_approval":
        assert body["status"] == "blocked_ats_gate"
        return

    approved = client.post(f"/resume-drafts/{body['id']}/approve")
    assert approved.status_code == 200
    payload = approved.json()
    assert payload["format"] == "docx"
    assert payload["download_url"].startswith("/resumes/")
