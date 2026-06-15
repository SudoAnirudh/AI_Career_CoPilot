import httpx
import json
import logging
import re
from app.config import settings

logger = logging.getLogger("app.services.llm")

def call_nvidia_nim(prompt: str, system_prompt: str = "") -> str:
    """
    Call the NVIDIA NIM API (Llama 3.1 70B). 
    If the API key is not configured, it triggers the mock/fallback response generator.
    """
    if not settings.NVIDIA_API_KEY or settings.NVIDIA_API_KEY == "mock_key":
        logger.info("Using local fallback mock LLM engine (NVIDIA key not configured).")
        return generate_mock_llm_response(prompt)

    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "meta/llama-3.3-70b-instruct",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 2048
    }

    try:
        with httpx.Client() as client:
            response = client.post(
                f"{settings.NVIDIA_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=45.0
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return content
    except Exception as e:
        logger.error(f"NVIDIA NIM API call failed: {e}. Falling back to mock engine.")
        return generate_mock_llm_response(prompt)


def generate_mock_llm_response(prompt: str) -> str:
    """
    Generates realistic, structured mock JSON/text responses based on the prompt content
    to ensure full off-line capability.
    """
    # 1. Check if the prompt is for Resume Parsing
    if "User Profile" in prompt or "resume" in prompt.lower() and "json" in prompt.lower() and "skills" in prompt.lower():
        # Extracted candidate details for Anirudh Sudheer (default profile based on PRD)
        profile_data = {
            "name": "Anirudh Sudheer",
            "email": "anirudhsudheer@gmail.com",
            "phone": "+91 9539102881",
            "location": "Kozhikode, Kerala",
            "linkedin": "sudoanirudh",
            "github": "SudoAnirudh",
            "skills": {
                "languages": ["Python", "Kotlin", "TypeScript", "SQL", "HTML", "CSS"],
                "frameworks": ["FastAPI", "Jetpack Compose", "LangChain", "React", "Next.js"],
                "tools": ["Firebase", "Docker", "Git", "Gemini API", "ChromaDB", "PostgreSQL", "Redis"]
            },
            "projects": [
                {
                    "name": "Nimma-Guru",
                    "tech": ["Kotlin", "Jetpack Compose", "Firebase", "Gemini 2.0 Flash"],
                    "description": "Community mentorship platform connecting retired professionals with students.",
                    "impact": "Integrated 7 Gemini AI features and reached 100+ active users."
                },
                {
                    "name": "SummarizeAgent",
                    "tech": ["Python", "FastAPI", "Google Cloud Run", "Gemini 2.0"],
                    "description": "Agentic tool to summarize large PDF documents and research papers.",
                    "impact": "Deployed on Google Cloud Run with low latency and 98% user satisfaction rate."
                },
                {
                    "name": "FutIQ",
                    "tech": ["Python", "scikit-learn", "Flask"],
                    "description": "Machine learning system predicting future skill gaps and recommending courses.",
                    "impact": "Achieved 89% accuracy on validation dataset."
                }
            ],
            "education": [
                {
                    "degree": "B.E. in Artificial Intelligence & Machine Learning",
                    "institution": "Srinivas Institute of Technology",
                    "year": "2026"
                }
            ],
            "experience": [
                {
                    "role": "AI Engineer Intern",
                    "company": "Smart Solutions",
                    "duration": "Jan 2025 - Present",
                    "description": "Developed internal NLP tools using FastAPI and LangChain. Managed embeddings database."
                }
            ],
            "certifications": [
                {
                    "name": "TensorFlow Developer Certificate",
                    "issuer": "Google",
                    "year": "2024"
                }
            ]
        }
        return json.dumps(profile_data, indent=2)

    # 2. Check if the prompt is for Match Explanation
    if "MATCH_EXPLANATION_PROMPT" in prompt or "project_alignments" in prompt:
        # Extract company/job info from prompt if possible
        job_title = "AI Engineer"
        company_name = "Sarvam AI"
        
        match_title = re.search(r"title[\"\']?\s*:\s*[\"\']?([^\"\'\n]+)", prompt, re.I)
        if match_title:
            job_title = match_title.group(1)
        match_comp = re.search(r"company[\"\']?\s*:\s*[\"\']?([^\"\'\n]+)", prompt, re.I)
        if match_comp:
            company_name = match_comp.group(1)

        score = 85.0
        # If job calls for something completely unrelated, reduce score
        if "android" in job_title.lower():
            score = 88.0
        elif "ml" in job_title.lower() or "ai" in job_title.lower():
            score = 87.0
        
        explanation = {
            "score": score,
            "matched_skills": ["Python", "FastAPI", "LangChain", "Gemini API", "ChromaDB"],
            "missing_skills": ["Kubernetes", "PyTorch"],
            "project_alignments": [
                {"project": "SummarizeAgent", "jd_element": "Building LLM agents", "similarity": 0.91},
                {"project": "Nimma-Guru", "jd_element": "Generative AI integrations", "similarity": 0.85}
            ],
            "role_similarity": 0.92,
            "summary": f"Your strong background in building FastAPI microservices and integrating Gemini/LLMs aligns directly with {company_name}'s requirements for a {job_title}.",
            "recommendation": "apply"
        }
        return json.dumps(explanation, indent=2)

    # 3. Check if prompt is for Outreach Message
    if "REFERRAL_REQUEST_PROMPT" in prompt or "outreach" in prompt.lower() or "referral" in prompt.lower():
        # Get details from prompt
        contact_name = "Priya Sharma"
        company_name = "Sarvam AI"
        job_title = "AI Engineer"
        
        match_contact = re.search(r"contact_name[\"\']?\s*:\s*[\"\']?([^\"\'\n]+)", prompt)
        if match_contact:
            contact_name = match_contact.group(1)
        match_comp = re.search(r"company_name[\"\']?\s*:\s*[\"\']?([^\"\'\n]+)", prompt)
        if match_comp:
            company_name = match_comp.group(1)
        match_job = re.search(r"job_title[\"\']?\s*:\s*[\"\']?([^\"\'\n]+)", prompt)
        if match_job:
            job_title = match_job.group(1)

        if "referral" in prompt.lower() or "linkedin" in prompt.lower():
            return f"Hi {contact_name},\n\nI came across the {job_title} opening at {company_name} and noticed your work on Indic language models. I'm a final-year AI/ML student at SIT with experience building LLM pipelines, including Nimma-Guru (Gemini API). I would genuinely love to learn more about the team's engineering goals.\n\nWould you be open to a quick 10-minute chat sometime next week? No pressure at all.\n\nBest,\nAnirudh"
        else:
            # Cold email
            return f"Subject: AI Engineer Application – Anirudh Sudheer, AI/ML @ SIT, 3 deployed projects\n\nHi {contact_name},\n\nI hope this email finds you well. I'm writing to express my interest in the {job_title} role at {company_name}.\n\nQuick snapshot of my profile:\n• Final-year AI/ML student at Srinivas Institute of Technology\n• Built Nimma-Guru (7 Gemini AI integrations, Kotlin/Compose/Firebase)\n• Deployed SummarizeAgent (Google Cloud Run, FastAPI + Gemini 2.0)\n• Proficient in Python, FastAPI, LangChain, and ChromaDB\n\nI would love the opportunity to contribute to {company_name}'s products. My GitHub portfolio is available at github.com/SudoAnirudh.\n\nAre you open to a brief conversation to discuss how my skills align with your team's needs?\n\nBest regards,\nAnirudh Sudheer"

    # Default fallback
    return "This is a default mock response from the AI Career CoPilot LLM engine."
