from contextlib import asynccontextmanager
from pathlib import Path
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database.db import get_db
from database.init_db import init_db
from services.file_service import (
    get_master_resume,
    list_resume_profiles,
    save_master_resume,
    select_master_resume,
)
from services.resume_parser import parse_resume
from services.resume_library import delete_resume_versions
from services.jd_analyzer import analyze_jd
from services.job_fetcher import run_fetch
from services.resume_generator import approve_resume_draft, create_resume_draft
from services.scheduler import scheduler, start_scheduler
from services.agent_monitor import record as record_agent_event, snapshot as agent_snapshot
from services.approval_router import decide as decide_approval, list_pending as list_pending_approvals, route_high_match
from services.notification_service import list_notifications, mark_read
from services.realtime import event_hub
from utils.text_parser import extract_text

load_dotenv()


def row_dict(row):
    item = dict(row)
    for key in ("required_skills", "preferred_skills", "missing_keywords"):
        if key in item:
            item[key] = [value for value in (item[key] or "").split(",") if value]
    return item


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    event_hub.start()
    start_scheduler()
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)


app = FastAPI(
    title="Rolecraft",
    description="Local-first job analysis and evidence-constrained resume drafting.",
    version="1.0.0",
    lifespan=lifespan,
)
frontend_origins = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
}
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(frontend_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ManualJD(BaseModel):
    title: str
    company: str = ""
    location: str = ""
    jd_text: str


class ApplicationCreate(BaseModel):
    job_id: int | None = None
    resume_id: int | None = None
    company: str
    role_title: str
    job_link: str = ""
    status: str = "Applied"
    applied_date: str | None = None
    recruiter_name: str = ""
    follow_up_date: str | None = None
    notes: str = ""


class ApplicationUpdate(BaseModel):
    status: str | None = None
    recruiter_name: str | None = None
    follow_up_date: str | None = None
    notes: str | None = None


class SourceCreate(BaseModel):
    source_name: str
    source_url: str
    source_type: str
    active: bool = True


class ApprovalDecision(BaseModel):
    decision: str
    reason: str = ""


class ResumeDeleteRequest(BaseModel):
    resume_ids: list[int]


@app.get("/health")
def health():
    return {"status": "ok", "database": "sqlite", "storage": "local", "scheduler": scheduler.running, "application_submission": "manual_only"}


@app.websocket("/ws/events")
async def workspace_events(websocket: WebSocket):
    await event_hub.connect(websocket)
    try:
        await websocket.send_json({"type": "agent_snapshot", "agents": agent_snapshot()})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        event_hub.disconnect(websocket)


@app.get("/dashboard/summary")
def dashboard_summary():
    with get_db() as db:
        row = db.execute(
            """SELECT COUNT(*) total_jobs,
            SUM(CASE WHEN posted_date=date('now','localtime') THEN 1 ELSE 0 END) todays_jobs,
            SUM(CASE WHEN match_score>=85 THEN 1 ELSE 0 END) strong_matches,
            SUM(CASE WHEN match_score>=70 AND match_score<85 THEN 1 ELSE 0 END) medium_matches,
            SUM(CASE WHEN match_score<70 THEN 1 ELSE 0 END) low_matches FROM jobs"""
        ).fetchone()
        result = dict(row)
        result["generated_resumes"] = db.execute("SELECT COUNT(*) count FROM resume_versions").fetchone()["count"]
        result["applications"] = db.execute("SELECT COUNT(*) count FROM applications").fetchone()["count"]
        return {key: value or 0 for key, value in result.items()}


@app.post("/resume/master/upload")
async def upload_master_resume(file: UploadFile = File(...)):
    content = await file.read()
    try:
        text = extract_text(file.filename or "resume.txt", content)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if not text.strip():
        raise HTTPException(400, "No readable text was found in the resume.")
    return save_master_resume(file.filename or "resume.txt", content, text)


@app.get("/resume/master")
def master_resume():
    metadata = get_master_resume()
    if not metadata:
        raise HTTPException(404, "No master resume uploaded yet.")
    return metadata


@app.get("/resume/master/parse")
def parse_master_resume():
    """Expose the local Phase 1 structure and independently derived search clusters."""
    text = get_master_resume()
    if not text:
        raise HTTPException(404, "No master resume uploaded yet.")
    from services.file_service import master_text
    return parse_resume(master_text())


@app.get("/resume/profiles")
def resume_profiles():
    return list_resume_profiles()


@app.post("/resume/profiles/{profile_id}/select")
def select_resume_profile(profile_id: str):
    try:
        return select_master_resume(profile_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.post("/manual-jd/analyze")
def manual_jd(payload: ManualJD):
    if not payload.jd_text.strip():
        raise HTTPException(400, "Paste a job description before analyzing it.")
    record_agent_event("JD Scanner", "working", "Extracting requirements from the pasted job description.")
    analysis = analyze_jd(payload.jd_text, title=payload.title, location=payload.location)
    record_agent_event("JD Scanner", "completed", "Role requirements and skills extracted.")
    record_agent_event("Match Scorer", "completed", f"Evidence-based match score calculated: {analysis['match_score']}%.")
    record_agent_event("Resume Updater Agent", "completed", "Built an evidence-backed resume update plan.")
    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO manual_jds (
              title, company, location, jd_text, required_skills, preferred_skills,
              experience_required, cloud_platform, role_type, match_score,
              missing_keywords, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                payload.title, payload.company, payload.location, payload.jd_text,
                ",".join(analysis["required_skills"]), ",".join(analysis["preferred_skills"]),
                analysis["experience_required"], analysis["cloud_platform"], analysis["role_type"],
                analysis["match_score"], ",".join(analysis["missing_keywords"]),
                analysis["recommendation"],
            ),
        )
        analysis["id"] = cursor.lastrowid
    return analysis


def create_resume_draft_record(job_id=None, manual_jd_id=None):
    table = "jobs" if job_id else "manual_jds"
    identifier = job_id or manual_jd_id
    with get_db() as db:
        row = db.execute(f"SELECT * FROM {table} WHERE id=?", (identifier,)).fetchone()
        if not row:
            raise HTTPException(404, "Job description not found.")
        item = row_dict(row)
        jd_text = item["job_description"] if job_id else item["jd_text"]
        analysis = analyze_jd(
            jd_text,
            title=item["title"],
            location=item.get("location") or "",
        )
        if job_id:
            db.execute(
                """UPDATE jobs SET required_skills=?, preferred_skills=?,
                experience_required=?, cloud_platform=?, role_type=?, match_score=?,
                missing_keywords=?, recommendation=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?""",
                (
                    ",".join(analysis["required_skills"]),
                    ",".join(analysis["preferred_skills"]),
                    analysis["experience_required"],
                    analysis["cloud_platform"],
                    analysis["role_type"],
                    analysis["match_score"],
                    ",".join(analysis["missing_keywords"]),
                    analysis["recommendation"],
                    job_id,
                ),
            )
        else:
            db.execute(
                """UPDATE manual_jds SET required_skills=?, preferred_skills=?,
                experience_required=?, cloud_platform=?, role_type=?, match_score=?,
                missing_keywords=?, recommendation=? WHERE id=?""",
                (
                    ",".join(analysis["required_skills"]),
                    ",".join(analysis["preferred_skills"]),
                    analysis["experience_required"],
                    analysis["cloud_platform"],
                    analysis["role_type"],
                    analysis["match_score"],
                    ",".join(analysis["missing_keywords"]),
                    analysis["recommendation"],
                    manual_jd_id,
                ),
            )

    record_agent_event("Resume Tailoring Agent", "working", "Creating an evidence-constrained resume draft.", job_id)
    record_agent_event("Resume Updater Agent", "completed", "Mapped JD requirements to resume evidence and gaps.", job_id)
    try:
        path, report = create_resume_draft(
            item.get("company") or "ManualJD",
            item["title"],
            jd_text,
            analysis,
        )
    except ValueError as exc:
        record_agent_event("Resume Tailoring Agent", "failed", str(exc), job_id)
        raise HTTPException(400, str(exc)) from exc
    record_agent_event("Resume Tailoring Agent", "completed", f"Completed {len(report['changes'])} evidence-constrained edits.", job_id)
    quality_status = "completed" if report["status"] == "approved" else "needs_attention"
    record_agent_event("Resume Quality Monitor", quality_status, "Resume evidence and formatting verification completed.", job_id)
    draft_status = "pending_approval" if report["ats_gate_passed"] and report["status"] == "approved" else "blocked_ats_gate"
    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO resume_drafts (
              job_id, manual_jd_id, draft_name, draft_path, match_score, ats_score, company,
              role_title, status, generation_report
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job_id,
                manual_jd_id,
                path.name,
                str(path),
                analysis["match_score"],
                report["ats_score"],
                item.get("company"),
                item["title"],
                draft_status,
                json.dumps(report),
            ),
        )
        return {
            "id": cursor.lastrowid,
            "draft_name": path.name,
            "status": draft_status,
            "generation_report": report,
        }


@app.post("/manual-jd/generate-resume/{manual_jd_id}")
def generate_manual_resume(manual_jd_id: int):
    return create_resume_draft_record(manual_jd_id=manual_jd_id)


@app.get("/jobs")
def list_jobs(role: str | None = None, cloud_platform: str | None = None, match_score: int | None = None, status: str | None = None):
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if role:
        query += " AND role_type=?"
        params.append(role)
    if cloud_platform:
        query += " AND cloud_platform=?"
        params.append(cloud_platform)
    if match_score is not None:
        query += " AND match_score>=?"
        params.append(match_score)
    if status:
        query += " AND status=?"
        params.append(status)
    query += " ORDER BY posted_date DESC, match_score DESC"
    with get_db() as db:
        return [row_dict(row) for row in db.execute(query, params).fetchall()]


@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Job not found.")
        return row_dict(row)


@app.post("/jobs/fetch")
def fetch_jobs():
    record_agent_event("JD Scanner", "working", "Refreshing the permitted local job sources.")
    result = run_fetch()
    record_agent_event("JD Scanner", "completed", f"Processed {result['jobs_found']} job listings.")
    record_agent_event("Match Scorer", "completed", "Updated deterministic match scores for refreshed jobs.")
    with get_db() as db:
        high_matches = db.execute("SELECT id, match_score, employment_type, company, title FROM jobs WHERE match_score>=90").fetchall()
    for job in high_matches:
        route_high_match(job["id"], job["match_score"], job["employment_type"], job["company"], job["title"])
    return result


@app.post("/jobs/{job_id}/analyze")
def analyze_job(job_id: int):
    record_agent_event("JD Scanner", "working", "Re-analyzing the selected listing.", job_id)
    with get_db() as db:
        row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Job not found.")
        row_data = dict(row)
        analysis = analyze_jd(
            row_data["job_description"],
            title=row_data["title"],
            location=row_data["location"] or "",
        )
        db.execute(
            """UPDATE jobs SET required_skills=?, preferred_skills=?, experience_required=?,
            cloud_platform=?, role_type=?, match_score=?, missing_keywords=?, recommendation=?,
            updated_at=CURRENT_TIMESTAMP WHERE id=?""",
            (
                ",".join(analysis["required_skills"]), ",".join(analysis["preferred_skills"]),
                analysis["experience_required"], analysis["cloud_platform"], analysis["role_type"],
                analysis["match_score"], ",".join(analysis["missing_keywords"]),
                analysis["recommendation"], job_id,
            ),
        )
    record_agent_event("JD Scanner", "completed", "Listing requirements refreshed.", job_id)
    record_agent_event("Match Scorer", "completed", f"Evidence-based match score calculated: {analysis['match_score']}%.", job_id)
    route_high_match(job_id, analysis["match_score"], row_data["employment_type"], row_data["company"], row_data["title"])
    return analysis


@app.get("/agents/status")
def agents_status():
    return agent_snapshot()


@app.get("/notifications")
def notifications():
    return list_notifications()


@app.post("/notifications/{notification_id}/read")
def read_notification(notification_id: int):
    if not mark_read(notification_id):
        raise HTTPException(404, "Notification not found.")
    return {"id": notification_id, "is_read": True}


@app.get("/fte-approvals")
def fte_approvals():
    return list_pending_approvals()


@app.post("/fte-approvals/{approval_id}/decision")
def fte_approval_decision(approval_id: int, payload: ApprovalDecision):
    try:
        result = decide_approval(approval_id, payload.decision, payload.reason)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if not result:
        raise HTTPException(404, "Approval request not found.")
    return result


@app.post("/jobs/{job_id}/generate-resume")
def generate_job_resume(job_id: int):
    return create_resume_draft_record(job_id=job_id)


def draft_dict(row):
    item = dict(row)
    item["generation_report"] = json.loads(item["generation_report"])
    return item


@app.get("/resume-drafts/{draft_id}")
def get_resume_draft(draft_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM resume_drafts WHERE id=?", (draft_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Resume draft not found.")
    return draft_dict(row)


@app.get("/resume-drafts/{draft_id}/download")
def download_resume_draft(draft_id: int):
    with get_db() as db:
        row = db.execute("SELECT draft_name, draft_path FROM resume_drafts WHERE id=?", (draft_id,)).fetchone()
    if not row or not Path(row["draft_path"]).exists():
        raise HTTPException(404, "Resume draft file not found.")
    return FileResponse(row["draft_path"], filename=row["draft_name"])


@app.post("/resume-drafts/{draft_id}/approve")
def approve_draft(draft_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM resume_drafts WHERE id=?", (draft_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Resume draft not found.")
        draft = draft_dict(row)
        if draft["status"] != "pending_approval" or not draft["generation_report"].get("ats_gate_passed"):
            raise HTTPException(400, "A truthfulness-verified draft must meet the 95% ATS gate before final output.")
        report = draft["generation_report"]
        path = approve_resume_draft(draft["draft_path"], draft["company"] or "ManualJD", draft["role_title"])
        cursor = db.execute(
            """INSERT INTO resume_versions (
              job_id, manual_jd_id, resume_name, docx_path, pdf_path, match_score, company,
              role_title, generation_status, requirement_coverage,
              truthfulness_score, generation_report
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                draft["job_id"], draft["manual_jd_id"], path.name, str(path), None,
                draft["match_score"], draft["company"], draft["role_title"],
                "approved", report["requirement_coverage"], report["truthfulness_score"],
                json.dumps(report),
            ),
        )
        db.execute(
            "UPDATE resume_drafts SET status='approved', approved_at=CURRENT_TIMESTAMP WHERE id=?",
            (draft_id,),
        )
        version_id = cursor.lastrowid
        return {
            "id": version_id,
            "resume_name": path.name,
            "download_url": f"/resumes/{version_id}/download",
            "format": "docx",
            "generation_report": report,
        }


@app.get("/resumes")
def resumes():
    with get_db() as db:
        items = []
        for row in db.execute(
            "SELECT * FROM resume_versions ORDER BY created_at DESC"
        ).fetchall():
            item = dict(row)
            item["generation_report"] = json.loads(item["generation_report"]) if item.get(
                "generation_report"
            ) else None
            items.append(item)
        return items


@app.get("/resumes/{resume_id}/download")
def download_resume(resume_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM resume_versions WHERE id=?", (resume_id,)).fetchone()
        if not row or not Path(row["docx_path"]).exists():
            raise HTTPException(404, "Resume file not found.")
    return FileResponse(row["docx_path"], filename=row["resume_name"])


@app.get("/resumes/{resume_id}/download/pdf")
def download_resume_pdf(resume_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM resume_versions WHERE id=?", (resume_id,)).fetchone()
    if not row or not row["pdf_path"] or not Path(row["pdf_path"]).exists():
        raise HTTPException(404, "Resume PDF not found.")
    return FileResponse(row["pdf_path"], filename=f"{Path(row['resume_name']).stem}.pdf", media_type="application/pdf")


@app.delete("/resumes")
def delete_resumes(payload: ResumeDeleteRequest):
    try:
        return delete_resume_versions(payload.resume_ids)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/applications")
def applications():
    with get_db() as db:
        return [dict(row) for row in db.execute("SELECT * FROM applications ORDER BY created_at DESC").fetchall()]


@app.post("/applications")
def create_application(payload: ApplicationCreate):
    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO applications (
              job_id, resume_id, company, role_title, job_link, status, applied_date,
              recruiter_name, follow_up_date, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                payload.job_id, payload.resume_id, payload.company, payload.role_title,
                payload.job_link, payload.status, payload.applied_date, payload.recruiter_name,
                payload.follow_up_date, payload.notes,
            ),
        )
        if payload.job_id:
            db.execute("UPDATE jobs SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (payload.status, payload.job_id))
        return {"id": cursor.lastrowid, **payload.model_dump()}


@app.put("/applications/{application_id}")
def update_application(application_id: int, payload: ApplicationUpdate):
    fields = {key: value for key, value in payload.model_dump().items() if value is not None}
    if not fields:
        raise HTTPException(400, "No changes supplied.")
    assignments = ", ".join(f"{key}=?" for key in fields)
    with get_db() as db:
        cursor = db.execute(
            f"UPDATE applications SET {assignments}, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            [*fields.values(), application_id],
        )
        if not cursor.rowcount:
            raise HTTPException(404, "Application not found.")
        return {"id": application_id, **fields}


@app.get("/sources")
def sources():
    with get_db() as db:
        return [dict(row) for row in db.execute("SELECT * FROM job_sources ORDER BY source_name").fetchall()]


@app.post("/sources")
def create_source(payload: SourceCreate):
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO job_sources (source_name, source_url, source_type, active) VALUES (?, ?, ?, ?)",
            (payload.source_name, payload.source_url, payload.source_type, int(payload.active)),
        )
        return {"id": cursor.lastrowid, **payload.model_dump()}


@app.put("/sources/{source_id}")
def update_source(source_id: int, payload: SourceCreate):
    with get_db() as db:
        cursor = db.execute(
            "UPDATE job_sources SET source_name=?, source_url=?, source_type=?, active=? WHERE id=?",
            (payload.source_name, payload.source_url, payload.source_type, int(payload.active), source_id),
        )
        if not cursor.rowcount:
            raise HTTPException(404, "Source not found.")
        return {"id": source_id, **payload.model_dump()}
