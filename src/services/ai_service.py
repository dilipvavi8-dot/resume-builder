"""AI suggestion service — stub with rule-based suggestions.
Replace with OpenAI / Bedrock / local Ollama integration."""

from typing import List, Optional


class AISuggestionService:
    """Provides AI-style writing suggestions for resume sections."""

    SUMMARY_TEMPLATES = [
        "Results-driven {role} with {years}+ years of experience in {domain}.",
        "Innovative {role} specializing in {domain}, delivering measurable outcomes.",
        "Strategic {role} with a track record of {achievement} in {domain}.",
    ]

    BULLET_STARTERS = [
        "Led cross-functional team to ",
        "Reduced operational costs by ",
        "Increased system performance by ",
        "Designed and implemented ",
        "Collaborated with stakeholders to ",
        "Delivered ",
        "Architected scalable solution for ",
        "Automated ",
    ]

    SKILL_SUGGESTIONS = [
        "Python", "FastAPI", "React", "TypeScript", "AWS", "Docker",
        "Kubernetes", "Terraform", "PostgreSQL", "Redis", "GraphQL",
        "CI/CD", "Agile", "REST APIs", "Microservices",
    ]

    def suggest(self, section: str, context: str, current_text: Optional[str] = None) -> List[str]:
        if section == "summary":
            return [
                f"Experienced professional with expertise in {context[:50]}.",
                f"Results-oriented specialist delivering value through {context[:40]}.",
                f"Strategic thinker with deep knowledge of {context[:40]} and proven success.",
            ]
        elif section == "bullets":
            return [
                f"{starter}{context[:30]}..." for starter in self.BULLET_STARTERS[:4]
            ]
        elif section == "skills":
            keywords = context.lower().split()
            matched = [s for s in self.SKILL_SUGGESTIONS if s.lower() in keywords]
            return matched if matched else self.SKILL_SUGGESTIONS[:8]
        else:
            return [f"Consider highlighting your {section} achievements clearly."]
