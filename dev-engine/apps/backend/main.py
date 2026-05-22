from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
import structlog
from .core.config import settings
from .services.ingestion import ingest_repository
from .services.fix_engine import run_autonomous_fix
from .utils.logger import setup_logging

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    structlog.get_logger().info("Dev-Engine started", env=settings.ENV)
    yield

app = FastAPI(title="Dev-Engine", lifespan=lifespan)

@app.post("/ingest")
async def start_ingest(repo_url: str, background: BackgroundTasks):
    background.add_task(ingest_repository, repo_url)
    return {"status": "started", "repo": repo_url}

@app.post("/fix")
async def start_fix(repo_url: str, error: str, repo_path: str):
    result = await run_autonomous_fix(repo_url, error, repo_path)
    return result