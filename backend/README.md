# 🐍 AI Career CoPilot - Backend Engine

The backend layer is an asynchronous service built using **FastAPI**, **SQLAlchemy 2.0**, and **Celery**. It handles all the data orchestration, agent execution pipelines, PDF parsing, web scrapers, and matching logic.

---

## 📂 Backend Directory Structure

```
backend/
├── app/
│   ├── api/            # API Route endpoints & HTTP controllers
│   │   └── routes.py   # Main router mappings
│   ├── services/       # Autonomous Agent logic & third-party integrations
│   │   ├── analytics_service.py
│   │   ├── company_research_service.py
│   │   ├── contact_discovery_service.py
│   │   ├── job_discovery_service.py
│   │   ├── llm.py      # NVIDIA & Gemini LLM interfaces
│   │   ├── matching_service.py
│   │   ├── outreach_service.py
│   │   ├── resume_service.py
│   │   └── websocket_manager.py
│   ├── config.py       # Configuration and environmental validation
│   ├── database.py     # Database engine & Session initializers
│   ├── models.py       # SQLAlchemy declarative ORM models
│   ├── schemas.py      # Pydantic v2 data models & serialization schemas
│   ├── tasks.py        # Asynchronous Celery tasks definition
│   └── worker.py       # Celery application setup
├── Dockerfile          # Multi-stage production container definition
├── requirements.txt    # Python package dependencies manifest
└── test_scraping.py    # Sandbox scraping test utility script
```

---

## ⚡ Key Services & Architecture

1.  **FastAPI REST Layer**: Standardized HTTP API routing under the `/api/v1` namespace.
2.  **WebSocket Manager (`app/services/websocket_manager.py`)**: Establishes continuous active connection pools (`/ws/jobs`, `/ws/tasks`) to push background scraping and matching updates straight to the client in real-time.
3.  **ORM Layer (`app/models.py`)**: Maps Python classes directly to PostgreSQL tables.
4.  **Celery Queue (`app/tasks.py`)**: Offloads CPU-intensive and slow parsing/crawling tasks (such as Playwright job scraping and NVIDIA Llama NIM API calls) to separate background worker threads.

---

## 💻 Local Setup & Run Commands

### 1. Requirements & Dev Setup
Make sure you have created your virtual environment and installed all packages:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Database Migrations
On startup, FastAPI automatically runs database schema updates:
```python
Base.metadata.create_all(bind=engine)
```

### 3. Start Application Servers

*   **REST Server**:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
*   **Celery Worker**:
    ```bash
    celery -A app.worker.celery_app worker --loglevel=info
    ```
