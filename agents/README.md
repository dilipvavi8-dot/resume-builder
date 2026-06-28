# Project Agents

This directory contains both engineering contributor profiles and the runtime resume
agents used by Rolecraft.

| Agent | Primary ownership | Use for |
|---|---|---|
| [Principal Architect](principal-architect.md) | System design and contracts | Cross-layer features, schema changes, provider architecture |
| [Frontend Engineer](frontend-engineer.md) | Next.js product experience | Pages, components, responsive UI, accessibility |
| [Backend and AI Engineer](backend-ai-engineer.md) | FastAPI and domain logic | APIs, analysis, scoring, resume files, job sources |
| [QA and DevOps Engineer](qa-devops-engineer.md) | Reliability and local runtime | Builds, API workflows, browser checks, setup docs |

## Runtime Resume Agents

| Agent | Responsibility | Runtime output |
|---|---|---|
| [Resume Tailoring Agent](resume-tailoring-agent.md) | Rewrite supported summary, skills, and experience content in place | Change log and task completion |
| [Resume Updater Agent](resume-updater-agent.md) | Build evidence-backed JD gap and update strategy | Weighted baseline, gaps, and safe edit plan |
| [Resume Quality Monitor](resume-quality-monitor.md) | Verify evidence, formatting, metrics, and JD coverage; request revisions | Approval, coverage, truthfulness, and gap report |

These two agents execute during DOCX generation. The monitor can reject a draft and send
corrective directives back to the tailoring agent for up to two additional passes.

## Recommended Handoff

1. The Principal Architect identifies affected contracts and invariants.
2. The owning implementation agent makes the smallest coherent change.
3. The QA and DevOps Engineer verifies the user workflow and local artifacts.
4. Documentation is updated in the same change when behavior or setup changes.

For a narrow frontend or backend fix, skip the architect role unless the API contract,
database schema, security model, or storage behavior changes.
