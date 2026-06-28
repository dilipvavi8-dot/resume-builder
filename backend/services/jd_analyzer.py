from services.file_service import master_text
from services.resume_update_planner import build_update_plan
from utils.scoring import analyze_text


def analyze_jd(jd_text: str, title: str = "", location: str = "") -> dict:
    resume_text = master_text()
    analysis = analyze_text(jd_text, resume_text, title=title, location=location)
    analysis["resume_update_plan"] = build_update_plan(jd_text, title, analysis, resume_text)
    return analysis
