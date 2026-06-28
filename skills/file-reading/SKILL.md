---
name: file-reading
description: Route local Rolecraft resume, reference-resume, and job-description files to the correct safe reader. Use when an uploaded input is DOCX, PDF, or text and the workflow needs extraction before analysis or tailoring.
---

# File Reading

Use `backend/utils/text_parser.py` for local extraction. Accept DOCX, PDF, and text; reject empty or unreadable input with a clear error. Keep source files local and preserve the original bytes. Return extracted text plus filename and type for the evidence map.
