import logging
import re
import json
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.models import Contact, Job, Company
from app.services.llm import call_nvidia_nim

logger = logging.getLogger("app.services.contact_discovery")

def discover_contacts_for_job(db: Session, job: Job) -> list:
    """
    Find actual key contacts for the company listed on the Job record by scraping
    the job description and the job source URL.
    """
    # Check if we already have contacts saved for this job
    existing_contacts = db.query(Contact).filter(Contact.job_id == job.id).all()
    if existing_contacts:
        logger.info(f"Using cached contacts for job: {job.title} at {job.company}")
        return existing_contacts

    contacts_found = []
    page_text = ""
    
    # 1. Start with the job description
    if job.description:
        page_text += job.description + "\n"
        
    # 2. Try to scrape the source_url if present
    if job.source_url and job.source_url.startswith("http"):
        logger.info(f"Scraping job source URL: {job.source_url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            with httpx.Client(follow_redirects=True, verify=False) as client:
                response = client.get(job.source_url, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    page_text += "\n" + soup.get_text(separator=" ")
        except Exception as e:
            logger.warning(f"Failed to scrape job source URL {job.source_url}: {e}")

    # Clean up page_text (limit length for prompt)
    clean_text = re.sub(r'\s+', ' ', page_text).strip()
    if len(clean_text) > 8000:
        clean_text = clean_text[:8000]

    # Extract all emails found in the text using regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails_in_text = list(set(re.findall(email_pattern, clean_text)))
    
    contacts_data = []
    
    if clean_text:
        # We will pass the list of emails and clean_text to the LLM to get a structured JSON
        prompt = f"""
        Analyze the following scraped text from a job posting for "{job.title}" at "{job.company}".
        Identify any ACTUAL recruiter, hiring manager, or company contact person's name and email address mentioned in the text.
        
        List of potential email addresses found in the page: {emails_in_text}
        
        Text:
        \"\"\"{clean_text}\"\"\"
        
        Return a JSON list of contacts. Do NOT guess or invent contacts. If no contact person is explicitly mentioned, return an empty list [].
        Each contact object must have:
        - name: "First Last" of the contact person (or "Hiring Team" / "Recruiting Team" if no specific name is mentioned but a specific contact email is given)
        - title: "Their Role/Title" (e.g. "Hiring Manager", "Recruiter", etc.)
        - email: "email address" (must be one of the potential emails or another email clearly mentioned in the text)
        - email_confidence: confidence score between 0.0 and 1.0 (1.0 if explicitly mentioned, lower if guessed/inferred)
        - source: "Job Posting"
        
        Return ONLY valid JSON. No conversational text.
        """
        
        try:
            response_text = call_nvidia_nim(prompt)
            json_match = re.search(r"\[\s*\{.*\}\s*\]", response_text, re.DOTALL)
            if json_match:
                contacts_data = json.loads(json_match.group(0))
            else:
                contacts_data = json.loads(response_text)
        except Exception as e:
            logger.warning(f"Failed to extract contacts using LLM: {e}")
            contacts_data = []

    # If LLM didn't find specific people but we found raw recruiter/talent emails using regex, let's include them
    if not contacts_data and emails_in_text:
        for email in emails_in_text:
            # Check if it has any keyword that suggests it's a contact or hiring email
            email_user = email.split("@")[0].lower()
            if any(k in email_user for k in ["apply", "careers", "jobs", "talent", "recruiting", "hiring", "hr", "recruitment"]):
                contacts_data.append({
                    "name": f"{job.company} Hiring Team",
                    "title": "Recruiter / Hiring Team",
                    "email": email,
                    "email_confidence": 0.9,
                    "source": "Job Posting"
                })

    for item in contacts_data:
        email = item.get("email")
        if not email:
            continue
            
        new_contact = Contact(
            job_id=job.id,
            name=item.get("name", "Hiring Team"),
            title=item.get("title", "Hiring Contact"),
            company=job.company,
            linkedin_url=item.get("linkedin_url", f"https://linkedin.com/company/{job.company.lower().replace(' ', '')}"),
            email=email,
            email_confidence=item.get("email_confidence", 1.0),
            connection_degree=1,
            source=item.get("source", "Job Posting"),
            status="discovered",
            notes="Extracted directly from job posting details."
        )
        db.add(new_contact)
        contacts_found.append(new_contact)
        
    db.commit()
    logger.info(f"Discovered {len(contacts_found)} contacts for job: {job.title} at {job.company}")
    
    # Retrieve to return fully bound entities
    return db.query(Contact).filter(Contact.job_id == job.id).all()
