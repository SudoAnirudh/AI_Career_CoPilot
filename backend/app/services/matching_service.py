import logging
import math
import json
import re
from sqlalchemy.orm import Session
from app.models import Job, Profile
from app.services.llm import call_nvidia_nim

logger = logging.getLogger("app.services.matching")

def clean_and_parse_json(json_str: str, default_val: dict) -> dict:
    """
    Strips single-line comments, multi-line comments, and parses a JSON string,
    cleaning up project_alignments and other fields to fit the expected structure.
    """
    import re
    # Extract first valid JSON object based on brace matching depth
    first_brace = json_str.find('{')
    if first_brace != -1:
        depth = 0
        in_string = False
        escape = False
        target_str = ""
        for i in range(first_brace, len(json_str)):
            char = json_str[i]
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        target_str = json_str[first_brace:i+1]
                        break
        if not target_str:
            target_str = json_str[first_brace:]
    else:
        target_str = json_str
        
    try:
        # Remove single-line comments like // ... (careful with https://)
        target_str = re.sub(r'(?<!:)\/\/[^\n]*', '', target_str)
        # Remove multi-line comments /* ... */
        target_str = re.sub(r'\/\*.*?\*\/', '', target_str, flags=re.DOTALL)
        
        data = json.loads(target_str.strip())
    except Exception as e:
        logger.warning(f"JSON clean parsing failed: {e}")
        return default_val

    # Standardize project_alignments
    raw_alignments = data.get("project_alignments", [])
    standardized_alignments = []
    if isinstance(raw_alignments, list):
        for item in raw_alignments:
            if isinstance(item, dict):
                proj_name = item.get("project") or item.get("name") or "Project"
                jd_el = item.get("jd_element") or item.get("description") or "Aligned Stack"
                sim_val = item.get("similarity") or 0.8
                try:
                    sim_val = float(sim_val)
                except ValueError:
                    sim_val = 0.8
                standardized_alignments.append({
                    "project": str(proj_name),
                    "jd_element": str(jd_el),
                    "similarity": sim_val
                })
            elif isinstance(item, str):
                standardized_alignments.append({
                    "project": item,
                    "jd_element": "Aligned stack and skills",
                    "similarity": 0.8
                })
        data["project_alignments"] = standardized_alignments
    else:
        data["project_alignments"] = []
        
    # Standardize lists
    for list_field in ["matched_skills", "missing_skills"]:
        if list_field not in data or not isinstance(data[list_field], list):
            data[list_field] = []
        else:
            data[list_field] = [str(x) for x in data[list_field]]
            
    # Standardize string fields
    if "summary" not in data:
        data["summary"] = default_val.get("summary", "")
    else:
        data["summary"] = str(data["summary"])
        
    if "tailoring_advice" not in data:
        data["tailoring_advice"] = default_val.get("tailoring_advice", "")
    elif isinstance(data["tailoring_advice"], list):
        data["tailoring_advice"] = "\n".join([f"• {x}" for x in data["tailoring_advice"]])
    else:
        data["tailoring_advice"] = str(data["tailoring_advice"])
        
    # Set overall score if present
    if "score" in data:
        try:
            data["score"] = float(data["score"])
        except ValueError:
            data["score"] = default_val.get("score", 70.0)
    else:
        data["score"] = default_val.get("score", 70.0)
        
    if "recommendation" not in data:
        data["recommendation"] = default_val.get("recommendation", "apply")
        
    return data

# Simple tf-idf/cosine similarity implementation for fallback/offline calculations
def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate basic cosine similarity between two texts using word counts."""
    if not text1 or not text2:
        return 0.0
    
    # Lowercase and tokenise words
    words1 = re_tokenize(text1.lower())
    words2 = re_tokenize(text2.lower())
    
    if not words1 or not words2:
        return 0.0
        
    # Vectorise
    vec1 = {}
    vec2 = {}
    for w in words1:
        vec1[w] = vec1.get(w, 0) + 1
    for w in words2:
        vec2[w] = vec2.get(w, 0) + 1
        
    # Cosine similarity
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return float(numerator) / denominator

def re_tokenize(text: str) -> list:
    """Utility to extract words from text."""
    return re.findall(r'\w+', text)


def calculate_skills_match(profile_skills: dict, job_skills: list) -> float:
    """Calculate ratio of job skills found in candidate profile."""
    if not job_skills:
        return 1.0  # If job doesn't specify skills, assume full match
        
    flat_profile_skills = set()
    for cat, items in profile_skills.items():
        if isinstance(items, list):
            for item in items:
                flat_profile_skills.add(item.lower())
                
    job_skills_lower = [s.lower() for s in job_skills]
    matches = [s for s in job_skills_lower if s in flat_profile_skills]
    
    return len(matches) / len(job_skills_lower)

def calculate_project_relevance(projects: list, job_description: str) -> float:
    """Calculate maximum similarity between any candidate project and the job description."""
    if not projects or not job_description:
        return 0.0
        
    max_sim = 0.0
    for proj in projects:
        proj_text = f"{proj.get('name', '')} {proj.get('description', '')} {' '.join(proj.get('tech', []))}"
        sim = calculate_text_similarity(proj_text, job_description)
        if sim > max_sim:
            max_sim = sim
            
    return max_sim

def calculate_role_title_similarity(profile_projects: list, job_title: str) -> float:
    """Check how close the job title is to the candidate's target focus (AI/ML or Android)."""
    title_lower = job_title.lower()
    
    # We can infer candidate's projects focus
    project_text = " ".join([p.get('name', '') + " " + p.get('description', '') for p in profile_projects])
    
    score = 0.5
    if "ai" in title_lower or "ml" in title_lower or "machine learning" in title_lower:
        if "gemini" in project_text.lower() or "llm" in project_text.lower() or "ai" in project_text.lower():
            score = 0.95
        else:
            score = 0.70
    elif "android" in title_lower or "mobile" in title_lower:
        if "kotlin" in project_text.lower() or "compose" in project_text.lower():
            score = 0.95
        else:
            score = 0.70
            
    return score

def run_matching_pipeline(db: Session, job: Job, profile: Profile) -> dict:
    """
    Score a single job listing against a candidate's profile.
    Uses the 5-component weighted formula plus penalties.
    """
    # 1. Skills overlap (40%)
    profile_skills = profile.skills or {}
    job_skills = job.skills_required or []
    skill_score = calculate_skills_match(profile_skills, job_skills)
    
    # 2. Project relevance (25%)
    projects = profile.projects or []
    project_score = calculate_project_relevance(projects, job.description or "")
    
    # 3. Technology stack match (20%)
    # We count this as the overlap of tool/framework skills specifically mentioned in job desc
    tech_score = skill_score # Simplification mapping to overall skill overlap ratio for this step
    
    # 4. Role Title Similarity (10%)
    role_score = calculate_role_title_similarity(projects, job.title)
    
    # 5. Education Match (5%)
    education = profile.education or []
    edu_score = 0.5
    for edu in education:
        degree = edu.get("degree", "").lower()
        if "b.e." in degree or "b.tech" in degree or "computer science" in degree or "artificial intelligence" in degree:
            edu_score = 1.0
            
    # Weighted base score (0 - 100)
    base_score = (
        (skill_score * 40.0) +
        (project_score * 25.0) +
        (tech_score * 20.0) +
        (role_score * 10.0) +
        (edu_score * 5.0)
    )
    
    # Clamp base score
    base_score = min(max(base_score, 0.0), 100.0)
    
    # Penalties
    penalties = 0.0
    
    # Experience penalty: -15 if experience required > user YOE
    # Anirudh graduates in 2026, meaning YOE is 0 (as of 2026)
    user_yoe = 0
    job_req_yoe = job.experience_years_min or 0
    if job_req_yoe > user_yoe:
        # Penalise based on gap
        gap = job_req_yoe - user_yoe
        if gap > 1:
            penalties += 15.0
            
    # Location penalty: -10 if onsite in unsupported city
    # Anirudh is remote-friendly and location is Bangalore/Kerala.
    # If onsite elsewhere (e.g. Mumbai, Chennai, Delhi) without remote option, apply -10
    if job.location and not job.remote:
        loc = job.location.lower()
        if "bangalore" not in loc and "bengaluru" not in loc and "kozhikode" not in loc and "kerala" not in loc:
            penalties += 10.0
            
    final_score = max(base_score - penalties, 0.0)
    
    # Create prompt to request AI-generated explanation
    explanation_prompt = f"""
    You are an expert ATS (Applicant Tracking System) optimizer and career advisor analyzing job fit.
    
    User Profile Skills:
    {json.dumps(profile_skills)}
    Projects: {json.dumps(projects)}
    
    Job Title: {job.title}
    Company: {job.company}
    Job Description: {job.description[:1200]}...
    
    We calculated a match score of {final_score:.1f}/100.
    
    Return a JSON explanation matching this format:
    {{
      "score": {final_score:.1f},
      "matched_skills": ["List", "of", "matched", "skills/technologies"],
      "missing_skills": ["List", "of", "missing", "skills/technologies requested in the Job Description"],
      "project_alignments": [
        {{"project": "Project Name", "jd_element": "What matches in Job Description", "similarity": 0.85}}
      ],
      "summary": "2-3 sentences explaining why this is a good or poor fit.",
      "tailoring_advice": "Specific actionable recommendation on how to modify your resume projects, summary, or skills to match this job description.",
      "recommendation": "apply" or "apply_with_note" or "skip"
    }}
    """
    
    llm_explanation_raw = call_nvidia_nim(explanation_prompt)
    
    matched = [s for s in job_skills if s.lower() in [p.lower() for cat, items in profile_skills.items() for p in items]]
    missing = [s for s in job_skills if s.lower() not in [p.lower() for cat, items in profile_skills.items() for p in items]]
    fallback_json = {
        "score": final_score,
        "matched_skills": matched[:5] if matched else ["Python", "FastAPI", "React"],
        "missing_skills": missing[:5] if missing else ["Generative AI", "LangChain"],
        "project_alignments": [{"project": projects[0].get("name") if projects else "None", "jd_element": job.title, "similarity": 0.8}],
        "summary": f"Good match based on your projects and development stack. Required experience is {job.experience_years_min or 0} years.",
        "tailoring_advice": f"Emphasize your hands-on experience with {job.title} related stacks and your active AI/ML engineering projects.",
        "recommendation": "apply" if final_score > 70 else "skip"
    }
    
    explanation_json = clean_and_parse_json(llm_explanation_raw, fallback_json)
        
    # Inject components so that frontend has the metrics breakdown
    explanation_json["components"] = {
        "skills_overlap": skill_score,
        "project_relevance": project_score,
        "technology_stack": tech_score,
        "role_title_similarity": role_score,
        "education_match": edu_score
    }
    
    # Update job object in database
    job.match_score = final_score
    job.match_explanation = explanation_json
    db.commit()
    
    return {"job_id": job.id, "score": final_score, "explanation": explanation_json}
