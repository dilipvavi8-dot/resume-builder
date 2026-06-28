# Rolecraft Verification Matrix

| Capability | API or artifact | UI |
|---|---|---|
| Backend readiness | `GET /health` | Dashboard loads data |
| Dashboard metrics | `GET /dashboard/summary` | Metric cards |
| Base resumes | upload, profile list, and active selection | Overview upload and selector |
| Job discovery | `POST /jobs/fetch`, `GET /jobs` | Job feed and score rings |
| Manual analysis | `POST /manual-jd/analyze` | JD studio result panel |
| Resume generation | generate endpoint and DOCX file | Resume download action |
| Resume history | `GET /resumes` | Resume library |
| Application tracking | create/update/list endpoints | Tracker status selector |
| Scheduler | health reports scheduler active | No dedicated UI |

## High-Risk Regressions

- Existing jobs keep stale scores after the master resume changes.
- A duplicate fetch creates duplicate rows.
- DOCX generation overwrites an earlier version.
- A missing master resume causes an unhelpful server error.
- Frontend CORS fails when Next.js selects port `3001`.
- Landing animation leaves important content hidden.
- Narrow layouts create horizontal overflow.

## Visual Routes

Inspect `/`, `/dashboard`, `/jobs`, `/manual-jd`, `/resumes`, and `/tracker`.
