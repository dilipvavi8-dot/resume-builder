"""Resume export endpoints (JSON, plain text)"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse, JSONResponse
from src.services.resume_service import ResumeService
from src.services.export_service import ExportService

router = APIRouter()
resume_service = ResumeService()
export_service = ExportService()


@router.get(
    "/resumes/{resume_id}/export/json",
    summary="Export resume as JSON",
)
async def export_json(resume_id: str):
    resume = resume_service.get(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found",
        )
    return JSONResponse(content=resume.model_dump())


@router.get(
    "/resumes/{resume_id}/export/text",
    summary="Export resume as plain text",
    response_class=PlainTextResponse,
)
async def export_text(resume_id: str):
    resume = resume_service.get(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found",
        )
    text = export_service.to_text(resume)
    return PlainTextResponse(content=text)
