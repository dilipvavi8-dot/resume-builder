"""Deterministic, evidence-first plan for a JD-specific resume update."""

import re

from services.resume_parser import parse_resume
from utils.scoring import detect_skills


def build_update_plan(jd_text: str, title: str, analysis: dict, resume_text: str) -> dict:
    resume_skills = set(detect_skills(resume_text))
    required = analysis.get("required_skills", [])
    preferred = analysis.get("preferred_skills", [])
    required_match = [skill for skill in required if skill in resume_skills]
    preferred_match = [skill for skill in preferred if skill in resume_skills]
    total_weight = (3 * len(required)) + (2 * len(preferred))
    matched_weight = (3 * len(required_match)) + (2 * len(preferred_match))
    weighted_score = round(100 * matched_weight / max(total_weight, 1))
    missing_required = [skill for skill in required if skill not in resume_skills]
    missing_preferred = [skill for skill in preferred if skill not in resume_skills]
    summary_mismatch = bool(title.strip()) and title.lower() not in resume_text.lower()
    jd_lower = jd_text.lower()
    action_verbs = [verb for verb in ("lead", "architect", "design", "implement", "optimize", "automate", "develop", "collaborate") if verb in jd_lower]
    industry_terms = [term for term in ("telecommunications", "healthcare", "financial", "compliance", "enterprise") if term in jd_lower]
    years = [int(value) for value in re.findall(r"(\d+)\+?\s*years", jd_lower)]
    parsed = parse_resume(resume_text)
    role_keywords = [title] if title.strip() else []
    # The score is deliberately evidence-only. A keyword may be mirrored only when it
    # already appears in the selected master resume.
    client_gaps = []
    for client in parsed["clients"]:
        client_stack = set(client["stack"])
        client_gaps.append({
            "client": client["employer"],
            "existing_stack": client["stack"],
            "missing_required": [skill for skill in required if skill not in client_stack],
            "missing_preferred": [skill for skill in preferred if skill not in client_stack],
            "missing_keywords": [skill for skill in role_keywords if skill.lower() not in " ".join(client["bullets"]).lower()],
            "weak_bullets": client["bullets"][:3],
            "terminology_map": {},
        })
    return {
        "baseline_weighted_score": weighted_score,
        "target_score": 95,
        "target_status": "blocked_by_missing_evidence" if missing_required else "potentially_achievable_with_rewrites",
        "jd_analysis": {
            "role_keywords": role_keywords,
            "soft_skills": [term for term in ("collaboration", "communication", "leadership") if term in jd_lower],
            "industry_terms": industry_terms,
            "action_verbs": action_verbs,
            "years_experience": {"overall": max(years)} if years else {},
            "education_req": "Bachelor's degree" if "bachelor" in jd_lower else "",
            "certifications_req": ["AWS Certified"] if "aws certified" in jd_lower else [],
        },
        "required_skills": required,
        "preferred_skills": preferred,
        "missing_required": missing_required,
        "missing_preferred": missing_preferred,
        "client_gaps": client_gaps,
        "global_gaps": {
            "missing_keywords": missing_required + missing_preferred,
            "summary_needs_rewrite": summary_mismatch,
            "skills_section_gaps": missing_required + missing_preferred,
            "certifications_flagged": [item for item in ["AWS Certified"] if item in jd_text and item not in resume_text],
        },
        "resume_structure": parsed,
        "weak_sections": [
            section for section, weak in {
                "Professional Summary": summary_mismatch,
                "Technical Skills": bool(required_match),
                "Work Experience": bool(required_match),
            }.items() if weak
        ],
        "strategy": [
            "Mirror JD wording only where the selected base resume provides evidence.",
            "Keep original bullets untouched; add a separately logged evidence-backed alignment bullet only when source evidence exists.",
            "Keep unsupported requirements visible as gaps instead of adding claims.",
        ],
    }
