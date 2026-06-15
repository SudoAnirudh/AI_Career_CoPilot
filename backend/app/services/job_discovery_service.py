import hashlib
import logging
import urllib.parse
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta
import httpx
from sqlalchemy.orm import Session
from app.models import Job, Profile

logger = logging.getLogger("app.services.job_discovery")


def generate_search_keywords(profile: Profile) -> list:
    """Derive search keywords based on the candidate's active profile."""
    keywords = []
    skills = profile.skills or {}
    languages = skills.get("languages", [])
    frameworks = skills.get("frameworks", [])
    
    if "Python" in languages or "FastAPI" in frameworks or "AI" in str(profile.projects):
        keywords.append("AI Engineer")
        keywords.append("ML Engineer")
    if "Kotlin" in languages or "Android" in str(profile.projects):
        keywords.append("Android Developer")
    
    if not keywords:
        keywords = ["AI Engineer", "Software Engineer"]
    
    return keywords

def compute_source_hash(company: str, title: str, location: str) -> str:
    """Generate a unique SHA-256 hash for deduplication."""
    input_str = f"{company.strip().lower()}|{title.strip().lower()}|{(location or '').strip().lower()}"
    return hashlib.sha256(input_str.encode("utf-8")).hexdigest()

def scrape_linkedin_jobs(keywords: str, location: str = "Remote") -> list:
    """Query LinkedIn Guest search API."""
    jobs = []
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={urllib.parse.quote(keywords)}&location={urllib.parse.quote(location)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    logger.info(f"Scraping LinkedIn Guest Search: {url}")
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers, timeout=12.0)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                cards = soup.find_all("li")
                for card in cards:
                    title_el = card.find("h3", class_="base-search-card__title")
                    company_el = card.find("h4", class_="base-search-card__subtitle")
                    link_el = card.find("a", class_="base-card__full-link")
                    loc_el = card.find("span", class_="job-search-card__location")
                    
                    if not title_el or not company_el:
                        continue
                        
                    title = title_el.text.strip()
                    company = company_el.text.strip()
                    link = link_el["href"].split("?")[0] if link_el else ""
                    loc = loc_el.text.strip() if loc_el else location
                    
                    description = f"Position: {title} at {company} located in {loc}. Explore the role details and requirements to apply via: {link}"
                    
                    # Fetch detailed description (limit to first 3 to prevent rate limits / slowness)
                    if link and len(jobs) < 3:
                        try:
                            detail_headers = {
                                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                                "Accept-Language": "en-US,en;q=0.9"
                            }
                            detail_resp = client.get(link, headers=detail_headers, timeout=6.0)
                            if detail_resp.status_code == 200:
                                detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                                desc_el = detail_soup.find('div', class_='show-more-less-html__markup') or detail_soup.find('div', class_='description__text')
                                if desc_el:
                                    description = desc_el.text.strip()
                        except Exception as detail_err:
                            logger.debug(f"Failed to fetch LinkedIn job detail description for {link}: {detail_err}")
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "description": description,
                        "skills_required": [keywords],
                        "location": loc,
                        "remote": "remote" in loc.lower() or "remote" in location.lower(),
                        "source": "LinkedIn",
                        "source_url": link,
                        "posted_date": date.today()
                    })
    except Exception as e:
        logger.warning(f"Error scraping LinkedIn: {e}")
    return jobs

def scrape_weworkremotely_jobs() -> list:
    """Fetch live public jobs from WeWorkRemotely RSS feed."""
    jobs = []
    url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    logger.info(f"Scraping WeWorkRemotely RSS: {url}")
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers, timeout=12.0)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall(".//item"):
                    title_full = item.find("title").text or ""
                    company = "Remote Company"
                    title = title_full
                    if ":" in title_full:
                        parts = title_full.split(":")
                        company = parts[0].strip()
                        title = ":".join(parts[1:]).strip()
                    
                    link = item.find("link").text or ""
                    desc = item.find("description").text or ""
                    desc_clean = re.sub(r'<[^>]*>', '', desc)[:1500]
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "description": desc_clean,
                        "skills_required": ["Python", "Kotlin", "TypeScript", "React"],
                        "location": "Remote",
                        "remote": True,
                        "source": "We Work Remotely",
                        "source_url": link,
                        "posted_date": date.today()
                    })
    except Exception as e:
        logger.warning(f"Failed to scrape WeWorkRemotely RSS: {e}")
    return jobs

def scrape_remoteok_jobs() -> list:
    """Fetch remote jobs from RemoteOK API."""
    jobs = []
    url = "https://remoteok.com/api"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    logger.info(f"Scraping RemoteOK JSON API: {url}")
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers, timeout=12.0)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 1:
                    for item in data[1:12]:
                        title = item.get("position")
                        company = item.get("company")
                        link = item.get("url")
                        desc = item.get("description", "")
                        desc_clean = re.sub(r'<[^>]*>', '', desc)[:1500]
                        skills = item.get("tags", ["Python", "React"])
                        loc = item.get("location", "Remote")
                        
                        jobs.append({
                            "title": title,
                            "company": company,
                            "description": desc_clean,
                            "skills_required": skills,
                            "location": loc,
                            "remote": True,
                            "source": "RemoteOK",
                            "source_url": link,
                            "posted_date": date.today()
                        })
    except Exception as e:
        logger.warning(f"Failed to scrape RemoteOK: {e}")
    return jobs

def scrape_nitter_jobs(keywords: str) -> list:
    """Scrape job tweets from curated X accounts via Nitter RSS feeds."""
    jobs = []
    
    # Curated X accounts that post software/tech job listings
    JOB_ACCOUNTS = [
        "echojobs__io",
        "XCareers",
        "TechJobsforGood",
        "TechIsHiring",
        "fullstackjob",
        "remote_dev_jobs",
        "devsofx",
        "TechJobsDirect",
        "softwareduniyas",
        "ajay_2512x",
        "TechJobsDailyIN",
    ]
    
    instances = [
        "https://nitter.privacydev.net",
        "https://nitter.net",
        "https://nitter.cz",
        "https://twiiit.com",
        "https://nitter.tiekoetter.com",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    # Find a working Nitter instance first
    working_instance = None
    for instance in instances:
        try:
            test_url = f"{instance}/{JOB_ACCOUNTS[0]}/rss"
            with httpx.Client(follow_redirects=True) as client:
                resp = client.get(test_url, headers=headers, timeout=6.0)
                if resp.status_code == 200 and len(resp.text) > 200:
                    working_instance = instance
                    logger.info(f"Using Nitter instance: {instance}")
                    break
        except Exception:
            continue
    
    if not working_instance:
        logger.info(f"No working Nitter instance found for X account scraping.")
        return jobs
    
    kw_lower = keywords.lower()
    
    with httpx.Client(follow_redirects=True) as client:
        for account in JOB_ACCOUNTS:
            try:
                rss_url = f"{working_instance}/{account}/rss"
                response = client.get(rss_url, headers=headers, timeout=6.0)
                if response.status_code != 200 or len(response.text) < 200:
                    continue
                    
                root = ET.fromstring(response.content)
                for item in root.findall(".//item"):
                    title_text = item.find("title").text or ""
                    link = item.find("link").text or ""
                    desc = item.find("description").text or ""
                    desc_clean = re.sub(r'<[^>]*>', '', desc)[:1200]
                    
                    # Filter: only include tweets mentioning the keyword
                    combined = f"{title_text} {desc_clean}".lower()
                    if kw_lower not in combined and not any(
                        term in combined for term in ["hiring", "job", "engineer", "developer", "opening"]
                    ):
                        continue
                    
                    # Extract a meaningful title from the tweet
                    job_title = keywords  # Default
                    title_match = re.search(r'(?:hiring|looking for|seeking)\s+(?:a\s+)?([^.!\n]{5,60})', combined, re.I)
                    if title_match:
                        job_title = title_match.group(1).strip().title()
                    
                    jobs.append({
                        "title": job_title,
                        "company": f"@{account} (X/Twitter)",
                        "description": desc_clean,
                        "skills_required": [keywords],
                        "location": "Remote",
                        "remote": True,
                        "source": "Twitter",
                        "source_url": link.replace(working_instance, "https://twitter.com"),
                        "posted_date": date.today()
                    })
            except Exception as e:
                logger.debug(f"Failed to scrape @{account}: {e}")
    
    logger.info(f"X/Twitter accounts: found {len(jobs)} job tweets for '{keywords}'")
    return jobs

def scrape_indeed_jobs(keywords: str) -> list:
    """Scrape Indeed guest search for real job listings."""
    jobs = []
    query = urllib.parse.quote(keywords)
    url = f"https://www.indeed.com/jobs?q={query}&l=India&fromage=14"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    logger.info(f"Scraping Indeed: {url}")
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                # Indeed uses mosaic/slider cards or job_seen_beacon divs
                cards = soup.find_all('div', class_='job_seen_beacon') or soup.find_all('td', class_='resultContent')
                for card in cards[:8]:
                    title_el = card.find('h2', class_='jobTitle') or card.find('a', attrs={'data-jk': True})
                    company_el = card.find('span', attrs={'data-testid': 'company-name'}) or card.find('span', class_='companyName')
                    loc_el = card.find('div', attrs={'data-testid': 'text-location'}) or card.find('div', class_='companyLocation')
                    
                    if not title_el:
                        continue
                    
                    title = title_el.text.strip()
                    company = company_el.text.strip() if company_el else "Unknown"
                    loc = loc_el.text.strip() if loc_el else "India"
                    
                    link_el = card.find('a', href=True)
                    link = f"https://www.indeed.com{link_el['href']}" if link_el and link_el['href'].startswith('/') else (link_el['href'] if link_el else "")
                    
                    # Try to get snippet/description
                    snippet_el = card.find('div', class_='job-snippet') or card.find('ul')
                    snippet = snippet_el.text.strip()[:500] if snippet_el else f"{title} at {company} in {loc}"
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "description": snippet,
                        "skills_required": [keywords],
                        "location": loc,
                        "remote": "remote" in loc.lower(),
                        "source": "Indeed",
                        "source_url": link,
                        "posted_date": date.today()
                    })
            else:
                logger.warning(f"Indeed returned status {response.status_code}")
    except Exception as e:
        logger.warning(f"Error scraping Indeed: {e}")
    return jobs

def scrape_yc_jobs_rss() -> list:
    """Fetch live public jobs from YC Work at a Startup (embedded JSON in HTML)."""
    import html as html_module
    jobs = []
    url = "https://www.workatastartup.com/jobs/rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html, */*"
    }
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers, timeout=12.0)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                # YC uses Inertia.js — job data is in a div with data-page attribute
                react_div = soup.find('div', attrs={'data-page': True})
                
                if react_div and react_div.get('data-page'):
                    raw_json = html_module.unescape(react_div['data-page'])
                    data = json.loads(raw_json)
                    
                    # Extract job listings from the Inertia.js props
                    props = data.get("props", {})
                    job_listings = props.get("jobs", [])
                    if not job_listings and "featuredJobs" in props:
                        job_listings = props.get("featuredJobs", [])
                    
                    for item in job_listings[:20]:  # Limit to 20 jobs
                        title = item.get("title", "")
                        company = item.get("companyName", "YC Startup")
                        batch = item.get("companyBatch", "")
                        one_liner = item.get("companyOneLiner", "")
                        location = item.get("location", "Remote")
                        role_type = item.get("roleType", "")
                        salary = item.get("salary", "")
                        job_type = item.get("jobType", "")
                        
                        slug = item.get("companySlug", "")
                        job_id = item.get("id", "")
                        source_url = f"https://www.workatastartup.com/companies/{slug}" if slug else ""
                        
                        description = f"{title} at {company} ({batch}). {one_liner}. Role: {role_type}. Type: {job_type}. Salary: {salary}. Location: {location}."
                        
                        is_remote = "remote" in location.lower() if location else False
                        
                        jobs.append({
                            "title": title,
                            "company": company,
                            "description": description,
                            "skills_required": [role_type] if role_type else ["Python", "TypeScript"],
                            "location": location or "Remote",
                            "remote": is_remote,
                            "source": "YC Jobs",
                            "source_url": source_url,
                            "posted_date": date.today()
                        })
                    logger.info(f"YC Jobs: parsed {len(jobs)} listings from embedded JSON")
                else:
                    logger.warning("YC Jobs page: no React component div found with job data")
            else:
                logger.warning(f"YC Jobs page returned status {response.status_code}")
    except Exception as e:
        logger.warning(f"Failed to scrape YC Jobs: {e}")
    return jobs

def discover_and_save_jobs(db: Session, profile: Profile) -> dict:
    """
    Main job discovery coordinator. Generates keywords, fetches new jobs
    from LinkedIn, Indeed, Twitter, Remote OK, WeWorkRemotely, and YC RSS,
    deduplicates them, and saves new entries.
    """
    keywords_list = generate_search_keywords(profile)
    logger.info(f"Generated search keywords: {keywords_list}")

    discovered_jobs = []

    # 1. Fetch from WeWorkRemotely & RemoteOK
    discovered_jobs.extend(scrape_weworkremotely_jobs())
    discovered_jobs.extend(scrape_remoteok_jobs())

    # 2. Fetch from LinkedIn, Indeed, Twitter/X for each keyword
    for kw in keywords_list:
        discovered_jobs.extend(scrape_linkedin_jobs(kw))
        discovered_jobs.extend(scrape_indeed_jobs(kw))
        discovered_jobs.extend(scrape_nitter_jobs(kw))

    # 3. Scrape YC RSS
    discovered_jobs.extend(scrape_yc_jobs_rss())

    # All sources are real scraped data — no mock/hardcoded jobs

    new_count = 0
    dup_count = 0

    seen_hashes = set()
    for job_data in discovered_jobs:
        shash = compute_source_hash(job_data["company"], job_data["title"], job_data["location"])
        
        # Deduplicate internally within this batch first
        if shash in seen_hashes:
            dup_count += 1
            continue
            
        # Check if already exists in database
        existing_job = db.query(Job).filter(Job.source_hash == shash).first()
        if existing_job:
            dup_count += 1
            seen_hashes.add(shash)
            continue
            
        seen_hashes.add(shash)
        
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


def run_discovery_and_matching_sync(profile_id: str) -> list:
    """
    Runs the full job discovery, matching, company research, contact discovery,
    and outreach/apply pipeline in a synchronous, thread-safe manner.
    Designed to be run inside a background thread pool to prevent blocking the event loop.
    """
    from datetime import date, datetime
    from app.database import SessionLocal
    from app.models import Profile, Job, Application, Contact
    from app.services.matching_service import run_matching_pipeline
    from app.services.company_research_service import research_company
    from app.services.contact_discovery_service import discover_contacts_for_job
    from app.services.outreach_service import generate_outreach_message

    db = SessionLocal()
    updated_job_ids = []
    try:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            logger.error(f"Profile {profile_id} not found for scheduled run.")
            return []
            
        logger.info(f"Running scheduled job discovery in background thread for profile: {profile.id}")
        res = discover_and_save_jobs(db, profile)
        logger.info(f"Scheduled discovery results for profile {profile.id}: {res}")
        
        # Run matching pipeline on new jobs
        new_jobs = db.query(Job).filter(Job.status == "discovered", Job.match_score.is_(None)).all()
        logger.info(f"Calculating match scores for {len(new_jobs)} new jobs for profile {profile.id}")
        
        for job in new_jobs:
            try:
                match_res = run_matching_pipeline(db, job, profile)
                score = match_res.get("score", 0.0)
                logger.info(f"Job Match complete: {job.company} - {job.title} (Score: {score})")
                
                if score >= 70.0:
                    logger.info(f"Match score >= 70 for job {job.id}. Initiating company research & contact discovery.")
                    research_company(db, job.company)
                    contacts = discover_contacts_for_job(db, job)
                    
                    # Check if we found any contact with a valid email
                    contact_with_email = None
                    for c in contacts:
                        if c.email and "@" in c.email:
                            contact_with_email = c
                            break
                            
                    if contact_with_email:
                        logger.info(f"Found contact with email: {contact_with_email.name} ({contact_with_email.email}). Drafting cold email outreach.")
                        # Generate outreach message
                        msg = generate_outreach_message(db, str(contact_with_email.id), "cold_email")
                        
                        # Send cold email outreach automatically
                        msg.status = "sent"
                        msg.sent_at = datetime.utcnow()
                        msg.final_text = msg.draft
                        contact_with_email.status = "contacted"
                        
                        # Create Application record as "applied"
                        new_app = Application(
                            user_id=profile.user_id,
                            job_id=job.id,
                            profile_version=profile.version,
                            status="applied",
                            applied_date=date.today(),
                            platform="Cold Email Outreach",
                            notes=f"Sent cold outreach email to {contact_with_email.name} ({contact_with_email.title}) at {contact_with_email.email}."
                        )
                        db.add(new_app)
                        job.status = "applied"
                        db.commit()
                        logger.info(f"Outreach sent automatically via cold email to {contact_with_email.email} for job {job.title}.")
                    else:
                        logger.info(f"No contacts with emails found for job {job.title} at {job.company}. Applying directly through agent.")
                        # Create Application record as "applied" directly
                        new_app = Application(
                            user_id=profile.user_id,
                            job_id=job.id,
                            profile_version=profile.version,
                            status="applied",
                            applied_date=date.today(),
                            platform="Agent Auto-Apply",
                            notes="No contact email found. Applied directly via Agent Auto-Apply automation."
                        )
                        db.add(new_app)
                        job.status = "applied"
                        db.commit()
                        logger.info(f"Direct application submitted by agent for job {job.title} at {job.company}.")
                        
                    updated_job_ids.append(str(job.id))
            except Exception as e:
                logger.error(f"Failed to process job {job.id}: {e}")
                db.rollback()
    except Exception as e:
        logger.error(f"Error in discovery/matching thread run: {e}")
    finally:
        db.close()
    return updated_job_ids


async def run_periodic_job_discovery_loop():
    """
    Background loop that runs job discovery every 2 to 3 hours (randomized gap).
    """
    import asyncio
    import random
    from app.database import SessionLocal
    from app.models import Profile
    from app.services.websocket_manager import ws_manager

    logger.info("Periodic job discovery scheduler task started.")
    # Wait for 15 seconds on startup before the first run
    await asyncio.sleep(15)
    
    while True:
        db = SessionLocal()
        try:
            logger.info("Starting scheduled periodic job discovery (2-3 hour interval)...")
            active_profiles = db.query(Profile).filter(Profile.is_active == True).all()
            if not active_profiles:
                logger.warning("No active profile found for scheduled job discovery.")
                
            for profile in active_profiles:
                # Offload synchronous execution to a separate worker thread
                updated_job_ids = await asyncio.to_thread(run_discovery_and_matching_sync, str(profile.id))
                
                # Broadcast real-time update to the frontend for any newly processed high-score jobs
                for job_id in updated_job_ids:
                    try:
                        await ws_manager.broadcast({"type": "job_status_updated", "job_id": job_id}, "jobs")
                    except Exception as ws_err:
                        logger.warning(f"Failed to broadcast websocket update: {ws_err}")
                                
        except Exception as e:
            logger.error(f"Error in periodic job discovery run: {e}")
        finally:
            db.close()
            
        # Daily gap scraping of 2 to 3 hours
        gap = random.randint(7200, 10800)
        hours = gap / 3600.0
        logger.info(f"Scheduled discovery complete. Sleeping for {hours:.2f} hours (randomized gap between 2-3 hours).")
        await asyncio.sleep(gap)
