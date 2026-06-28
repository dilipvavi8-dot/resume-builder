"""Resume CRUD and AI suggestion endpoints"""

import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List

from src.models.resume import (
    ResumeData,
    ResumeResponse,
    AISuggestRequest,
    AISuggestResponse,
)
from src.services.resume_service import ResumeService
from src.services.ai_service import AISuggestionService

router = APIRouter()
resume_service = ResumeService()
ai_service = AISuggestionService()


@router.post(
    "/resumes",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new resume",
)
async def create_resume(resume_data: ResumeData):
    resume_id = str(uuid.uuid4())
    created = resume_service.save(resume_id, resume_data)
    return ResumeResponse(id=resume_id, message="Resume created successfully", data=created)


@router.get(
    "/resumes",
    summary="List all resumes",
)
async def list_resumes():
    resumes = resume_service.list_all()
    return {"resumes": resumes, "count": len(resumes)}


@router.get(
    "/resumes/{resume_id}",
    response_model=ResumeResponse,
    summary="Get a specific resume by ID",
)
async def get_resume(resume_id: str):
    resume = resume_service.get(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID '{resume_id}' not found",
        )
    return ResumeResponse(id=resume_id, message="Resume retrieved", data=resume)


@router.put(
    "/resumes/{resume_id}",
    response_model=ResumeResponse,
    summary="Update an existing resume",
)
async def update_resume(resume_id: str, resume_data: ResumeData):
    existing = resume_service.get(resume_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID '{resume_id}' not found",
        )
    updated = resume_service.save(resume_id, resume_data)
    return ResumeResponse(id=resume_id, message="Resume updated successfully", data=updated)


@router.delete(
    "/resumes/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resume",
)
async def delete_resume(resume_id: str):
    success = resume_service.delete(resume_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID '{resume_id}' not found",
        )


@router.post(
    "/resumes/ai/suggest",
    response_model=AISuggestResponse,
    summary="Get AI suggestions for resume sections",
)
async def ai_suggest(request: AISuggestRequest):
    suggestions = ai_service.suggest(request.section, request.context, request.current_text)
    return AISuggestResponse(suggestions=suggestions, section=request.section)
