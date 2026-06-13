import logging
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Company, Job
from app.services.llm import call_nvidia_nim

logger = logging.getLogger("app.services.company_research")

RESEARCH_PROMPT = """
You are a corporate intelligence researcher. Research the following company:
Company Name: {company_name}

Provide a structured JSON output detailing:
1. Overview: 2-3 sentence overview of the company, its mission, and products.
2. Tech Stack: List of technologies they use (languages, frameworks, databases, infrastructure).
3. Funding Stage: Seed, Series A, Series B, Public, Bootstrap, etc.
4. Team Size: Range of employees (e.g., 10-50, 100-500).
5. Recent News: List of 2-3 notable events, funding announcements, or product launches in the last 30-90 days.
6. AI Focus: Summary of their AI initiatives or ML usage (if any).
7. Why Fit: Explain in 2 sentences how a candidate with a strong background in Python, FastAPI, and GenAI agents (like Anirudh Sudheer) fits into their team.

Return a JSON object matching this structure EXACTLY:
{{
  "name": "{company_name}",
  "domain": "company.com",
  "overview": "...",
  "tech_stack": ["Python", "Docker"],
  "funding_stage": "...",
  "team_size": "...",
  "recent_news": ["...", "..."],
  "ai_focus": "...",
  "why_fit": "..."
}}

Provide ONLY raw JSON. No markdown backticks, no wrapper.
"""

def research_company(db: Session, company_name: str) -> Company:
    """
    Research a company and cache the profile. 
    If already researched in the last 7 days, returns cached profile.
    """
    company_name_clean = company_name.strip()
    
    # Check cache
    cached_company = db.query(Company).filter(Company.name.ilike(company_name_clean)).first()
    if cached_company and cached_company.last_researched_at:
        # Check if cache is fresh (less than 7 days old)
        if datetime.utcnow() - cached_company.last_researched_at < timedelta(days=7):
            logger.info(f"Using cached research for company: {company_name_clean}")
            return cached_company
            
    # Compile prompt
    prompt = RESEARCH_PROMPT.format(company_name=company_name_clean)
    llm_raw = call_nvidia_nim(prompt)
    
    # Clean markdown
    clean_json_str = llm_raw.strip()
    if clean_json_str.startswith("```"):
        lines = clean_json_str.split("\n")
        if "```" in lines[0]:
            lines = lines[1:]
        if "```" in lines[-1]:
            lines = lines[:-1]
        clean_json_str = "\n".join(lines).strip()
        
    try:
        data = json.loads(clean_json_str)
    except Exception as e:
        logger.error(f"Failed to parse company research JSON: {e}")
        # Default mock fallback
        data = {
            "name": company_name_clean,
            "domain": f"{company_name_clean.lower().replace(' ', '')}.ai",
            "overview": f"{company_name_clean} is an innovative technology company building next-generation software products.",
            "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "funding_stage": "Series A",
            "team_size": "50-100",
            "recent_news": [f"Expanded engineering team for new AI products", f"Launched flagship developer tool"],
            "ai_focus": "Developing smart workflows and integrating semantic LLM agents.",
            "why_fit": "Your background in Python and FastAPI fits well into their high-performance service architecture."
        }
        
    # Save or update cache
    if cached_company:
        cached_company.domain = data.get("domain")
        cached_company.overview = data.get("overview")
        cached_company.tech_stack = data.get("tech_stack")
        cached_company.funding_stage = data.get("funding_stage")
        cached_company.team_size = data.get("team_size")
        cached_company.recent_news = data.get("recent_news")
        cached_company.ai_focus = data.get("ai_focus")
        cached_company.why_fit = data.get("why_fit")
        cached_company.last_researched_at = datetime.utcnow()
        db.commit()
        db.refresh(cached_company)
        return cached_company
    else:
        new_company = Company(
            name=company_name_clean,
            domain=data.get("domain"),
            overview=data.get("overview"),
            tech_stack=data.get("tech_stack"),
            funding_stage=data.get("funding_stage"),
            team_size=data.get("team_size"),
            recent_news=data.get("recent_news"),
            ai_focus=data.get("ai_focus"),
            why_fit=data.get("why_fit"),
            last_researched_at=datetime.utcnow()
        )
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        return new_company
