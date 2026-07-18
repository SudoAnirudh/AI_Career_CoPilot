# 🤖 AI Career CoPilot

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js%2014-000000?style=flat-square&logo=next.js)](https://nextjs.org/)
[![Gemini](https://img.shields.io/badge/Gemini%20AI-4285F4?style=flat-square&logo=googlegemini)](https://ai.google.dev/)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA%20NIM-76B900?style=flat-square&logo=nvidia)](https://www.nvidia.com/en-us/ai/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)

**AI Career CoPilot** is an intelligent, agentic job search assistant that automates the tedious parts of looking for a job. It acts as a personal AI career team—continuously discovering opportunities, parsing and analyzing your resume, scoring job matches, finding referral contacts, generating highly personalized outreach drafts, and tracking applications through a visual Kanban pipeline.

---

## 🛠️ System Architecture

AI Career CoPilot utilizes a multi-agent system built on **FastAPI** and **Next.js**, coordinated by **Celery** background tasks with **Redis** as a message broker. It uses a hybrid database approach: relational models in **PostgreSQL** and vector representations in **ChromaDB** for semantic search and matching.

```mermaid
graph TD
    subgraph Frontend [Next.js PWA Client]
        Client[React UI]
        Zustand[Zustand State]
        TQ[TanStack Query]
    end

    subgraph Backend [FastAPI API Layer]
        API[FastAPI Server]
        WS[WebSocket Manager]
    end

    subgraph Workers [Background Queue]
        Celery[Celery Workers]
        Sched[APScheduler Cron]
    end

    subgraph DBs [Storage Layer]
        PG[(PostgreSQL / Supabase)]
        Chroma[(ChromaDB Vector Store)]
        Redis[(Redis Cache & Broker)]
    end

    subgraph AI [AI & LLM Services]
        Gemini[Gemini 2.0 Flash]
        NVIDIA[NVIDIA NIM / Llama 3]
        Embed[BGE-M3 Embeddings]
    end

    Client <-->|REST / WS| API
    API <--> PG
    API <--> Redis
    API -->|Enqueue Tasks| Celery
    Sched -->|Trigger Scrapes| Celery
    Celery <--> PG
    Celery <--> Chroma
    Celery <--> Redis
    Celery <--> AI
    API <--> Chroma
```

---

## ✨ Core Features

*   **📄 Resume Intelligence & NER**: Parses PDF resumes to extract structured professional profiles (skills, projects, education, experience) using LLMs and structured Pydantic models.
*   **🔍 Continuous Job Discovery**: Scraping agents periodically query job sources (Wellfound, YC Jobs, Naukri, LinkedIn) using dynamic search queries auto-tuned to your profile.
*   **🎯 Semantic Matching Engine**: Computes high-dimensional cosine similarity between resume and job description embeddings, combined with keyword overlaps and project relevance metrics.
*   **🏢 Automated Company Research**: Background agents run real-time web searches to research company funding, tech stack, and key initiatives before outreach.
*   **👥 Contact Discovery & Email Guessing**: Identifies engineering managers, recruiters, and alumni on LinkedIn and runs SMTP-verify logic to discover contact emails.
*   **✉️ Hyper-Personalized Outreach**: Generates context-aware, short outreach messages (LinkedIn requests, recruiter cold emails, follow-ups) using Nvidia NIMs/Gemini.
*   **📋 Kanban Application Tracker**: Visually manage your applications from *Discovered* to *Saved*, *Applied*, *Interviewing*, and *Offers*.
*   **📊 Rich Analytics Dashboard**: Monitors response rates, funnel metrics, and details skill gaps extracted from target job descriptions.

---

## 🚀 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14 (App Router), TypeScript, TailwindCSS, shadcn/ui, Recharts, Zustand, TanStack Query, Clerk |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy 2.0, Pydantic v2, Celery, APScheduler, Playwright, BeautifulSoup4 |
| **AI/ML Layer** | NVIDIA NIM (Llama 3.1 70B), Gemini 2.0 Flash, BGE-M3 (Sentence Transformers), ChromaDB, FAISS |
| **Databases** | PostgreSQL (Supabase / Local PG), Redis (Broker & Cache) |
| **Infrastructure** | Vercel (Frontend), Render/Railway (Backend & Workers), Docker Compose |

---

## 📂 Project Structure

```
AI_Career_CoPilot/
├── backend/                    # FastAPI Backend Application
│   ├── app/
│   │   ├── api/                # API Routers & Endpoint Handlers
│   │   │   └── routes.py       # Core endpoint routing
│   │   ├── services/           # Agentic Business Logic Services
│   │   │   ├── analytics_service.py
│   │   │   ├── company_research_service.py
│   │   │   ├── contact_discovery_service.py
│   │   │   ├── job_discovery_service.py
│   │   │   ├── llm.py          # LLM Provider interfaces (Gemini / NVIDIA)
│   │   │   ├── matching_service.py
│   │   │   ├── outreach_service.py
│   │   │   ├── resume_service.py
│   │   │   └── websocket_manager.py
│   │   ├── config.py           # Settings and env validation
│   │   ├── database.py         # DB connection & session creation
│   │   ├── models.py           # SQL Alchemy database models
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── tasks.py            # Celery background tasks
│   │   └── worker.py           # Celery application initialization
│   ├── Dockerfile              # Backend container build script
│   ├── requirements.txt        # Python dependencies
│   └── test_scraping.py        # Scraping and search utilities test script
│
├── frontend/                   # Next.js Frontend Application
│   ├── public/                 # Static assets
│   ├── src/
│   │   ├── app/                # Next.js App Router Page layouts
│   │   │   ├── analytics/      # Performance metrics and dashboard charts
│   │   │   ├── jobs/           # Discovered/matched jobs search list
│   │   │   ├── kanban/         # Job applications pipeline board
│   │   │   ├── outreach/       # Outreach contacts and generated drafts
│   │   │   ├── settings/       # Profile management and API configurations
│   │   │   ├── globals.css     # Global styles & tailwind components
│   │   │   ├── layout.tsx      # Main layout shell
│   │   │   └── page.tsx        # Homepage dashboard landing page
│   │   ├── components/         # Shared UI components (shadcn/ui)
│   │   ├── context/            # Auth & context providers
│   │   └── firebase.ts         # Firebase configuration
│   ├── Dockerfile              # Frontend container build script
│   └── package.json            # Node.js dependencies
│
├── docker-compose.yml          # Local database & redis services config
├── docker-compose.prod.yml     # Complete Production/Staging stack orchestrator
└── render.yaml                 # Render Blueprint configuration
```

---

## 💻 Local Development Setup

### Prerequisites

*   Python 3.11+
*   Node.js 18+ & npm
*   Docker & Docker Compose

### 📦 1. Start Relational DB & Redis Cache

The simplest way to run PostgreSQL and Redis locally is using Docker Compose. Run this command in the project root:

```bash
docker compose up -d
```

This starts PostgreSQL on port `5439` and Redis on port `6389` (to avoid ports conflicts with system services).

### 🐍 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Install Playwright browser engines (required for job board scraping):
   ```bash
   playwright install chromium
   ```
5. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
6. Open `.env` and fill in the required keys:
   * `DATABASE_URL=postgresql://postgres:password@localhost:5439/career_copilot`
   * `REDIS_URL=redis://localhost:6389/0`
   * `GEMINI_API_KEY=your_google_gemini_api_key`
   * `NVIDIA_API_KEY=your_nvidia_key`
   * `DEV_AUTH_BYPASS=true` (Allows bypassing authentication setup in local development)
7. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
8. Start the Celery background worker (in a separate terminal window, with active venv):
   ```bash
   celery -A app.worker.celery_app worker --loglevel=info
   ```

### 🎨 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install package dependencies:
   ```bash
   npm install
   ```
3. Create a `.env.local` or `.env` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
   # Add Clerk / Firebase authentication keys if DEV_AUTH_BYPASS is set to false
   ```
4. Start the frontend development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

## 🤖 AI Agents Workflow Reference

1.  **Resume Agent**: Converts uploaded resume PDFs using `PyMuPDF` and LLM parsing to create a structured JSON Profile. This gets indexed in `ChromaDB` as a semantic vector.
2.  **Job Discovery Agent**: Regularly runs background scrapes of target job websites, deduplicates opportunities by computing description similarities, and hashes titles/companies.
3.  **Matching Agent**: Computes the matching score based on skill match (40%), project alignment (25%), tech stack overlap (20%), role title similarity (10%), and education criteria (5%).
4.  **Company Research Agent**: Scrapes public website information and funding statuses to output fit reports detailing why the applicant is a match.
5.  **Contact Research Agent**: Discovers targeted team members and attempts email verification using SMTP verify sockets.
6.  **Outreach Agent**: Generates drafts of professional referral request messages and recruiter cold emails tailored to the research.
7.  **Analytics Agent**: Generates weekly analytics digests outlining funnel performance and identifying critical skill gaps (e.g. "Kubernetes is requested in 45% of saved JDs").

---

## 📖 Detailed Documentation Index

For in-depth explanations of specific areas of the codebase, refer to the documents in the `docs/` folder:

*   **[System Architecture](docs/architecture.md)**: Detailed multi-tier layouts, sequence diagrams, and client-server communication channels.
*   **[Data & AI Models](docs/models_and_database.md)**: Relational Postgres tables, validation schemas (Pydantic v2), and configurations for NVIDIA NIM and Gemini models.
*   **[Workflows & Agent Systems](docs/workflows_and_agents.md)**: In-depth workflow diagrams for all 7 agents, background tasks configuration, and the mathematical matching formula equations.
*   **[Tech Stack & Configurations](docs/tech_stack.md)**: Complete mapping of frontend (Next.js 16) and backend (FastAPI) dependencies.

---

## ☁️ Deployment

For detailed configurations on how to deploy this stack to production using Docker Compose, Render Blueprints, or hybrid Vercel/Supabase/Railway configurations, consult the [Deployment Guide](DEPLOYMENT.md).
