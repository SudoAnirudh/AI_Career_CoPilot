import logging
import random
from sqlalchemy.orm import Session
from app.models import Contact, Job, Company

logger = logging.getLogger("app.services.contact_discovery")

MOCK_FIRST_NAMES = ["Priya", "Rahul", "Neha", "Arjun", "Karan", "Simran", "Vijay", "Aisha", "David", "Sarah"]
MOCK_LAST_NAMES = ["Sharma", "Nair", "Patel", "Sudheer", "Mathew", "Roy", "Verma", "Sen", "Smith", "Jones"]

MOCK_ROLES = [
    ("Engineering Manager - AI/ML", 1),       # Priority 1
    ("Talent Acquisition Specialist", 2),    # Priority 2
    ("Senior Software Engineer", 3),          # Priority 3
    ("SIT Alumni / Engineer", 4)             # Priority 4
]

def guess_email(first_name: str, last_name: str, domain: str) -> tuple:
    """Guess company email using common patterns and assign confidence score."""
    clean_first = first_name.strip().lower()
    clean_last = last_name.strip().lower()
    clean_domain = (domain or "company.com").strip().lower()
    
    patterns = [
        (f"{clean_first}@{clean_domain}", 0.8),
        (f"{clean_first}.{clean_last}@{clean_domain}", 0.95),
        (f"{clean_first[0]}{clean_last}@{clean_domain}", 0.75),
    ]
    
    # Pick the most likely (pattern 2 is standard)
    selected_pattern = patterns[1]
    return selected_pattern[0], selected_pattern[1]

def discover_contacts_for_job(db: Session, job: Job) -> list:
    """
    Find key contacts for the company listed on the Job record.
    Caches them in the contacts table.
    """
    # Check if we already have contacts saved for this job
    existing_contacts = db.query(Contact).filter(Contact.job_id == job.id).all()
    if existing_contacts:
        logger.info(f"Using cached contacts for job: {job.title} at {job.company}")
        return existing_contacts
        
    # Get company domain if cached
    company_cache = db.query(Company).filter(Company.name.ilike(job.company)).first()
    domain = company_cache.domain if company_cache else f"{job.company.lower().replace(' ', '')}.com"
    
    contacts = []
    
    # Generate 2 to 3 contacts representing our priorities
    num_contacts = random.randint(2, 3)
    selected_roles = random.sample(MOCK_ROLES, num_contacts)
    
    for role_title, priority in selected_roles:
        first = random.choice(MOCK_FIRST_NAMES)
        last = random.choice(MOCK_LAST_NAMES)
        
        email, confidence = guess_email(first, last, domain)
        
        new_contact = Contact(
            job_id=job.id,
            name=f"{first} {last}",
            title=role_title,
            company=job.company,
            linkedin_url=f"https://linkedin.com/in/{first.lower()}-{last.lower()}",
            email=email,
            email_confidence=confidence,
            connection_degree=random.choice([1, 2, 3]) if priority != 4 else 1, # Alumni is 1st degree equivalent
            source="LinkedIn" if priority != 4 else "Alumni Network",
            status="discovered",
            notes=f"Discovered automatically. Priority {priority} contact."
        )
        db.add(new_contact)
        contacts.append(new_contact)
        
    db.commit()
    logger.info(f"Discovered {len(contacts)} contacts for job: {job.title} at {job.company}")
    
    # Retrieve to return fully bound entities
    return db.query(Contact).filter(Contact.job_id == job.id).all()
