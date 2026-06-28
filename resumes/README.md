# Base Resume Library

This directory records the base resumes available for Rolecraft.

Private resume files are stored under `resumes/base/` and are intentionally ignored by
Git. The application imports each resume into `backend/storage/resume_library/`, which is
also private and ignored.

## Current Main Resume

The active base resume is:

`dilip-resume` - DILIP Resume (DOCX)

This is the preferred main profile because the application can preserve its native Word
styles, numbering, sections, and spacing while adding targeted points.

See [registry.json](registry.json) for the machine-readable selection.

## Adding Another Resume

1. Create a descriptive folder under `resumes/base/`, such as
   `cloud-platform-engineer/`.
2. Place the DOCX, PDF, or TXT resume in that folder.
3. Upload it from the Rolecraft Overview page.
4. Select it from **Main resume** when it should be used for matching and generation.
5. Update `registry.json` so project documentation reflects the intended default.

Uploading a new resume no longer deletes previous profiles.
