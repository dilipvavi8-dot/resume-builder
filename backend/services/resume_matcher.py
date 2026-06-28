from utils.scoring import analyze_text


def score_resume(jd_text: str, resume_text: str) -> dict:
    return analyze_text(jd_text, resume_text)
