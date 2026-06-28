"""Pydantic models for resume data"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class ContactInfo(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None


class WorkExperience(BaseModel):
    company: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    start_date: str  # e.g. "Jan 2020"
    end_date: Optional[str] = "Present"
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str = Field(..., min_length=1)
    degree: str = Field(..., min_length=1)
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str = Field(..., min_length=1)
    description: str
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Certification(BaseModel):
    name: str
    issuer: str
    date_issued: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_url: Optional[str] = None


class ResumeData(BaseModel):
    contact: ContactInfo
    summary: Optional[str] = None
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    template: str = "modern"  # modern | classic | minimal


class ResumeResponse(BaseModel):
    id: str
    message: str
    data: ResumeData


class AISuggestRequest(BaseModel):
    section: str  # "summary" | "bullets" | "skills"
    context: str  # Job description or current text
    current_text: Optional[str] = None


class AISuggestResponse(BaseModel):
    suggestions: List[str]
    section: str
