import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.routes import api_router
from app.services.websocket_manager import ws_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")

# Auto-create tables (SQLite fallback makes this instant)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")
except Exception as e:
    logger.error(f"Error initializing database tables: {e}")

app = FastAPI(
    title="AI Career CoPilot API",
    description="Backend API powering the agentic resume parser, job matching engine, and outreach automator.",
    version="1.0.0"
)

# Enable CORS for the React/Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core routers
app.include_router(api_router, prefix="/api/v1")

# Mount static files to serve uploaded resumes
from fastapi.staticfiles import StaticFiles
import os
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "resumes"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Healthcheck route
@app.get("/health")
@app.get("/api/v1/health")
def healthcheck():
    return {
        "status": "healthy",
        "database": "connected",
        "mock_mode": settings.NVIDIA_API_KEY == "mock_key"
    }

# ==========================================
# WEBSOCKET CHANNELS
# ==========================================
@app.websocket("/ws/jobs")
async def websocket_jobs_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, "jobs")
    try:
        while True:
            # Keep connection alive; clients generally just listen to broadcasts
            data = await websocket.receive_text()
            logger.info(f"Received msg on jobs channel: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "jobs")
    except Exception as e:
        logger.warning(f"Error on jobs WebSocket connection: {e}")
        ws_manager.disconnect(websocket, "jobs")

@app.websocket("/ws/tasks")
async def websocket_tasks_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, "tasks")
    try:
        while True:
            # Keep connection alive; clients generally just listen to broadcasts
            data = await websocket.receive_text()
            logger.info(f"Received msg on tasks channel: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "tasks")
    except Exception as e:
        logger.warning(f"Error on tasks WebSocket connection: {e}")
        ws_manager.disconnect(websocket, "tasks")
