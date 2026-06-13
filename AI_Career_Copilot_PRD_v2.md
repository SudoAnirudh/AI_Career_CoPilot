# AI Career Copilot

## Product Requirements Document

**Version:** 2.0  
**Owner:** Anirudh Sudheer  
**GitHub:** SudoAnirudh | **Email:** anirudhsudheer@gmail.com  
**Product Type:** Web Application + Progressive Web App (PWA)  
**Target Users:** Students, Freshers, AI/ML Engineers, Software Engineers, Job Seekers  
**Status:** In Planning  

---

# 1. Vision

AI Career Copilot is an intelligent, agentic job search assistant that continuously discovers opportunities, analyzes your resume, scores job matches, finds referral contacts, generates hyper-personalized outreach, and tracks every application — all in one place.

It acts as a personal AI-powered career team: part recruiter, part researcher, part writer.

---

# 2. Problem Statement

Job searching is fragmented, repetitive, and mentally exhausting.

| What you do today | What it costs |
|---|---|
| Search jobs manually across 10+ boards | 2–3 hours/day |
| Tailor resume per application | 30–60 min/application |
| Search LinkedIn for referral contacts | 1–2 hours per company |
| Write outreach messages from scratch | 20–30 min per message |
| Track applications in a spreadsheet | Constant manual updates |
| Research each company individually | 30–60 min per company |

AI Career Copilot replaces this with a 5-minute daily review workflow.

---

# 3. Product Goals

### Primary Goals
- Centralize the entire job search into a single dashboard
- Automatically discover and score relevant jobs on a schedule
- Generate personalized, high-quality outreach for referrals and recruiters
- Track every application through the full pipeline
- Improve interview conversion rate through better targeting

### Secondary Goals
- Build a portfolio-grade project demonstrating agentic AI systems
- Demonstrate production-ready multi-agent architecture
- Showcase Google Cloud + Gemini + NVIDIA NIM integration

---

# 4. Success Metrics

### User-Facing KPIs
| Metric | Target |
|---|---|
| Jobs discovered per day | > 30 |
| Jobs matched above 80% | > 10/day |
| Outreach messages generated per week | > 20 |
| Referral response rate | > 15% |
| Interview conversion rate | > 8% |

### System KPIs
| Metric | Target |
|---|---|
| Resume parsing accuracy | > 95% |
| Job match accuracy (manual eval) | > 85% |
| Job discovery latency | < 10 seconds |
| Message generation time | < 10 seconds |
| Duplicate job detection rate | > 99% |
| Uptime | > 99.5% |

---

# 5. Target Users

### Primary Persona: "The Active Fresher"
- Recent CS/AI graduate applying to first job
- Applying to 50+ roles simultaneously
- Needs: speed, personalization, referral access
- Pain: Resume tailoring takes too long; doesn't know where to start

### Secondary Persona: "The Transition Engineer"
- 1–3 years experience, switching domains (e.g., backend → AI/ML)
- Needs: Skill gap analysis, targeted matching, warm outreach
- Pain: Generic applications get ignored

### My Profile (Anirudh)
- AI/ML undergraduate at Srinivas Institute of Technology
- Target roles: AI Engineer, ML Engineer, Data Scientist, Product Engineer
- Key projects: PashuSwasthya, Nimma-Guru, FutIQ, SummarizeAgent, SplitSmart
- Skills: Python, FastAPI, Kotlin, Jetpack Compose, Gemini, Firebase, LangChain

---

# 6. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│               Next.js PWA (Frontend)                    │
│    Dashboard | Jobs | Outreach | Tracker | Analytics    │
└────────────────────────┬────────────────────────────────┘
                         │ REST + WebSocket
┌────────────────────────▼────────────────────────────────┐
│                  FastAPI (API Layer)                     │
│         Auth Middleware | Rate Limiting | CORS          │
└──┬──────────┬────────────┬──────────────┬───────────────┘
   │          │            │              │
   ▼          ▼            ▼              ▼
Resume     Job          Matching      Outreach
Service    Discovery    Service       Service
   │       Service         │              │
   ▼          ▼            ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                   Storage Layer                         │
│    PostgreSQL (Supabase)  |  ChromaDB  |  Redis Cache  │
└─────────────────────────────────────────────────────────┘
   │          │            │              │
   ▼          ▼            ▼              ▼
Google      Job         NVIDIA NIM    Gmail/SMTP
Drive      Boards       / Gemini      (Outreach)
```

### Background Workers
- **Celery + Redis**: Async task queue for job scraping, embeddings, matching
- **APScheduler**: Cron jobs for periodic discovery (every 4 hours)
- **WebSocket**: Real-time updates pushed to frontend dashboard

---

# 7. Technology Stack

## Frontend

| Layer | Technology | Reason |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR, PWA support, Vercel deploy |
| Language | TypeScript | Type safety |
| Styling | TailwindCSS | Rapid UI development |
| Components | shadcn/ui | Accessible, composable |
| Charts | Recharts | Analytics dashboard |
| State | Zustand | Lightweight global state |
| Data Fetching | TanStack Query | Caching, sync with server |
| PWA | next-pwa | Offline support, install prompt |
| Auth | Clerk | OAuth (Google), JWT |
| Notifications | react-hot-toast | In-app toasts |

## Backend

| Layer | Technology | Reason |
|---|---|---|
| Language | Python 3.11+ | AI ecosystem |
| Framework | FastAPI | Async, auto-docs, fast |
| Validation | Pydantic v2 | Schema validation |
| ORM | SQLAlchemy 2.0 | Type-safe DB access |
| Task Queue | Celery + Redis | Background job processing |
| Scheduler | APScheduler | Periodic discovery jobs |
| Scraping | Playwright + BeautifulSoup | Dynamic + static job pages |
| PDF Parsing | PyMuPDF + pdfplumber | Resume extraction |

## AI / ML Layer

| Purpose | Model / Library |
|---|---|
| Primary LLM | NVIDIA NIM (Llama 3.1 70B) |
| Fallback LLM | Gemini 2.0 Flash |
| Embeddings | BGE-M3 (via sentence-transformers) |
| Vector DB | ChromaDB |
| Resume NER | spaCy + custom NER pipeline |
| Semantic Search | FAISS (local) / Chroma (persistent) |

## Databases

| DB | Purpose |
|---|---|
| PostgreSQL (Supabase) | Users, Jobs, Applications, Contacts, Messages |
| ChromaDB | Resume embeddings, Job embeddings |
| Redis | Task queue, Cache, Session store |
| Cloudflare R2 | Resume PDF storage |

## Infrastructure

| Service | Tool |
|---|---|
| Frontend Deploy | Vercel |
| Backend Deploy | Railway |
| Database | Supabase (PostgreSQL) |
| Object Storage | Cloudflare R2 |
| Monitoring | Sentry |
| Logging | Loguru + structured JSON |
| Env Management | python-dotenv + .env.local |

---

# 8. Functional Requirements

---

## Module 1: Resume Intelligence

**Goal:** Parse the user's latest resume into a structured Professional Profile object.

### Input Sources (Priority Order)
1. Google Drive (auto-sync, latest PDF)
2. Direct PDF upload
3. GitHub profile scrape (README, pinned repos)
4. Manual form entry (fallback)

### Extraction Targets

```json
{
  "name": "Anirudh Sudheer",
  "email": "anirudhsudheer@gmail.com",
  "phone": "919539102881",
  "location": "Kozhikode, Kerala",
  "linkedin": "sudoanirudh",
  "github": "SudoAnirudh",
  "skills": {
    "languages": ["Python", "Kotlin", "TypeScript"],
    "frameworks": ["FastAPI", "Jetpack Compose", "LangChain"],
    "tools": ["Firebase", "Docker", "Git", "Gemini API"]
  },
  "projects": [
    {
      "name": "Nimma-Guru",
      "tech": ["Kotlin", "Jetpack Compose", "Firebase", "Gemini 2.0 Flash"],
      "description": "Community mentorship platform connecting retired professionals with students",
      "impact": "7 Gemini AI feature integrations"
    }
  ],
  "education": [...],
  "experience": [...],
  "certifications": [...]
}
```

### Resume Versioning
- Every re-sync creates a new version snapshot
- User can compare versions (v1 vs v2)
- Active version used for all matching

---

## Module 2: Skill Knowledge Base Builder

Transforms extracted resume into a searchable skill graph.

### Skill Normalization
- Aliases resolved: `"ML"` → `"Machine Learning"`, `"JS"` → `"JavaScript"`
- Skill levels inferred: mentions in multiple projects = higher weight
- Missing skills flagged: if JD requires X and profile lacks it → "Gap Alert"

### Knowledge Base Structure

```
Skills Graph:
  Python (strength: 0.92)
    └─ FastAPI (0.85)
    └─ LangChain (0.78)
    └─ scikit-learn (0.70)
  
  Android (strength: 0.80)
    └─ Kotlin (0.88)
    └─ Jetpack Compose (0.85)
    └─ Firebase (0.82)
```

---

## Module 3: Job Discovery Engine

**Goal:** Continuously discover relevant job postings from multiple sources.

### Data Sources

| Source | Method | Frequency |
|---|---|---|
| Wellfound (AngelList) | API / Scraper | Every 4 hours |
| YC Jobs | Scraper | Every 4 hours |
| Naukri | Scraper (Playwright) | Every 6 hours |
| Foundit | Scraper | Every 6 hours |
| Instahyre | Scraper | Every 8 hours |
| LinkedIn Jobs | Scraper (rate-limited) | Every 12 hours |
| Company Career Pages | Playwright | Daily |
| Google Jobs | Custom Search API | Every 4 hours |

### Search Queries (Auto-generated from Profile)
```
"AI Engineer" Bangalore Fresher
"ML Engineer" Remote India
"Software Engineer AI/ML" Remote
"Python Developer" + Gemini OR LangChain
"Android Developer" Kotlin Compose
```

### Deduplication Strategy
- Hash: `SHA256(company_name + job_title + location)`
- Fuzzy match on job description similarity > 90% → duplicate
- Same company + same role posted on 2 boards → deduplicated, sources merged

### Job Data Model

```json
{
  "id": "uuid",
  "title": "AI Engineer",
  "company": "Sarvam AI",
  "description": "...",
  "skills_required": ["Python", "LLMs", "FastAPI"],
  "location": "Bangalore / Remote",
  "salary_range": "₹8L–₹15L",
  "experience_required": "0–2 years",
  "posted_date": "2026-06-10",
  "source": "Wellfound",
  "source_url": "https://...",
  "match_score": 87.4,
  "status": "discovered"
}
```

---

## Module 4: Matching Engine

**Goal:** Score every job against the user's profile.

### Match Formula

```
Match Score (0–100) =
  40% × Skill Match Score
+ 25% × Project Relevance Score
+ 20% × Technology Stack Match
+ 10% × Role Title Similarity
+ 5%  × Education Match

Penalty:
  - If experience_required > user's YOE: -15 points
  - If location is onsite in unsupported city: -10 points
```

### Matching Pipeline
1. Embed job description using BGE-M3
2. Embed user profile using BGE-M3
3. Compute cosine similarity → base score
4. Run keyword skill extraction on JD → compare against profile skills
5. Apply weighted formula
6. Store score + explanation in DB

### Match Explanation (Per Job)

```
Match Score: 87/100

✅ Matched Skills: Python, FastAPI, LangChain, Gemini
⚠️  Partial Match: MLOps (you have exposure, not production)
❌  Missing: Kubernetes (not in your profile)

Project Alignment:
  SummarizeAgent → "AI Summarization" in JD (0.89 similarity)
  Nimma-Guru → "Multi-modal AI" in JD (0.72 similarity)

Role Match: "AI Engineer" vs your target "AI/ML Engineer" = 0.91
```

---

## Module 5: Company Research Agent

**Goal:** Automatically research every company before outreach.

### Research Areas
- Company overview (product, mission, stage)
- Team size and engineering org
- Recent news (last 30 days)
- Tech stack (from job postings, StackShare, GitHub)
- AI/ML initiatives
- Key investors and funding stage
- Employee LinkedIn profiles for contact discovery

### Output

```json
{
  "company": "Sarvam AI",
  "overview": "Indian AI startup building LLMs for Indic languages",
  "stage": "Series A",
  "team_size": "50–100",
  "tech_stack": ["Python", "PyTorch", "FastAPI", "Kubernetes"],
  "recent_news": ["Raised $41M Series A", "Launched Sarvam-2B LLM"],
  "ai_focus": "Indic LLMs, ASR, TTS",
  "why_fit": "Your NLP background and Gemini API experience directly align with their multilingual AI work"
}
```

---

## Module 6: Contact Discovery

**Goal:** Find the right person to contact at each company.

### Target Contacts (Priority Order)
1. Engineering Manager / Team Lead (highest referral conversion)
2. Recruiter / Talent Acquisition
3. Senior Engineer on target team
4. Alumni from your college at company (highest response rate)

### Contact Data Model

```json
{
  "id": "uuid",
  "job_id": "uuid",
  "name": "Priya Sharma",
  "title": "Engineering Manager – AI",
  "company": "Sarvam AI",
  "linkedin_url": "https://linkedin.com/in/...",
  "email": "priya@sarvam.ai (guessed)",
  "email_confidence": 0.82,
  "source": "LinkedIn",
  "connection_degree": 2,
  "shared_connections": ["Rajan Mathew", "Arjun KP"],
  "status": "pending_outreach"
}
```

### Email Guessing Logic
Common patterns tried:
- `first@company.com`
- `first.last@company.com`
- `flast@company.com`
- Validated via SMTP verify (no actual email sent)

---

## Module 7: Outreach Generator

**Goal:** Generate high-quality, personalized outreach messages.

### Message Types

#### 1. LinkedIn Referral Request
```
Hi [Name], I came across the [Role] opening at [Company] and noticed 
your work on [specific project/feature from their profile]. 

I'm a final-year AI/ML student with experience building [relevant project 
from resume matching their work] — I'd genuinely love to learn more about 
the team before applying.

Would you be open to a quick 15-minute chat? No pressure at all.
[My LinkedIn / GitHub]
```

#### 2. Cold Recruiter Email
```
Subject: AI Engineer Application – [Name], AI/ML @ SIT, 3 deployed projects

Hi [Recruiter Name],

I'm applying for the [Role] at [Company]. 

Quick snapshot:
• Final-year AI/ML student at Srinivas Institute of Technology
• Built Nimma-Guru (7 Gemini AI integrations, Kotlin/Compose/Firebase)
• Built SummarizeAgent (deployed on Google Cloud Run, ADK + Gemini 2.0)
• Python, FastAPI, LangChain, Android stack

My application: [JD link]
Portfolio: github.com/SudoAnirudh

Happy to share more. Is this role still open?

Anirudh
```

#### 3. Follow-Up (7 days after no reply)
```
Hi [Name], just a gentle follow-up on my message from [Date]. 

I recently [shipped X / added Y to my GitHub] and thought it might be 
relevant to the [Role] role at [Company]. 

Still interested if there's a fit!
```

### Personalization Inputs
- User's resume (projects, skills)
- Company research summary
- Target contact's LinkedIn activity
- Job description
- Match explanation

### Message Quality Controls
- Tone: Professional but human
- Length: LinkedIn < 150 words, Email < 200 words
- No generic openers ("Hope this finds you well")
- Specific detail about their company required (not optional)

---

## Module 8: Application Tracker

**Goal:** Track every job through the full pipeline.

### Pipeline Stages

```
Discovered → Saved → Applied → Referral Requested → 
Interview Scheduled → Interview Done → Offer → Rejected / Withdrawn
```

### Stage Metadata

| Stage | Data Captured |
|---|---|
| Applied | Applied date, resume version, platform |
| Referral Requested | Contact name, message sent, sent date |
| Interview | Round number, date, interviewer, prep notes |
| Offer | CTC, joining date, negotiation notes |
| Rejected | Rejection reason (if known), follow-up option |

### Smart Reminders
- "You applied to X 7 days ago — still no reply. Send follow-up?"
- "Interview with Y is in 2 days. Prep checklist ready."
- "3 applications stuck in Applied for 14+ days. Consider reaching out."

---

## Module 9: Analytics Dashboard

### Cards (Top Row)
- Total Applications
- Active Applications (not rejected/withdrawn)
- Response Rate (replied / total outreach)
- Interview Rate (interviews / applications)

### Charts
- Application funnel (Sankey / bar chart)
- Match score distribution (histogram)
- Applications over time (line chart)
- Top companies applied to
- Skill gap heatmap (required vs. possessed)

### Weekly Summary (Auto-generated)
```
Week of June 9–15, 2026:

Jobs Discovered: 47
High Match (>80%): 12
Applied: 6
Referrals Requested: 4
Replies Received: 2 (50% reply rate this week 🔥)

Top Performing Sources: Wellfound (18 jobs), YC Jobs (9 jobs)
Skill Gap Alert: Kubernetes appearing in 8 of your target JDs
```

---

# 9. AI Agent Architecture

## Agent 1: Resume Agent

```
Trigger: New PDF uploaded / Google Drive sync
Input: Raw PDF bytes
Steps:
  1. Extract text (PyMuPDF)
  2. Run NER pipeline (spaCy)
  3. Structure into ProfileObject (Pydantic)
  4. Generate BGE-M3 embedding
  5. Store in ChromaDB + PostgreSQL
  6. Notify: "Profile updated. 3 new skills detected."
Output: ProfileObject + embedding
```

## Agent 2: Job Discovery Agent

```
Trigger: APScheduler (every 4 hours)
Input: User profile, target roles, locations
Steps:
  1. Build search queries from profile
  2. Scrape each source (Playwright / requests)
  3. Parse job listings into JobObject
  4. Deduplicate via hash + fuzzy match
  5. Embed job descriptions (BGE-M3)
  6. Store new jobs, skip duplicates
  7. Trigger Matching Agent for new jobs
Output: List[JobObject], count_new, count_duplicate
```

## Agent 3: Matching Agent

```
Trigger: New job discovered OR profile updated
Input: JobObject + ProfileObject
Steps:
  1. Semantic similarity (cosine on embeddings)
  2. Skill keyword extraction + overlap
  3. Project relevance scoring (FAISS nearest neighbor)
  4. Weighted formula → match_score
  5. Generate human-readable match explanation
  6. Update job record with score + explanation
Output: MatchResult { score, explanation, gaps[] }
```

## Agent 4: Company Research Agent

```
Trigger: Job saved / match score > 70
Input: Company name + domain
Steps:
  1. Web search (Google Custom Search API)
  2. Scrape company website (About, Blog, Team pages)
  3. Search LinkedIn for company info
  4. Search Crunchbase for funding info
  5. Summarize using LLM
  6. Store CompanyProfile
Output: CompanyProfile { overview, stack, news, why_fit }
```

## Agent 5: Contact Research Agent

```
Trigger: Job saved by user
Input: Company name, target role
Steps:
  1. Search LinkedIn for relevant people
  2. Filter by seniority (Manager, Lead, Recruiter)
  3. Scrape public profile info
  4. Guess email using pattern + SMTP verify
  5. Store ContactObject
Output: List[ContactObject]
```

## Agent 6: Outreach Agent

```
Trigger: User clicks "Generate Message" for a contact
Input: ProfileObject + CompanyProfile + ContactObject + JobObject
Steps:
  1. Select message type (referral / recruiter / follow-up)
  2. Build personalization context
  3. LLM prompt → draft message
  4. Quality checks (length, no banned phrases, has specific detail)
  5. If quality fail → regenerate (max 3 retries)
Output: MessageObject { type, draft, tokens_used }
```

## Agent 7: Analytics Agent

```
Trigger: Weekly cron (Sunday 8 PM)
Input: All applications, messages, match scores
Steps:
  1. Compute funnel metrics
  2. Identify skill gaps from rejected JDs
  3. Identify best-performing sources
  4. Generate weekly summary text
  5. Push notification to user
Output: WeeklySummary { metrics, gaps, highlights }
```

---

# 10. Database Schema

## users
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_id VARCHAR UNIQUE NOT NULL,
  name VARCHAR NOT NULL,
  email VARCHAR UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## profiles
```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  version INT DEFAULT 1,
  raw_text TEXT,
  skills JSONB,
  projects JSONB,
  education JSONB,
  experience JSONB,
  certifications JSONB,
  resume_url VARCHAR,
  embedding_id VARCHAR,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_profiles_active ON profiles(user_id, is_active);
```

## jobs
```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR NOT NULL,
  company VARCHAR NOT NULL,
  description TEXT,
  skills_required JSONB,
  location VARCHAR,
  remote BOOLEAN,
  salary_min INT,
  salary_max INT,
  experience_years_min INT,
  experience_years_max INT,
  source VARCHAR,
  source_url VARCHAR,
  source_hash VARCHAR UNIQUE,
  match_score FLOAT,
  match_explanation JSONB,
  status VARCHAR DEFAULT 'discovered',
  posted_date DATE,
  discovered_at TIMESTAMP DEFAULT NOW(),
  embedding_id VARCHAR
);
CREATE INDEX idx_jobs_match_score ON jobs(match_score DESC);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_company ON jobs(company);
```

## companies
```sql
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR UNIQUE NOT NULL,
  domain VARCHAR,
  overview TEXT,
  tech_stack JSONB,
  funding_stage VARCHAR,
  team_size VARCHAR,
  recent_news JSONB,
  ai_focus TEXT,
  why_fit TEXT,
  last_researched_at TIMESTAMP
);
```

## contacts
```sql
CREATE TABLE contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
  name VARCHAR,
  title VARCHAR,
  company VARCHAR,
  linkedin_url VARCHAR,
  email VARCHAR,
  email_confidence FLOAT,
  connection_degree INT,
  source VARCHAR,
  status VARCHAR DEFAULT 'discovered',
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_contacts_job_id ON contacts(job_id);
CREATE INDEX idx_contacts_status ON contacts(status);
```

## messages
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
  job_id UUID REFERENCES jobs(id),
  type VARCHAR NOT NULL,
  draft TEXT NOT NULL,
  final_text TEXT,
  sent_at TIMESTAMP,
  replied_at TIMESTAMP,
  status VARCHAR DEFAULT 'draft',
  created_at TIMESTAMP DEFAULT NOW()
);
```

## applications
```sql
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  job_id UUID REFERENCES jobs(id),
  profile_version INT,
  status VARCHAR DEFAULT 'saved',
  applied_date DATE,
  platform VARCHAR,
  interview_rounds JSONB,
  offer_details JSONB,
  notes TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
```

---

# 11. API Design

## Resume
```
POST   /api/v1/resume/upload          # Upload PDF
POST   /api/v1/resume/sync/drive      # Sync from Google Drive
GET    /api/v1/resume/profile         # Get active profile
GET    /api/v1/resume/versions        # List all versions
PATCH  /api/v1/resume/versions/{id}/activate  # Set active version
```

## Jobs
```
GET    /api/v1/jobs                   # List jobs (filter by status, score, company)
GET    /api/v1/jobs/{id}              # Job detail + match explanation
POST   /api/v1/jobs/{id}/save         # Save job
POST   /api/v1/jobs/discover          # Trigger manual discovery
GET    /api/v1/jobs/{id}/contacts     # Get discovered contacts for job
```

## Outreach
```
POST   /api/v1/outreach/generate      # Generate message for contact
GET    /api/v1/outreach/messages      # List all messages
PATCH  /api/v1/outreach/messages/{id} # Update draft
POST   /api/v1/outreach/messages/{id}/send  # Send via Gmail API
```

## Applications
```
GET    /api/v1/applications           # List all applications
POST   /api/v1/applications           # Create application
PATCH  /api/v1/applications/{id}      # Update status / add notes
DELETE /api/v1/applications/{id}      # Withdraw
```

## Analytics
```
GET    /api/v1/analytics/summary      # Full metrics
GET    /api/v1/analytics/funnel       # Pipeline funnel data
GET    /api/v1/analytics/skill-gaps   # Frequently required missing skills
GET    /api/v1/analytics/weekly       # Latest weekly report
```

## WebSocket
```
WS     /ws/jobs                       # Real-time new job notifications
WS     /ws/tasks                      # Background task progress updates
```

---

# 12. UI Pages

## 12.1 Dashboard
**URL:** `/`

- **Top Cards:** Jobs Found Today | High Match (>80%) | Pending Outreach | Active Applications
- **Activity Feed:** Recent discoveries, status changes, reminders
- **Match Score Distribution Chart:** Histogram of all job scores
- **Quick Actions:** Sync Resume | Run Discovery | Open Tracker

## 12.2 Opportunities
**URL:** `/opportunities`

- **Filters:** Score ≥ N | Remote | Location | Date Range | Source
- **Table Columns:** Company | Role | Match Score (badge, color-coded) | Location | Status | Actions
- **Actions Per Row:** Save | View Details | Find Contacts | Generate Message
- **Sort:** By match score (default), date posted, company name

## 12.3 Job Details
**URL:** `/opportunities/{id}`

- **Left Panel:** Job description (raw + cleaned)
- **Right Panel:**
  - Match Score ring chart
  - Matched Skills (green ✅) / Missing Skills (red ❌)
  - Company Research Summary
  - Discovered Contacts
  - Generated Messages (if any)
  - "Apply" button + status update

## 12.4 Outreach Center
**URL:** `/outreach`

- **Message Queue:** All generated drafts
- **Status Filter:** Draft | Sent | Replied | Follow-Up Due
- **Per Message:** Contact name | Company | Message type | Preview | Edit | Copy | Mark Sent
- **Quick Compose:** Select job → select contact → generate → edit → send

## 12.5 Application Tracker
**URL:** `/tracker`

- **Kanban Board View:** Cards per stage, drag-and-drop
- **List View:** Sortable table
- **Per Card:** Company | Role | Applied Date | Match Score | Days Since Applied
- **Smart Reminders Banner:** "5 applications need follow-up"

## 12.6 Analytics
**URL:** `/analytics`

- **Funnel Chart:** Discovered → Saved → Applied → Interview → Offer
- **Timeline:** Applications over last 30/60/90 days
- **Source Performance:** Which boards give best match scores
- **Skill Gap Table:** Missing skills ranked by frequency in target JDs
- **Weekly Report Card:** Auto-generated summary

## 12.7 Settings
**URL:** `/settings`

- **Profile:** Edit personal info, target roles, locations, experience level
- **Integrations:** Connect Google Drive, Gmail, LinkedIn
- **Discovery Preferences:** Job boards to use, search keywords, remote/hybrid/onsite
- **Notification Preferences:** Email digest frequency, in-app alerts
- **Resume Versions:** View, compare, activate

---

# 13. LLM Prompt Engineering

## Match Explanation Prompt

```python
MATCH_EXPLANATION_PROMPT = """
You are a career advisor analyzing job fit.

User Profile:
{profile_json}

Job Description:
{jd_text}

Skill Match Analysis:
{skill_overlap}

Return a JSON object:
{
  "score": <0-100>,
  "matched_skills": [...],
  "missing_skills": [...],
  "project_alignments": [{"project": "...", "jd_element": "...", "similarity": 0.XX}],
  "role_similarity": 0.XX,
  "summary": "2-3 sentence plain English fit summary",
  "recommendation": "apply" | "apply_with_note" | "skip"
}

Respond only with the JSON. No markdown.
"""
```

## Outreach Generation Prompt

```python
REFERRAL_REQUEST_PROMPT = """
You are a career coach writing a LinkedIn referral request on behalf of {user_name}.

User Background:
{profile_summary}

Target Contact:
- Name: {contact_name}
- Title: {contact_title}
- Company: {company_name}
- Notable work: {contact_notable_work}

Job Role: {job_title}

Company Context:
{company_summary}

Rules:
- Max 150 words
- No generic openers ("Hope this finds you well")
- Reference one specific thing about the contact's company or work
- Mention one relevant project from the user's background
- End with a clear, low-pressure ask
- Do not use the word "leverage"
- Sound human, not AI-generated

Return only the message text. No subject line. No "Hi" header.
"""
```

---

# 14. Error Handling

| Error Type | Handling |
|---|---|
| Scraper blocked (403/429) | Rotate user-agent, exponential backoff, skip source for session |
| LLM timeout | Retry once, fallback to secondary model (Gemini) |
| Google Drive auth expired | Re-auth prompt in UI |
| Duplicate job detected | Silent skip, increment duplicate counter in logs |
| Email SMTP verify fails | Store email as "unverified", still show to user with warning |
| ChromaDB embedding error | Queue for retry, don't block pipeline |
| Match score computation fails | Set score to null, flag for manual review |

---

# 15. Security

| Area | Implementation |
|---|---|
| Authentication | Clerk (OAuth + JWT) |
| API Authorization | JWT middleware on all /api/v1/* routes |
| Secrets | Environment variables (never in code) |
| Data Encryption at Rest | AES-256 (Supabase default) |
| HTTPS | Enforced on Vercel + Railway |
| Rate Limiting | SlowAPI (FastAPI) — 100 req/min per user |
| Resume Storage | Cloudflare R2 with signed URLs (1-hour expiry) |
| CORS | Restricted to frontend domain only |
| LinkedIn Scraping | Respect robots.txt, throttle to ~1 req/3s |

---

# 16. Notifications

### In-App (WebSocket push)
- New high-match job discovered (score > 80)
- Outreach message generated
- Weekly analytics summary ready

### Email Digest (Optional, daily/weekly)
- New matches above threshold
- Follow-up reminders
- Weekly report

### Browser Push (PWA)
- New job > 85% match
- Interview reminder 24h before

---

# 17. MVP Roadmap

## Week 1 — Foundation
- [ ] Project scaffold (Next.js + FastAPI + Supabase)
- [ ] Clerk auth integration
- [ ] Resume upload + PDF parser
- [ ] Google Drive sync
- [ ] Profile object builder + ChromaDB embedding
- [ ] Basic dashboard shell

## Week 2 — Discovery + Matching
- [ ] Job scraper (Wellfound + YC Jobs first)
- [ ] Deduplication pipeline
- [ ] BGE-M3 embedding for jobs
- [ ] Weighted match scoring
- [ ] Match explanation generator
- [ ] Opportunities page with filters

## Week 3 — Outreach + Tracking
- [ ] Company research agent
- [ ] Contact discovery (manual input + LinkedIn search)
- [ ] Outreach message generator (referral + recruiter types)
- [ ] Application tracker (Kanban)
- [ ] Message copy/edit/send flow

## Week 4 — Polish + Deploy
- [ ] Analytics dashboard (funnel + charts)
- [ ] Skill gap analysis
- [ ] Weekly summary email
- [ ] PWA manifest + service worker
- [ ] Deploy to Vercel + Railway
- [ ] Sentry error monitoring setup

---

# 18. Post-MVP Enhancements

| Feature | Priority | Notes |
|---|---|---|
| AI Resume Optimizer | High | Tailored per JD, suggests edits |
| Interview Prep Agent | High | Company-specific Q&A practice |
| Cover Letter Generator | Medium | Personalized, 1-click |
| Salary Prediction | Medium | Based on role, company, location |
| LinkedIn Auto-DM | Low | Semi-automated, user confirms |
| Multi-user Support | Low | Share tracker with mentor/coach |
| Voice Career Assistant | Low | "What should I apply to today?" |
| Chrome Extension | Medium | 1-click save from any job board |
| Company Intelligence Reports | High | PDF report per company |
| Cold Email Sequencer | Medium | Auto follow-up after N days |

---

# 19. Local Dev Setup

```bash
# Clone
git clone https://github.com/SudoAnirudh/ai-career-copilot
cd ai-career-copilot

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in: SUPABASE_URL, SUPABASE_KEY, NVIDIA_API_KEY, GOOGLE_CLIENT_ID, etc.
uvicorn app.main:app --reload

# Celery (separate terminal)
celery -A app.worker worker --loglevel=info

# Frontend
cd frontend
npm install
cp .env.local.example .env.local
npm run dev

# ChromaDB (runs in-process by default, or run standalone)
# Redis (for Celery)
redis-server
```

---

# 20. Environment Variables

```env
# Backend
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379
CHROMA_PERSIST_DIR=./chroma_db
R2_BUCKET_URL=...
R2_ACCESS_KEY=...
R2_SECRET_KEY=...

# AI
NVIDIA_API_KEY=...
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
GEMINI_API_KEY=...

# Google
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_CUSTOM_SEARCH_API_KEY=...

# Clerk (Backend)
CLERK_SECRET_KEY=...

# Frontend
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=...
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

# Final Product Outcome

**AI Career Copilot** is a production-grade, agentic job search system that:

- **Discovers** 30+ relevant jobs per day across 8+ boards
- **Scores** every job with a transparent 0–100 match score + explanation
- **Researches** each company automatically before you apply
- **Finds** the right people to contact at each company
- **Writes** personalized, human-quality outreach messages in seconds
- **Tracks** every application through a full pipeline with smart reminders
- **Analyzes** your job search performance weekly and flags skill gaps

Turning a 3-hour/day job search into a 5-minute daily review.
