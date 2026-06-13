import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Application, Job, Message, Profile

logger = logging.getLogger("app.services.analytics")

def get_analytics_summary(db: Session, user_id: str) -> dict:
    """Get overall funnel rates: Total, Active, Response, and Interview rates."""
    total_apps = db.query(Application).count()
    
    # Active = not rejected or withdrawn
    active_apps = db.query(Application).filter(
        Application.status.notin_(["rejected", "withdrawn"])
    ).count()
    
    # Response rate = contacts who replied / total outreach messages sent
    total_sent = db.query(Message).filter(Message.status == "sent").count()
    replied = db.query(Message).filter(Message.status == "replied").count()
    response_rate = float(replied) / float(total_sent) if total_sent > 0 else 0.0
    
    # Interview rate = applications in interviewing/offered status / total applications
    interviews = db.query(Application).filter(
        Application.status.in_(["interviewing", "offered"])
    ).count()
    interview_rate = float(interviews) / float(total_apps) if total_apps > 0 else 0.0
    
    return {
        "total_applications": total_apps,
        "active_applications": active_apps,
        "response_rate": round(response_rate * 100, 1),
        "interview_rate": round(interview_rate * 100, 1)
    }

def get_funnel_analytics(db: Session) -> list:
    """Calculate the counts of applications at each stage of the search pipeline."""
    stages = ["saved", "applied", "interviewing", "offered", "rejected"]
    funnel = []
    
    for stage in stages:
        count = db.query(Application).filter(Application.status == stage).count()
        funnel.append({"stage": stage.capitalize(), "count": count})
        
    return funnel

def get_skill_gaps(db: Session) -> list:
    """
    Scan all discovered jobs with high match scores or saved status,
    analyze the 'missing_skills' listed in match explanations,
    and rank them by occurrence frequency.
    """
    gaps = {}
    
    # Look at jobs with match explanation
    jobs = db.query(Job).filter(Job.match_explanation.isnot(None)).all()
    for job in jobs:
        exp = job.match_explanation or {}
        missing = exp.get("missing_skills", [])
        for skill in missing:
            gaps[skill] = gaps.get(skill, 0) + 1
            
    # Sort and structure
    sorted_gaps = sorted(gaps.items(), key=lambda x: x[1], reverse=True)
    
    # Check what skills candidate has to confirm
    profile = db.query(Profile).filter(Profile.is_active == True).first()
    profile_skills_flat = []
    if profile and profile.skills:
        for cat, items in profile.skills.items():
            if isinstance(items, list):
                profile_skills_flat.extend([s.lower() for s in items])
                
    result = []
    for skill, count in sorted_gaps[:10]: # Top 10 skill gaps
        is_missing = skill.lower() not in profile_skills_flat
        result.append({
            "skill": skill,
            "frequency": count,
            "missing": is_missing
        })
        
    return result

def generate_weekly_report(db: Session) -> dict:
    """Compile and summarize the job search performance over the last 7 days."""
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=7)
    
    # Counts
    jobs_discovered = db.query(Job).filter(
        func.date(Job.discovered_at) >= start_date
    ).count()
    
    high_matches = db.query(Job).filter(
        func.date(Job.discovered_at) >= start_date,
        Job.match_score >= 80.0
    ).count()
    
    applied = db.query(Application).filter(
        func.date(Application.applied_date) >= start_date
    ).count()
    
    referrals_requested = db.query(Message).filter(
        func.date(Message.created_at) >= start_date,
        Message.type == "linkedin_referral"
    ).count()
    
    replies_received = db.query(Message).filter(
        func.date(Message.replied_at) >= start_date
    ).count()
    
    # Top sources
    sources_query = db.query(
        Job.source, func.count(Job.id)
    ).filter(
        func.date(Job.discovered_at) >= start_date
    ).group_by(Job.source).all()
    
    top_sources = [{"source": s, "count": c} for s, c in sources_query]
    
    # Get skill gaps
    gaps = get_skill_gaps(db)
    missing_gaps = [g["skill"] for g in gaps if g["missing"]][:3]
    
    # Compile text summary
    summary_text = f"""
    Week of {start_date.strftime('%B %d')} – {today.strftime('%B %d, %Y')}:
    
    Jobs Discovered: {jobs_discovered}
    High Match (>80%): {high_matches}
    Applied: {applied}
    Referrals Requested: {referrals_requested}
    Replies Received: {replies_received}
    
    Top Performing Sources: {', '.join([f"{s['source']} ({s['count']} jobs)" for s in top_sources[:3]]) if top_sources else 'None'}
    Skill Gap Alert: {f"Frequently missing skills: {', '.join(missing_gaps)}" if missing_gaps else "Your profile aligns perfectly with recent jobs!"}
    """
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "jobs_discovered": jobs_discovered,
        "high_matches": high_matches,
        "applied": applied,
        "referrals_requested": referrals_requested,
        "replies_received": replies_received,
        "top_sources": top_sources,
        "skill_gaps": missing_gaps,
        "summary_text": summary_text.strip()
    }
