"""Export service — converts ResumeData to various formats"""

from src.models.resume import ResumeData


class ExportService:
    def to_text(self, resume: ResumeData) -> str:
        lines = []
        c = resume.contact

        lines.append(c.full_name.upper())
        contact_parts = [c.email]
        if c.phone:
            contact_parts.append(c.phone)
        if c.location:
            contact_parts.append(c.location)
        lines.append(" | ".join(contact_parts))
        if c.linkedin:
            lines.append(f"LinkedIn: {c.linkedin}")
        if c.github:
            lines.append(f"GitHub: {c.github}")
        lines.append("")

        if resume.summary:
            lines.append("SUMMARY")
            lines.append("-" * 40)
            lines.append(resume.summary)
            lines.append("")

        if resume.work_experience:
            lines.append("WORK EXPERIENCE")
            lines.append("-" * 40)
            for job in resume.work_experience:
                lines.append(f"{job.title} — {job.company}")
                lines.append(f"{job.start_date} to {job.end_date or 'Present'}")
                for bullet in job.bullets:
                    lines.append(f"  • {bullet}")
                lines.append("")

        if resume.education:
            lines.append("EDUCATION")
            lines.append("-" * 40)
            for edu in resume.education:
                lines.append(f"{edu.degree} — {edu.institution}")
                if edu.field_of_study:
                    lines.append(f"  Field: {edu.field_of_study}")
                if edu.end_date:
                    lines.append(f"  Graduated: {edu.end_date}")
                lines.append("")

        if resume.skills:
            lines.append("SKILLS")
            lines.append("-" * 40)
            lines.append(", ".join(resume.skills))
            lines.append("")

        if resume.projects:
            lines.append("PROJECTS")
            lines.append("-" * 40)
            for proj in resume.projects:
                lines.append(f"{proj.name}")
                lines.append(f"  {proj.description}")
                if proj.technologies:
                    lines.append(f"  Tech: {', '.join(proj.technologies)}")
                lines.append("")

        if resume.certifications:
            lines.append("CERTIFICATIONS")
            lines.append("-" * 40)
            for cert in resume.certifications:
                lines.append(f"{cert.name} — {cert.issuer} ({cert.date_issued or 'N/A'})")
            lines.append("")

        return "\n".join(lines)
