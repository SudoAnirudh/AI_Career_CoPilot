# 🛠️ Tech Stack & Framework Configuration

This document provides details on the frameworks, libraries, and runtime dependencies chosen for **AI Career CoPilot**.

---

## 🎨 Frontend Stack (Next.js 16 Client)

Located in the `frontend/` directory.

### Core Libraries
*   **Next.js 16 (App Router)**: Serves as the React framework, leveraging Server Components and App Router layouts for high-performance rendering.
*   **React 19 & React DOM 19**: Powered by React's latest release, offering improved hook lifecycles and modern rendering performance.
*   **Recharts (`^3.8.1`)**: Used to construct the analytics funnel dashboards, match score histograms, and job discovery timelines.
*   **Firebase SDK (`^12.14.0`)**: Integrates real-time databases and user auth state providers.
*   **Lucide React (`^1.18.0`)**: Standard icon library used across the navigation sidebar and Kanban dashboard columns.
*   **Canvas Confetti (`^1.9.4`)**: Triggers micro-animations (e.g., when moving an application to the "Offered" state in the Kanban board).

### Development Tooling
*   **TypeScript (`^5.0.0`)**: Enforces strict type safety and auto-completion for components and endpoint payloads.
*   **ESLint (`^9.0.0`)**: Validates code quality and formatting rules during Next.js builds.

---

## 🐍 Backend Stack (FastAPI API Layer)

Located in the `backend/` directory.

### Core Frameworks
*   **FastAPI (`>=0.100.0`)**: Serves high-performance async REST and WebSocket endpoints.
*   **Uvicorn (`>=0.22.0`)**: The ASGI server running the FastAPI application.
*   **Pydantic (`>=2.0.0`) & Pydantic-Settings**: Handles request/response data validation and parses settings from environmental files.

### Database & ORM
*   **SQLAlchemy (`>=2.0.0`)**: Orchestrates object-relational mapping using type-safe SQL definitions.
*   **Psycopg2-Binary (`>=2.9.6`)**: PostgreSQL adapter facilitating connections to production databases like Supabase.
*   **ChromaDB**: Embeddings database facilitating cosine similarity lookups.

### Agentic & Parsing Tools
*   **Celery (`>=5.3.1`)**: A distributed task queue running long scrapes and AI calculations asynchronously.
*   **PyMuPDF (`>=1.22.5`)**: Parses and extracts text content from uploaded resume PDFs.
*   **Playwright (`>=1.35.0`) & BeautifulSoup4**: Automated browser scraper engine that navigates job boards and extracts JDs.
*   **Google Generative AI (`>=0.3.0`)**: Connects to the Gemini Flash 2.0 API for lightweight summaries and fallbacks.
*   **Websockets (`>=11.0.3`)**: Implements low-latency WebSocket connection handlers.

---

## ☁️ Infrastructure & Deployments

### 🐳 Production Container Stack
The production cluster is orchestrated using `docker-compose.prod.yml`, splitting services into distinct containers:
1.  **`db`**: PostgreSQL 15 container for relational datasets.
2.  **`redis`**: Redis 7 container working as the broker for background Celery tasks.
3.  **`backend`**: Custom Python 3.11 container running FastAPI.
4.  **`celery_worker`**: Copy of the backend container starting Celery task workers.
5.  **`frontend`**: Next.js Node container serving the compiled React build on port 3000.

### 🌐 Cloud Deployment Mappings
*   **FastAPI & Celery**: Deployed on Railway or Render using Docker builds to ensure browser dependencies (Playwright) are provisioned.
*   **Databases**: Supabase / Neon (relational PostgreSQL) and Upstash (Serverless Redis cache).
*   **Client**: Deployed on Vercel with serverless edge functions.
