import sys
import os
import logging

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_scraping")

# Mock database session for testing
class DummyProfile:
    def __init__(self):
        self.skills = {"languages": ["Python", "JavaScript"], "frameworks": ["FastAPI", "React"]}
        self.projects = ["Built AI Career CoPilot using FastAPI", "Android app with Kotlin"]

def test_scraping():
    from app.services.job_discovery_service import (
        scrape_linkedin_jobs,
        scrape_weworkremotely_jobs,
        scrape_remoteok_jobs,
        scrape_nitter_jobs,
        scrape_indeed_jobs,
        scrape_yc_jobs_rss
    )

    print("=== Testing WeWorkRemotely RSS ===")
    wwr_jobs = scrape_weworkremotely_jobs()
    print(f"WeWorkRemotely count: {len(wwr_jobs)}")
    if wwr_jobs:
        print(f"Sample: {wwr_jobs[0]['title']} @ {wwr_jobs[0]['company']} ({wwr_jobs[0]['source_url']})")

    print("\n=== Testing RemoteOK API ===")
    rok_jobs = scrape_remoteok_jobs()
    print(f"RemoteOK count: {len(rok_jobs)}")
    if rok_jobs:
        print(f"Sample: {rok_jobs[0]['title']} @ {rok_jobs[0]['company']} ({rok_jobs[0]['source_url']})")

    print("\n=== Testing LinkedIn Guest Search ===")
    li_jobs = scrape_linkedin_jobs("AI Engineer")
    print(f"LinkedIn count: {len(li_jobs)}")
    if li_jobs:
        print(f"Sample: {li_jobs[0]['title']} @ {li_jobs[0]['company']} ({li_jobs[0]['source_url']})")

    print("\n=== Testing Indeed Guest Search ===")
    in_jobs = scrape_indeed_jobs("AI Engineer")
    print(f"Indeed count: {len(in_jobs)}")
    if in_jobs:
        print(f"Sample: {in_jobs[0]['title']} @ {in_jobs[0]['company']} ({in_jobs[0]['source_url']})")

    print("\n=== Testing Nitter Twitter RSS ===")
    tw_jobs = scrape_nitter_jobs("AI Engineer")
    print(f"Twitter/Nitter count: {len(tw_jobs)}")
    if tw_jobs:
        print(f"Sample: {tw_jobs[0]['title']} @ {tw_jobs[0]['company']} ({tw_jobs[0]['source_url']})")

    print("\n=== Testing YC RSS ===")
    yc_jobs = scrape_yc_jobs_rss()
    print(f"YC count: {len(yc_jobs)}")
    if yc_jobs:
        print(f"Sample: {yc_jobs[0]['title']} @ {yc_jobs[0]['company']} ({yc_jobs[0]['source_url']})")

if __name__ == "__main__":
    test_scraping()
