import logging
from sqlalchemy.orm import Session
from app.models import Contact, Job, Company, Profile, Message, User
from app.services.llm import call_nvidia_nim

logger = logging.getLogger("app.services.outreach")

REFERRAL_REQUEST_PROMPT = """
You are {user_name}, writing a LinkedIn referral request directly to {contact_name}.

User Background (My Background):
{profile_summary}

Target Contact:
- Name: {contact_name}
- Title: {contact_title}
- Company: {company_name}

Job Role: {job_title}
Job Description:
{job_description}

Company Context:
{company_summary}

Rules:
- Max 150 words
- Write in the first person (use "I", "me", "my", "my background", "my projects"). DO NOT write in the third person or say you are writing on behalf of someone else.
- No generic openers ("Hope this finds you well", "Dear", "Respected")
- Reference one specific thing about the contact's company or work
- Mention one relevant project or skill from my background that directly aligns with the Job Description requirements.
- End with a clear, low-pressure ask
- Do not use the word "leverage"
- Sound human, not AI-generated
- Sign off using exactly your name "{user_name}". Do not leave any placeholders or template markers like "[Your Name]".

Return only the message text. No subject line. No "Hi" header.
"""

COLD_EMAIL_PROMPT = """
You are {user_name}, writing a cold outreach email directly to a recruiter ({contact_name}).

User Background (My Background):
{profile_summary}

Target Contact:
- Name: {contact_name}
- Title: {contact_title}
- Company: {company_name}

Job Role: {job_title}
Job Description:
{job_description}

Company Context:
{company_summary}

Rules:
- Max 200 words
- Write in the first person (use "I", "me", "my", "my background", "my projects"). DO NOT write in the third person or say you are writing on behalf of someone else.
- Subject Line: Must start with "Subject:" and be concise and click-worthy.
- No generic openers ("Hope this finds you well")
- Bullet points of key projects or experiences (max 2) with technologies that directly map to the core needs in the Job Description.
- Clear ask: is this role open or open to a brief chat?
- Sound professional, enthusiastic, and human
- Sign off using exactly your name "{user_name}". Do not leave any placeholders, square brackets, or template markers (like "[Your Name]", "[Your Contact Information]", "[Contact Name]", "[Company Name]") in the output. Replace them with the actual details provided.

Return the Subject line and the email body.
"""

FOLLOW_UP_PROMPT = """
You are {user_name}, writing a follow-up outreach message directly to {contact_name} at {company_name}.
I previously reached out about the {job_title} opening but haven't heard back.

User Background (My Background):
{profile_summary}

Job Description:
{job_description}

Rules:
- Max 100 words
- Write in the first person (use "I", "me", "my", "my background", "my projects"). DO NOT write in the third person or say you are writing on behalf of someone else.
- Acknowledge that they are busy
- Reinforce interest, citing a brief alignment with their Job Description (e.g. key matching technology/experience)
- Friendly, brief, no pressure
- Sign off using exactly your name "{user_name}". Do not leave any placeholders like "[Your Name]" in the output.

Return only the message text.
"""

def generate_outreach_message(db: Session, contact_id: str, message_type: str) -> Message:
    """
    Generate an outreach draft (LinkedIn Referral, Cold Recruiter Email, or Follow-up)
    for a contact and save it to the database.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise ValueError("Contact not found")
        
    job = db.query(Job).filter(Job.id == contact.job_id).first()
    if not job:
        raise ValueError("Job not found")
        
    # Get active profile
    profile = db.query(Profile).filter(Profile.is_active == True).first()
    if not profile:
        raise ValueError("No active profile found")
        
    user = db.query(User).filter(User.id == profile.user_id).first()
    user_name = user.name if user else "Anirudh Sudheer"
    
    # Get company info
    company = db.query(Company).filter(Company.name.ilike(job.company)).first()
    company_summary = company.overview if company else f"A leading firm in the space of {job.title}."
    
    # Construct profile summary
    skills_flat = []
    if profile.skills:
        for cat, items in profile.skills.items():
            if isinstance(items, list):
                skills_flat.extend(items)
                
    projects_desc = []
    if profile.projects:
        for p in profile.projects:
            projects_desc.append(f"{p.get('name')}: {p.get('description')} using {', '.join(p.get('tech', []))}")
            
    experience_desc = []
    if profile.experience:
        for exp in profile.experience:
            experience_desc.append(f"{exp.get('role')} at {exp.get('company')} ({exp.get('duration')}): {exp.get('description')}")
            
    education_desc = []
    if profile.education:
        for edu in profile.education:
            education_desc.append(f"{edu.get('degree')} from {edu.get('institution')} ({edu.get('year')})")
            
    profile_summary = f"""
    Name: {user_name}
    Skills: {', '.join(skills_flat)}
    Projects:
    - {chr(10).join(projects_desc)}
    Experience:
    - {chr(10).join(experience_desc) if experience_desc else 'None listed'}
    Education:
    - {chr(10).join(education_desc) if education_desc else 'None listed'}
    """
    
    job_desc = job.description or "No description provided."
    
    # Choose prompt based on type
    if message_type == "linkedin_referral":
        prompt = REFERRAL_REQUEST_PROMPT.format(
            user_name=user_name,
            profile_summary=profile_summary,
            contact_name=contact.name,
            contact_title=contact.title,
            company_name=job.company,
            job_title=job.title,
            job_description=job_desc,
            company_summary=company_summary
        )
    elif message_type == "cold_email":
        prompt = COLD_EMAIL_PROMPT.format(
            user_name=user_name,
            profile_summary=profile_summary,
            contact_name=contact.name,
            contact_title=contact.title,
            company_name=job.company,
            job_title=job.title,
            job_description=job_desc,
            company_summary=company_summary
        )
    elif message_type == "follow_up":
        prompt = FOLLOW_UP_PROMPT.format(
            user_name=user_name,
            profile_summary=profile_summary,
            contact_name=contact.name,
            company_name=job.company,
            job_title=job.title,
            job_description=job_desc
        )
    else:
        raise ValueError(f"Invalid message type: {message_type}")
        
    # Generate draft
    draft_text = call_nvidia_nim(prompt)
    
    # Perform basic quality control checks
    # Rule: Do not use the word "leverage"
    if "leverage" in draft_text.lower():
        draft_text = draft_text.replace("leverage", "utilize").replace("Leverage", "Utilize")
        
    # Rule: No generic openers
    for opener in ["Hope this finds you well", "Hope you are doing well"]:
        if opener.lower() in draft_text.lower():
            # Remove or replace opener
            draft_text = draft_text.replace(opener, "")
            
    # Save draft
    new_message = Message(
        contact_id=contact.id,
        job_id=job.id,
        type=message_type,
        draft=draft_text.strip(),
        status="draft"
    )
    db.add(new_message)
    
    # Update contact status
    contact.status = "pending_outreach"
    
    db.commit()
    db.refresh(new_message)
    
    return new_message
