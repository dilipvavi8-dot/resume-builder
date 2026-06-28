---
name: resume-updater-agent
description: Create an evidence-first update plan for an existing DOCX, PDF, or text resume against a job description or optional reference resume. Use when Rolecraft needs to extract JD requirements, calculate a truthful weighted baseline, identify gaps, propose client-specific edits, or prepare a reviewable resume draft.
---

# Resume Updater Agent

## Workflow

1. Parse the selected base resume and full JD; accept DOCX, PDF, or text through Rolecraft file parsing.
2. Separate required and preferred skills, then calculate the weighted baseline: required = 3, preferred = 2.
3. Map each JD requirement to source evidence, an existing skills row, or a client bullet.
4. Draft only evidence-backed summary, skills, and bullet edits. Use JD wording where it describes demonstrated work.
5. Leave unsupported requirements as explicit gaps. A 95% score is never a reason to invent skills, metrics, projects, or clients.
6. Require review of the before/after diff and monitor approval before creating the final DOCX.

## DOCX Safety

Preserve the source layout, section breaks, employers, dates, and metrics. Repair malformed source bullets only when their meaning is unchanged. Do not insert generic skills blocks or rebuild the document template.
