import hashlib
import logging
import urllib.parse
from datetime import datetime, date, timedelta
import xml.etree.ElementTree as ET
import httpx
from sqlalchemy.orm import Session
from app.models import Job, Profile
from app.schemas import JobCreate

logger = logging.getLogger("app.services.job_discovery")

# Realistic set of jobs in India / Remote for freshers/juniors in AI/ML & Android
MOCK_JOBS_DB = [
    {
        "title": "AI Engineer",
        "company": "Sarvam AI",
        "description": "We are looking for an AI Engineer to join our team in Bangalore. You will work on fine-tuning Indic language models, optimizing model inference, and building FastAPI backends. Experience with PyTorch, LLMs, and Python is required.",
        "skills_required": ["Python", "LLMs", "FastAPI", "PyTorch", "Indic languages"],
        "location": "Bangalore",
        "remote": False,
        "salary_min": 1200000,
        "salary_max": 1800000,
        "experience_years_min": 0,
        "experience_years_max": 2,
        "source": "Wellfound",
        "source_url": "https://wellfound.com/jobs/sarvam-ai-ai-engineer",
        "posted_date": date.today()
    },
    {
        "title": "Junior ML Engineer",
        "company": "Krutrim AI",
        "description": "Join Krutrim to build India's model infrastructure. Responsibilities include preparing datasets, training models, and deploying inference pipelines. Strong programming in Python, knowledge of transformers, and vector databases (ChromaDB/FAISS) is expected.",
        "skills_required": ["Python", "Transformers", "ChromaDB", "FAISS", "Machine Learning"],
        "location": "Remote",
        "remote": True,
        "salary_min": 1000000,
        "salary_max": 1500000,
        "experience_years_min": 0,
        "experience_years_max": 1,
        "source": "YC Jobs",
        "source_url": "https://www.workatastartup.com/jobs/krutrim-ml-engineer",
        "posted_date": date.today() - timedelta(days=1)
    },
    {
        "title": "Product Engineer (GenAI)",
        "company": "SplitSmart",
        "description": "Looking for a Product Engineer to integrate advanced AI agents into our billing and expense management platform. You will design LLM-powered invoice parsing tools, build robust APIs using FastAPI and Python, and manage database queries in PostgreSQL.",
        "skills_required": ["Python", "FastAPI", "PostgreSQL", "Gemini API", "AI Agents"],
        "location": "Remote",
        "remote": True,
        "salary_min": 800000,
        "salary_max": 1400000,
        "experience_years_min": 0,
        "experience_years_max": 2,
        "source": "Foundit",
        "source_url": "https://www.foundit.in/jobs/splitsmart-product-engineer",
        "posted_date": date.today() - timedelta(days=2)
    },
    {
        "title": "Android Developer (Kotlin)",
        "company": "Nimma App Studio",
        "description": "We are seeking a Passionate Android Developer to build modern mobile apps using Jetpack Compose, Kotlin, and Firebase. You will implement local caching, work on multi-threading, and build clean responsive interfaces. Familiarity with AI model integration on-device is a plus.",
        "skills_required": ["Kotlin", "Jetpack Compose", "Firebase", "Android SDK"],
        "location": "Bangalore",
        "remote": False,
        "salary_min": 600000,
        "salary_max": 1000000,
        "experience_years_min": 0,
        "experience_years_max": 2,
        "source": "Instahyre",
        "source_url": "https://www.instahyre.com/jobs/nimma-studio-android-dev",
        "posted_date": date.today() - timedelta(days=3)
    },
    {
        "title": "Software Engineer (AI/ML)",
        "company": "Zoho",
        "description": "Zoho is hiring a Software Engineer to work on Zoho Creator's generative AI components. You will use Python, LangChain, and databases to build customizable workflow agents for global clients. Strong understanding of REST APIs and software architecture is needed.",
        "skills_required": ["Python", "LangChain", "REST APIs", "SQL", "Software Engineering"],
        "location": "Chennai",
        "remote": False,
        "salary_min": 900000,
        "salary_max": 1300000,
        "experience_years_min": 0,
        "experience_years_max": 2,
        "source": "LinkedIn",
        "source_url": "https://www.linkedin.com/jobs/zoho-se-ai-ml",
        "posted_date": date.today() - timedelta(days=1)
    },
    {
        "title": "AI Research Assistant",
        "company": "SIT Labs",
        "description": "Research assistant role focusing on multi-modal AI mentoring systems and indicator parsing. Tasks include scraping data, structuring knowledge bases, and experimenting with Gemini 2.0 Flash models. Experience with Python, BeautifulSoup, and LangChain is crucial.",
        "skills_required": ["Python", "Gemini API", "BeautifulSoup", "LangChain", "Research"],
        "location": "Mangalore",
        "remote": False,
        "salary_min": 400000,
        "salary_max": 600000,
        "experience_years_min": 0,
        "experience_years_max": 1,
        "source": "Direct",
        "source_url": "https://sit.edu/research/jobs",
        "posted_date": date.today()
    }
]

def generate_search_queries(profile: Profile) -> list:
    """Derive search keywords based on the candidate's active profile."""
    queries = []
    skills = profile.skills or {}
    languages = skills.get("languages", [])
    frameworks = skills.get("frameworks", [])
    
    # Core focus query
    if "Python" in languages and "FastAPI" in frameworks:
        queries.append('"AI Engineer" Bangalore')
        queries.append('"ML Engineer" Remote')
    if "Kotlin" in languages or "Android" in str(profile.projects):
        queries.append('"Android Developer" Kotlin')
    
    # Fallback default queries
    if not queries:
        queries = ["AI Engineer Remote", "Software Engineer Fresher"]
    
    return queries

def compute_source_hash(company: str, title: str, location: str) -> str:
    """Generate a unique SHA-256 hash for deduplication."""
    input_str = f"{company.strip().lower()}|{title.strip().lower()}|{(location or '').strip().lower()}"
    return hashlib.sha256(input_str.encode("utf-8")).hexdigest()

def scrape_yc_jobs_rss() -> list:
    """Fetch live public jobs from YC Work at a Startup RSS feed (best efforts)."""
    jobs = []
    url = "https://www.workatastartup.com/jobs/rss"
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, timeout=10.0)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                for item in root.findall(".//item"):
                    title_full = item.find("title").text or ""
                    # Title format is usually: "Job Title at Company (Location)"
                    company = "YC Startup"
                    title = title_full
                    if " at " in title_full:
                        parts = title_full.split(" at ")
                        title = parts[0].strip()
                        company_info = parts[1].split("(")
                        company = company_info[0].strip()
                    
                    link = item.find("link").text or ""
                    desc = item.find("description").text or ""
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "description": desc,
                        "skills_required": ["Python", "TypeScript", "React"],  # Default guess
                        "location": "Remote",
                        "remote": True,
                        "salary_min": 90000,
                        "salary_max": 150000,
                        "experience_years_min": 1,
                        "experience_years_max": 3,
                        "source": "YC Jobs RSS",
                        "source_url": link,
                        "posted_date": date.today()
                    })
    except Exception as e:
        logger.warning(f"Failed to scrape YC RSS feed: {e}")
    return jobs

def discover_and_save_jobs(db: Session, profile: Profile) -> dict:
    """
    Main job discovery coordinator. Generates queries, fetches new jobs,
    deduplicates them, and saves new entries.
    """
    queries = generate_search_queries(profile)
    logger.info(f"Generated search queries: {queries}")

    discovered_jobs = []

    # 1. Scrape live RSS feed
    rss_jobs = scrape_yc_jobs_rss()
    discovered_jobs.extend(rss_jobs)

    # 2. Add mock jobs for rich local database matching
    discovered_jobs.extend(MOCK_JOBS_DB)

    new_count = 0
    dup_count = 0

    for job_data in discovered_jobs:
        shash = compute_source_hash(job_data["company"], job_data["title"], job_data["location"])
        
        # Check if already exists
        existing_job = db.query(Job).filter(Job.source_hash == shash).first()
        if existing_job:
            # Skip or merge source URL
            dup_count += 1
            continue
        
        # Save new job
        new_job = Job(
            title=job_data["title"],
            company=job_data["company"],
            description=job_data["description"],
            skills_required=job_data["skills_required"],
            location=job_data["location"],
            remote=job_data["remote"],
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            experience_years_min=job_data.get("experience_years_min", 0),
            experience_years_max=job_data.get("experience_years_max", 2),
            source=job_data["source"],
            source_url=job_data["source_url"],
            source_hash=shash,
            posted_date=job_data.get("posted_date", date.today()),
            status="discovered"
        )
        db.add(new_job)
        new_count += 1

    db.commit()
    logger.info(f"Job discovery complete: {new_count} new, {dup_count} duplicates.")
    return {"new_jobs_count": new_count, "duplicate_jobs_count": dup_count}
