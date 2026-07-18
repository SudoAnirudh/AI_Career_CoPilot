# Deployment Guide: AI Career CoPilot

This document outlines how to deploy the **AI Career CoPilot** (Next.js frontend, FastAPI backend, Celery task queue, Postgres DB, Redis, and ChromaDB vector database).

---

## 🛠️ Architecture Overview

The system consists of five primary components:
1. **Frontend**: Next.js (React) application.
2. **Backend**: FastAPI web server serving REST endpoints and WebSocket connections (`/ws/jobs`, `/ws/tasks`).
3. **Task Queue**: Celery worker executing background scrapes, ATS matches, and outreach tasks.
4. **Broker & Cache**: Redis (coordinates Celery tasks).
5. **Databases**:
   - **PostgreSQL**: Stores relational models (Profiles, Jobs, Contacts, Outreach Logs).
   - **ChromaDB**: Persists vector representations of resumes and jobs for matching.

---

## 🚀 Deployment Options

Choose the deployment strategy that best fits your goals:

### Option 1: Docker Compose (VPS / Self-Hosted) — *Recommended for full control*
This runs all services together inside Docker containers. Ideal for DigitalOcean Droplets, AWS EC2 instances, Linode, or local testing.

### Option 2: Render Blueprint (Managed Cloud) — *Recommended for zero DevOps*
Render provides managed Postgres and Redis instances alongside native support for Web Services (FastAPI, Next.js) and Background Workers (Celery).

### Option 3: Manual Deployment — *Recommended for separate hosting platforms*
e.g., Frontend on **Vercel**, Backend & Worker on **Render/Railway**, Database on **Supabase/Neon**, Redis on **Upstash**.

---

## 🐳 Option 1: Docker Compose (VPS Setup)

A production-ready `docker-compose.prod.yml` and corresponding `Dockerfile`s have been generated in the project root.

### Step 1: Clone and Set Up Environment Variables
Create a `.env.prod` file in your root directory containing:

```env
# Database & Redis Settings
DATABASE_URL=postgresql://postgres:password_prod@db:5432/career_copilot
REDIS_URL=redis://redis:6379/0
CHROMA_PERSIST_DIR=/app/chroma_db

# APIs
NVIDIA_API_KEY=your_nvidia_key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
GEMINI_API_KEY=your_gemini_key
CLERK_SECRET_KEY=your_clerk_secret_key

# Dev Settings
DEV_AUTH_BYPASS=false
PORT=8000
HOST=0.0.0.0

# Frontend Environment Variables (Build-time)
NEXT_PUBLIC_API_URL=https://yourdomain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://yourdomain.com/ws
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-app.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-app.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### Step 2: Build and Run
On your VPS, execute the following command to pull, build, and start all containers in detached mode:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```

### Step 3: Verify Running Services
```bash
docker compose -f docker-compose.prod.yml ps
```
Your backend will be accessible at `http://localhost:8000` and frontend at `http://localhost:3000`.

---

## ☁️ Option 2: Render Blueprint (Managed Cloud)

We have created a `render.yaml` file in your workspace that specifies all settings required to set up the architecture with one click.

### Step 1: Push Code to GitHub/GitLab
Make sure your project repository is pushed to a private or public git server.

### Step 2: Deploy Blueprint on Render
1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New** -> **Blueprint**.
3. Connect your GitHub/GitLab repository.
4. Render will read the `render.yaml` file automatically and outline the infrastructure to provision (FastAPI backend, Celery worker, Frontend, Postgres Database, and Redis).
5. Input the secret credentials (`NVIDIA_API_KEY`, `GEMINI_API_KEY`, `CLERK_SECRET_KEY`, and Firebase keys) in the prompt screen.
6. Click **Approve**.

> [!IMPORTANT]
> FastAPI requires system libraries to support PDF parsing and Playwright web scraping. The provided backend Dockerfile handles these dependencies out-of-the-box. Ensure your Render Backend service runs on at least a **Starter** tier (512MB RAM / 1GB RAM) to prevent Out of Memory (OOM) crashing during browser runs.

---

## 🛠️ Option 3: Hybrid Deployment (Vercel + Supabase + Render)

To optimize cost (leveraging free tiers across platforms), you can run components separately:

### 1. Database (Supabase or Neon)
- Create a Postgres instance on [Supabase](https://supabase.com) or [Neon](https://neon.tech).
- Copy the transaction/session connection string and use it as `DATABASE_URL` for the backend.

### 2. Cache & Task Broker (Upstash Redis)
- Create a serverless Redis instance on [Upstash](https://upstash.com).
- Copy the SSL URL (starts with `rediss://`) and set it as `REDIS_URL` in the backend.

### 3. Backend & Celery Worker (Render / Railway)
- **FastAPI Backend**: Deploy as a Web Service on Render/Railway. Set the start command to:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- **Celery Worker**: Deploy as a Background Worker. Set the start command to:
  ```bash
  celery -A app.worker.celery_app worker --loglevel=info
  ```

### 4. Frontend (Vercel)
- Import the `frontend` folder into [Vercel](https://vercel.com).
- Set the Root Directory to `frontend`.
- Add the necessary `NEXT_PUBLIC_` environment variables under Settings -> Environment Variables.
- Click **Deploy**.

---

## 📝 Environment Variables Checklist

| Variable Name | Required | Default / Example | Purpose |
| :--- | :---: | :--- | :--- |
| `DATABASE_URL` | Yes | `postgresql://...` | Relational database connection string |
| `REDIS_URL` | Yes | `redis://...` | Celery broker & result backend connection |
| `CHROMA_PERSIST_DIR` | Yes | `./chroma_db` | Persistent directory for resume search vectors |
| `NVIDIA_API_KEY` | No | `mock_key` | Key for NVIDIA API (enables advanced models) |
| `GEMINI_API_KEY` | No | `mock_key` | Key for Google Gemini API |
| `CLERK_SECRET_KEY` | Yes | `sk_live_...` | Verification key for Clerk user authentication |
| `DEV_AUTH_BYPASS` | Yes | `false` | Disable auth requirements in development |
| `NEXT_PUBLIC_API_URL`| Yes | `http://localhost:8009/api/v1` | URL where the frontend contacts the FastAPI backend |
| `NEXT_PUBLIC_WS_URL` | Yes | `ws://localhost:8009/ws` | Backend WS endpoint for streaming matched logs |

---

## ⚠️ Troubleshooting & Production Tips

- **Playwright Scraping**: Playwright requires browser engines to be installed. If deploying manually on a non-docker environment, ensure you run `playwright install chromium` inside your backend deployment shell.
- **WebSocket Handshake**: If deploying behind a reverse proxy (e.g., NGINX, Cloudflare), make sure to configure support for `Connection "Upgrade"` headers to prevent WebSocket termination on `/ws/jobs` and `/ws/tasks`.
- **Database Migrations**: When deploying the FastAPI backend, it runs `Base.metadata.create_all` automatically on startup to initialize Postgres tables, avoiding manual migration script execution.
