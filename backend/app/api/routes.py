from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import uuid

from app.database import get_db
from app.api.deps import get_current_user
from app.models import User, Profile, Job, Contact, Message, Application, Company
import app.schemas as schemas

# Services
from app.services.resume_service import process_and_save_resume
from app.services.job_discovery_service import discover_and_save_jobs
from app.services.matching_service import run_matching_pipeline
from app.services.company_research_service import research_company
from app.services.contact_discovery_service import discover_contacts_for_job
from app.services.outreach_service import generate_outreach_message
from app.services.analytics_service import (
    get_analytics_summary,
    get_funnel_analytics,
    get_skill_gaps,
    generate_weekly_report
)

# Tasks
from app.tasks import discover_jobs_task

api_router = APIRouter()

# ==========================================
# RESUME ROUTER
# ==========================================
resume_router = APIRouter(prefix="/resume", tags=["Resume"])

@resume_router.post("/upload", response_model=schemas.ProfileResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    try:
        pdf_bytes = await file.read()
        profile = process_and_save_resume(db, current_user.clerk_id, pdf_bytes, file.filename)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@resume_router.post("/sync/drive", response_model=schemas.ProfileResponse)
async def sync_drive(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Mocking Google Drive sync: loads the default Anirudh profile
    from app.services.resume_service import parse_resume_to_json
    
    # Deactivate existing active profiles
    db.query(Profile).filter(Profile.user_id == current_user.id, Profile.is_active == True).update({"is_active": False})
    
    latest_profile = db.query(Profile).filter(Profile.user_id == current_user.id).order_by(Profile.version.desc()).first()
    next_version = (latest_profile.version + 1) if latest_profile else 1
    
    dummy_text = "Anirudh Sudheer, AI/ML student at SIT. Experience in FastAPI and Jetpack Compose. Built Nimma-Guru."
    parsed = parse_resume_to_json(dummy_text)
    
    profile = Profile(
        user_id=current_user.id,
        version=next_version,
        raw_text=dummy_text,
        skills=parsed.get("skills", {}),
        projects=parsed.get("projects", []),
        education=parsed.get("education", []),
        experience=parsed.get("experience", []),
        certifications=parsed.get("certifications", []),
        resume_url="google_drive_sync.pdf",
        is_active=True
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@resume_router.get("/profile", response_model=schemas.ProfileResponse)
async def get_active_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id, Profile.is_active == True).first()
    if not profile:
        raise HTTPException(status_code=404, detail="No active profile found. Please upload a resume.")
    return profile

@resume_router.get("/versions", response_model=List[schemas.ProfileResponse])
async def list_profile_versions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Profile).filter(Profile.user_id == current_user.id).order_by(Profile.version.desc()).all()

@resume_router.patch("/versions/{profile_id}/activate", response_model=schemas.ProfileResponse)
async def activate_profile_version(
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify profile exists and belongs to user
    profile = db.query(Profile).filter(Profile.id == profile_id, Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile version not found")
        
    # Deactivate all
    db.query(Profile).filter(Profile.user_id == current_user.id).update({"is_active": False})
    # Activate selected
    profile.is_active = True
    db.commit()
    db.refresh(profile)
    return profile

api_router.include_router(resume_router)


# ==========================================
# JOBS ROUTER
# ==========================================
jobs_router = APIRouter(prefix="/jobs", tags=["Jobs"])

@jobs_router.get("", response_model=List[schemas.JobResponse])
async def list_jobs(
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    company: Optional[str] = None,
    remote: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    if min_score is not None:
        query = query.filter(Job.match_score >= min_score)
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    if remote is not None:
        query = query.filter(Job.remote == remote)
        
    return query.order_by(Job.match_score.desc()).all()

@jobs_router.get("/{job_id}", response_model=schemas.JobResponse)
async def get_job_detail(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job

@jobs_router.post("/{job_id}/save", response_model=schemas.JobResponse)
async def save_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job.status = "saved"
    
    # Check if application record exists, create one
    existing_app = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_id == job.id
    ).first()
    
    if not existing_app:
        active_profile = db.query(Profile).filter(Profile.user_id == current_user.id, Profile.is_active == True).first()
        version = active_profile.version if active_profile else 1
        
        new_app = Application(
            user_id=current_user.id,
            job_id=job.id,
            profile_version=version,
            status="saved"
        )
        db.add(new_app)
        
    db.commit()
    db.refresh(job)
    return job

@jobs_router.post("/discover")
async def trigger_job_discovery(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id, Profile.is_active == True).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No active profile found. Please upload a resume first.")
        
    try:
        # Try running in background via Celery
        discover_jobs_task.delay(str(profile.id))
        return {"status": "enqueued", "message": "Background job discovery started."}
    except Exception as e:
        # Fallback to synchronous execution if Celery/Redis is unavailable
        logger.warning(f"Celery queue failed: {e}. Executing discovery synchronously.")
        res = discover_and_save_jobs(db, profile)
        
        # Run matching synchronously too
        new_jobs = db.query(Job).filter(Job.status == "discovered", Job.match_score.is_(None)).all()
        for j in new_jobs:
            run_matching_pipeline(db, j, profile)
            # Research company if score > 70
            if j.match_score and j.match_score >= 70.0:
                research_company(db, j.company)
                discover_contacts_for_job(db, j)
                
        return {"status": "completed", "message": "Synchronous job discovery complete.", "results": res}

@jobs_router.get("/{job_id}/contacts", response_model=List[schemas.ContactResponse])
async def get_job_contacts(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    contacts = discover_contacts_for_job(db, job)
    return contacts

@jobs_router.post("/{job_id}/recalculate", response_model=schemas.JobResponse)
async def recalculate_job_match(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    profile = db.query(Profile).filter(Profile.user_id == current_user.id, Profile.is_active == True).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No active profile found. Please upload a resume first.")
        
    run_matching_pipeline(db, job, profile)
    db.refresh(job)
    return job

api_router.include_router(jobs_router)


# ==========================================
# OUTREACH ROUTER
# ==========================================
outreach_router = APIRouter(prefix="/outreach", tags=["Outreach"])

@outreach_router.post("/generate", response_model=schemas.MessageResponse)
async def generate_outreach(
    contact_id: uuid.UUID,
    message_type: str, # linkedin_referral, cold_email, follow_up
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        msg = generate_outreach_message(db, str(contact_id), message_type)
        return msg
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outreach_router.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
async def get_contact_by_id(
    contact_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@outreach_router.get("/messages", response_model=List[schemas.MessageResponse])
async def list_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Message).order_by(Message.created_at.desc()).all()

@outreach_router.patch("/messages/{message_id}", response_model=schemas.MessageResponse)
async def update_message_draft(
    message_id: uuid.UUID,
    payload: schemas.MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message draft not found")
        
    if payload.draft is not None:
        msg.draft = payload.draft
    if payload.final_text is not None:
        msg.final_text = payload.final_text
    if payload.status is not None:
        msg.status = payload.status
    if payload.sent_at is not None:
        msg.sent_at = payload.sent_at
    if payload.replied_at is not None:
        msg.replied_at = payload.replied_at
        
    db.commit()
    db.refresh(msg)
    return msg

@outreach_router.post("/messages/{message_id}/send", response_model=schemas.MessageResponse)
async def send_outreach_message(
    message_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message draft not found")
        
    # Mock sending via Gmail API
    logger.info(f"Sending message {message_id} to contact.")
    
    # Check if there is an active profile with a resume PDF
    active_profile = db.query(Profile).filter(Profile.user_id == current_user.id, Profile.is_active == True).first()
    if active_profile and active_profile.resume_url:
        if active_profile.resume_url.startswith("/static/resumes/"):
            import os
            # Resolve physical file path: app/static/resumes/{profile_id}.pdf
            static_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rel_path = active_profile.resume_url.lstrip("/")
            full_path = os.path.join(static_dir, rel_path)
            if os.path.exists(full_path):
                logger.info(f"Attached resume PDF file: {full_path} to cold outreach email.")
            else:
                logger.warning(f"Resume PDF url is {active_profile.resume_url} but file does not exist at {full_path}.")
        else:
            logger.info(f"Attached resume URL/filename: {active_profile.resume_url} to cold outreach email.")
    else:
        logger.info("No resume attached (no active profile or resume found).")
        
    msg.status = "sent"
    msg.sent_at = datetime.utcnow()
    msg.final_text = msg.draft
    
    # Update associated contact status
    contact = db.query(Contact).filter(Contact.id == msg.contact_id).first()
    if contact:
        contact.status = "contacted"
        
    # Update associated application status
    if msg.job_id:
        app = db.query(Application).filter(
            Application.user_id == current_user.id,
            Application.job_id == msg.job_id
        ).first()
        if app and app.status == "saved":
            app.status = "applied"
            app.applied_date = date.today()
            
    db.commit()
    db.refresh(msg)
    return msg

api_router.include_router(outreach_router)


# ==========================================
# APPLICATIONS ROUTER
# ==========================================
applications_router = APIRouter(prefix="/applications", tags=["Applications"])

@applications_router.get("", response_model=List[schemas.ApplicationResponse])
async def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Application).filter(Application.user_id == current_user.id).all()

@applications_router.post("", response_model=schemas.ApplicationResponse)
async def create_application(
    payload: schemas.ApplicationBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_id == payload.job_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Application already tracked for this job.")
        
    new_app = Application(
        user_id=current_user.id,
        job_id=payload.job_id,
        profile_version=payload.profile_version,
        status=payload.status,
        applied_date=payload.applied_date,
        platform=payload.platform,
        interview_rounds=payload.interview_rounds,
        offer_details=payload.offer_details,
        notes=payload.notes
    )
    db.add(new_app)
    
    # Update job status
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if job:
        job.status = payload.status
        
    db.commit()
    db.refresh(new_app)
    return new_app

@applications_router.patch("/{app_id}", response_model=schemas.ApplicationResponse)
async def update_application_status(
    app_id: uuid.UUID,
    payload: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application record not found")
        
    if payload.status is not None:
        app.status = payload.status
        # Sync back to Job status
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if job:
            job.status = payload.status
    if payload.applied_date is not None:
        app.applied_date = payload.applied_date
    if payload.platform is not None:
        app.platform = payload.platform
    if payload.interview_rounds is not None:
        app.interview_rounds = payload.interview_rounds
    if payload.offer_details is not None:
        app.offer_details = payload.offer_details
    if payload.notes is not None:
        app.notes = payload.notes
        
    db.commit()
    db.refresh(app)
    return app

@applications_router.delete("/{app_id}")
async def withdraw_application(
    app_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    # Reset job status
    job = db.query(Job).filter(Job.id == app.job_id).first()
    if job:
        job.status = "discovered"
        
    db.delete(app)
    db.commit()
    return {"message": "Application removed successfully"}

api_router.include_router(applications_router)


# ==========================================
# ANALYTICS ROUTER
# ==========================================
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])

@analytics_router.get("/summary", response_model=schemas.AnalyticsSummaryResponse)
async def analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_analytics_summary(db, current_user.clerk_id)

@analytics_router.get("/funnel", response_model=schemas.FunnelResponse)
async def analytics_funnel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stages = get_funnel_analytics(db)
    return {"stages": stages}

@analytics_router.get("/skill-gaps", response_model=List[schemas.SkillGapItem])
async def analytics_skill_gaps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_skill_gaps(db)

@analytics_router.get("/weekly", response_model=schemas.WeeklySummaryResponse)
async def analytics_weekly(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return generate_weekly_report(db)

api_router.include_router(analytics_router)
