import re

ROLE_TERMS = {
    "DevOps": ["devops", "ci/cd", "continuous integration", "deployment engineer"],
    "SRE": ["site reliability", "sre", "reliability engineer", "slo", "error budget"],
    "Platform": ["platform engineer", "platform engineering", "developer platform"],
    "AI Engineer": ["ai engineer", "artificial intelligence", "llm", "generative ai", "rag"],
    "AI Ops": ["aiops", "mlops", "machine learning operations"],
    "Cloud Engineer": ["cloud engineer", "cloud infrastructure", "aws engineer", "azure engineer", "gcp engineer"],
    "Infrastructure": ["infrastructure engineer", "systems engineer", "infrastructure automation"],
    "Observability": ["observability engineer", "monitoring engineer", "telemetry"],
    "Automation": ["automation engineer", "infrastructure automation"],
}

SKILL_ALIASES = {
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Docker": ["docker", "containerization"],
    "Terraform": ["terraform"],
    "Ansible": ["ansible"],
    "Jenkins": ["jenkins"],
    "GitHub Actions": ["github actions", "github workflow"],
    # A GitLab listing under a CI/CD tools section is evidence of GitLab CI use.
    # This lets the tailorer promote the existing, supported skill in place.
    "GitLab CI": ["gitlab ci", "gitlab pipeline", "gitlab"],
    "Azure DevOps": ["azure devops"],
    "Argo CD": ["argo cd", "argocd"],
    "Python": ["python", "boto3"],
    "Bash": ["bash", "shell scripting"],
    "PowerShell": ["powershell", "power shell"],
    "Prometheus": ["prometheus"],
    "Grafana": ["grafana"],
    "Datadog": ["datadog"],
    "Splunk": ["splunk"],
    "OpenTelemetry": ["opentelemetry", "open telemetry"],
    "ELK": ["elk", "elasticsearch", "logstash", "kibana"],
    "Linux": ["linux", "ubuntu", "red hat", "centos"],
    "Helm": ["helm"],
    "EKS": ["eks", "elastic kubernetes service"],
    "AKS": ["aks", "azure kubernetes service"],
    "GKE": ["gke", "google kubernetes engine"],
    "ECS": ["ecs", "fargate"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment", "deployment pipeline"],
    "SRE": ["site reliability", "sre", "slo", "error budget"],
    "Incident Management": ["incident management", "incident response", "incident triage", "on-call", "root cause analysis", "rca"],
    "Security": ["security", "iam", "rbac", "hardening", "compliance"],
    "Networking": ["networking", "vpc", "dns", "vpn", "subnet", "load balancer"],
    "CloudFormation": ["cloudformation"],
    "REST API": ["rest api", "restful api", "web api", "apis"],
    "FastAPI": ["fastapi"],
    "React": ["react", "react.js", "reactjs"],
    "TypeScript": ["typescript"],
    "JavaScript": ["javascript", "java script"],
    "SQL": ["sql", "postgresql", "mysql", "sql server"],
    "LLM": ["llm", "large language model"],
    "Generative AI": ["generative ai", "genai"],
    "RAG": ["rag", "retrieval augmented generation"],
    "LangChain": ["langchain"],
    "Vector Database": ["vector database", "vector db", "pinecone", "weaviate", "faiss"],
    "Machine Learning": ["machine learning", "ml model"],
    "MLOps": ["mlops", "model deployment", "model monitoring"],
    "OpenAI": ["openai", "gpt"],
    "Bedrock": ["bedrock"],
    "SageMaker": ["sagemaker"],
    # Mainframe modernization and enterprise DevOps vocabulary. These must be
    # independently detected so an unproven Z-platform requirement remains a gap.
    "Endevor": ["endevor", "ca endevor"],
    "IBM Z": ["ibm z", "mainframe", "z/os", "zos"],
    "TSO": ["tso"],
    "ISPF": ["ispf"],
    "JCL": ["jcl"],
    "REXX": ["rexx"],
    "COBOL": ["cobol"],
    "PL/I": ["pl/i", "pli"],
    "VSAM": ["vsam", "qsam"],
    "DB2": ["db2"],
    "ADDI": ["addi"],
    "IDz": ["idz", "ibm developer for z"],
    "zD&T": ["zd&t", "zdt"],
    "DBB": ["dbb", "dependency based build"],
    "Git": ["git"],
    "Wazi Deploy": ["wazi deploy"],
    "UCD": ["ucd", "urbancode deploy"],
    "Artifactory": ["artifactory"],
    "uDeploy": ["udeploy", "urban code deploy"],
}

PLATFORM_SKILLS = {"Kubernetes", "Docker", "Terraform", "Ansible", "Jenkins", "GitHub Actions", "GitLab CI", "Azure DevOps", "Argo CD", "Helm", "CI/CD"}
OPS_SKILLS = {"Prometheus", "Grafana", "Datadog", "Splunk", "OpenTelemetry", "ELK", "SRE", "Incident Management", "Security"}
CLOUD_SKILLS = {"AWS", "Azure", "GCP"}
TITLE_STOP_WORDS = {"senior", "sr", "lead", "principal", "engineer", "engineering", "developer", "specialist", "administrator", "architect"}


def _contains(text: str, phrase: str) -> bool:
    if re.fullmatch(r"[a-z0-9 ]+", phrase):
        return re.search(rf"\b{re.escape(phrase)}\b", text) is not None
    return phrase in text


def detect_skills(text: str) -> list[str]:
    lowered = text.lower()
    return [
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if any(_contains(lowered, alias) for alias in aliases)
    ]


def _preferred_skills(jd_text: str) -> list[str]:
    preferred_lines = [
        line for line in jd_text.splitlines()
        if re.search(r"\b(preferred|nice to have|desired|bonus|plus)\b", line, re.I)
    ]
    return detect_skills("\n".join(preferred_lines))


def _role_type(title: str, jd_text: str) -> str:
    title_lower = title.lower()
    target = f"{title}\n{jd_text}".lower()
    scores = {
        role: sum(
            3 if _contains(title_lower, term) else 1
            for term in terms
            if _contains(target, term)
        )
        for role, terms in ROLE_TERMS.items()
    }
    return max(scores, key=scores.get) if max(scores.values(), default=0) else "Infrastructure"


def _resume_roles(resume_text: str) -> set[str]:
    lowered = resume_text.lower()
    return {
        role for role, terms in ROLE_TERMS.items()
        if any(_contains(lowered, term) for term in terms)
    }


def _experience_years(text: str) -> int | None:
    values = [
        int(match)
        for match in re.findall(r"(\d+)\+?\s*(?:years|yrs)", text.lower())
        if int(match) <= 40
    ]
    return max(values) if values else None


def _title_tokens(title: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9+#]+", title.lower())
        if token not in TITLE_STOP_WORDS and len(token) > 1
    }


def _recommendation(score: int) -> str:
    if score >= 85:
        return "Strong Apply"
    if score >= 70:
        return "Apply After Resume Update"
    if score >= 50:
        return "Weak Match"
    return "Skip"


def analyze_text(
    jd_text: str,
    resume_text: str = "",
    title: str = "",
    location: str = "",
) -> dict:
    preferred = _preferred_skills(jd_text)
    all_jd_skills = detect_skills(jd_text)
    required = [skill for skill in all_jd_skills if skill not in preferred]
    resume_skills = set(detect_skills(resume_text))
    matching = [skill for skill in required if skill in resume_skills]
    missing = [skill for skill in required if skill not in resume_skills]

    role = _role_type(title, jd_text)
    resume_roles = _resume_roles(resume_text)
    title_tokens = _title_tokens(title)
    resume_title_tokens = _title_tokens(resume_text)
    token_overlap = len(title_tokens & resume_title_tokens) / max(len(title_tokens), 1)
    if role in resume_roles:
        title_ratio = 1.0
    elif token_overlap:
        title_ratio = min(0.8, token_overlap)
    elif role in {"Cloud Engineer", "Infrastructure", "Automation"} and resume_roles & {"DevOps", "SRE", "Platform"}:
        title_ratio = 0.6
    else:
        title_ratio = 0.2

    cloud_required = [skill for skill in required if skill in CLOUD_SKILLS]
    platform_required = [skill for skill in required if skill in PLATFORM_SKILLS]
    ops_required = [skill for skill in required if skill in OPS_SKILLS]
    requested_years = _experience_years(jd_text)
    resume_years = _experience_years(resume_text)

    categories = [
        ("Role relevance", 20, title_ratio, True),
        ("Required skills", 25, len(matching) / max(len(required), 1), bool(required)),
        ("Cloud platform", 15, len(set(cloud_required) & resume_skills) / max(len(cloud_required), 1), bool(cloud_required)),
        ("Platform and delivery", 15, len(set(platform_required) & resume_skills) / max(len(platform_required), 1), bool(platform_required)),
        (
            "Experience",
            10,
            min(1.0, (resume_years or 0) / requested_years) if requested_years else 0,
            requested_years is not None,
        ),
        ("Reliability, observability, security", 10, len(set(ops_required) & resume_skills) / max(len(ops_required), 1), bool(ops_required)),
    ]

    # Location is only scored when the resume explicitly contains the requested location
    # or both documents explicitly state remote work.
    location_match = "remote" in location.lower() and "remote" in resume_text.lower()
    categories.append(("Location or remote", 5, 1.0 if location_match else 0.0, location_match))

    available = sum(weight for _, weight, _, applicable in categories if applicable)
    earned = sum(weight * ratio for _, weight, ratio, applicable in categories if applicable)
    score = round(100 * earned / max(available, 1))
    score_notes = []
    required_ratio = len(matching) / max(len(required), 1)
    if required and required_ratio < 0.5:
        score = min(score, 59)
        score_notes.append("Score capped because fewer than half of the required skills are evidenced.")
    ai_core = {"LLM", "Generative AI", "RAG", "LangChain", "Vector Database", "Machine Learning", "MLOps", "OpenAI", "Bedrock", "SageMaker"}
    requested_ai_core = set(required) & ai_core
    matched_ai_core = requested_ai_core & resume_skills
    if role in {"AI Engineer", "AI Ops"} and requested_ai_core and len(matched_ai_core) / len(requested_ai_core) < 0.5:
        score = min(score, 69)
        score_notes.append("Score capped because core AI requirements are not sufficiently evidenced.")
    if title_ratio < 0.5:
        score = min(score, 69)
        score_notes.append("Score capped because the target role is outside the resume's demonstrated role family.")
    breakdown = [
        {
            "category": name,
            "earned": round(weight * ratio, 1) if applicable else None,
            "possible": weight,
            "applicable": applicable,
        }
        for name, weight, ratio, applicable in categories
    ]

    cloud_hits = [cloud for cloud in ("AWS", "Azure", "GCP") if cloud in all_jd_skills]
    cloud = "Multi-cloud" if len(cloud_hits) > 1 else (cloud_hits[0] if cloud_hits else "Unknown")
    experience = f"{requested_years}+ years" if requested_years is not None else "Not specified"

    return {
        "required_skills": required,
        "preferred_skills": preferred,
        "matching_skills": matching,
        "experience_required": experience,
        "resume_experience": f"{resume_years}+ years" if resume_years is not None else "Not detected",
        "cloud_platform": cloud,
        "role_type": role,
        "match_score": score,
        "score_breakdown": breakdown,
        "score_notes": score_notes,
        "missing_keywords": missing,
        "recommendation": _recommendation(score),
    }
