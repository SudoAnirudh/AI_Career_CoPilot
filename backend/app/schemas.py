from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    clerk_id: str

class UserResponse(UserBase):
    id: UUID
    clerk_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Profile Schemas
class ProfileBase(BaseModel):
    version: int = 1
    raw_text: Optional[str] = None
    skills: Optional[Dict[str, List[str]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    resume_url: Optional[str] = None
    is_active: bool = True

class ProfileCreate(ProfileBase):
    user_id: UUID

class ProfileResponse(ProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Job Schemas
class JobBase(BaseModel):
    title: str
    company: str
    description: Optional[str] = None
    skills_required: Optional[List[str]] = None
    location: Optional[str] = None
    remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_years_min: Optional[int] = None
    experience_years_max: Optional[int] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    posted_date: Optional[date] = None

class JobCreate(JobBase):
    source_hash: str

class JobResponse(JobBase):
    id: UUID
    source_hash: str
    match_score: Optional[float] = None
    match_explanation: Optional[Dict[str, Any]] = None
    status: str
    discovered_at: datetime

    class Config:
        from_attributes = True

# Company Schemas
class CompanyBase(BaseModel):
    name: str
    domain: Optional[str] = None
    overview: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    funding_stage: Optional[str] = None
    team_size: Optional[str] = None
    recent_news: Optional[List[str]] = None
    ai_focus: Optional[str] = None
    why_fit: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: UUID
    last_researched_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Contact Schemas
class ContactBase(BaseModel):
    job_id: UUID
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    email_confidence: float = 0.0
    connection_degree: Optional[int] = None
    source: Optional[str] = None
    status: str = "discovered"
    notes: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    contact_id: UUID
    job_id: Optional[UUID] = None
    type: str
    draft: str
    final_text: Optional[str] = None
    status: str = "draft"

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    draft: Optional[str] = None
    final_text: Optional[str] = None
    status: Optional[str] = None
    sent_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None

class MessageResponse(MessageBase):
    id: UUID
    sent_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Application Schemas
class ApplicationBase(BaseModel):
    job_id: UUID
    profile_version: int = 1
    status: str = "saved"
    applied_date: Optional[date] = None
    platform: Optional[str] = None
    interview_rounds: Optional[List[Dict[str, Any]]] = None
    offer_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    user_id: UUID

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    applied_date: Optional[date] = None
    platform: Optional[str] = None
    interview_rounds: Optional[List[Dict[str, Any]]] = None
    offer_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    id: UUID
    user_id: UUID
    updated_at: datetime
    job: JobResponse

    class Config:
        from_attributes = True

# Analytics Schemas
class AnalyticsSummaryResponse(BaseModel):
    total_applications: int
    active_applications: int
    response_rate: float
    interview_rate: float

class FunnelStage(BaseModel):
    stage: str
    count: int

class FunnelResponse(BaseModel):
    stages: List[FunnelStage]

class SkillGapItem(BaseModel):
    skill: str
    frequency: int
    missing: bool

class WeeklySummaryResponse(BaseModel):
    start_date: str
    end_date: str
    jobs_discovered: int
    high_matches: int
    applied: int
    referrals_requested: int
    replies_received: int
    top_sources: List[Dict[str, Any]]
    skill_gaps: List[str]
    summary_text: str
