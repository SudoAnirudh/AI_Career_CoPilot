import logging
from uuid import UUID
from app.worker import celery_app
from app.database import SessionLocal
from app.models import Job, Profile
from app.services.job_discovery_service import discover_and_save_jobs
from app.services.matching_service import run_matching_pipeline
from app.services.company_research_service import research_company
from app.services.contact_discovery_service import discover_contacts_for_job

logger = logging.getLogger("app.tasks")

@celery_app.task(name="tasks.discover_jobs_task")
def discover_jobs_task(profile_id: str):
    """Celery task to run job discovery, then trigger matching on newly found jobs."""
    db = SessionLocal()
    try:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            logger.error(f"Profile {profile_id} not found for job discovery.")
            return "Profile not found"
            
        result = discover_and_save_jobs(db, profile)
        
        # Trigger matching for newly discovered jobs
        new_jobs = db.query(Job).filter(Job.status == "discovered", Job.match_score.is_(None)).all()
        for job in new_jobs:
            match_job_task.delay(str(job.id), str(profile.id))
            
        return result
    except Exception as e:
        logger.exception(f"Error during job discovery: {e}")
        return str(e)
    finally:
        db.close()


@celery_app.task(name="tasks.match_job_task")
def match_job_task(job_id: str, profile_id: str):
    """Celery task to compute match score. Triggers company research if score > 70."""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not job or not profile:
            logger.error(f"Job {job_id} or Profile {profile_id} not found for matching.")
            return "Job or Profile not found"
            
        result = run_matching_pipeline(db, job, profile)
        score = result.get("score", 0.0)
        
        # If match score > 70, trigger company research
        if score >= 70.0:
            research_company_task.delay(job.company, str(job.id))
            
        return f"Match completed: {score}/100"
    except Exception as e:
        logger.exception(f"Error during match calculation: {e}")
        return str(e)
    finally:
        db.close()


@celery_app.task(name="tasks.research_company_task")
def research_company_task(company_name: str, job_id: str):
    """Celery task to research company, then trigger contact discovery."""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found for company research.")
            return "Job not found"
            
        research_company(db, company_name)
        
        # Trigger contact discovery
        discover_contacts_task.delay(str(job.id))
        
        return f"Research completed for: {company_name}"
    except Exception as e:
        logger.exception(f"Error during company research: {e}")
        return str(e)
    finally:
        db.close()


@celery_app.task(name="tasks.discover_contacts_task")
def discover_contacts_task(job_id: str):
    """Celery task to find networking/referral contacts for a job."""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found for contact discovery.")
            return "Job not found"
            
        contacts = discover_contacts_for_job(db, job)
        return f"Discovered {len(contacts)} contacts for {job.company}"
    except Exception as e:
        logger.exception(f"Error during contact discovery: {e}")
        return str(e)
    finally:
        db.close()
