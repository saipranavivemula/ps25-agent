import asyncio
import sys

# Fix for Windows + Playwright subprocesses
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import stream, analyze, cases
from .config import settings
from .db import init_db, SessionLocal
from .models import PolicyRow, AllowlistEntry
from .agent.investigator import InvestigationAgent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create DB tables and default policy
    init_db()
    
    # 2. Load Policy and Allowlist from DB
    db = SessionLocal()
    policy = db.query(PolicyRow).first()
    allowlist_entries = db.query(AllowlistEntry).all()
    allowlist_set = {a.domain for a in allowlist_entries}
    db.close()
    
    # 3. Initialize the Agent and inject it into the analyze router
    brands = [b.strip() for b in settings.protected_brands.split(",")]
    agent_instance = InvestigationAgent(
        db_factory=SessionLocal,
        brands=brands,
        policy_loader=lambda: {
            "high_threshold": policy.high_threshold, 
            "medium_threshold": policy.medium_threshold, 
            "auto_actions_enabled": policy.auto_actions_enabled
        },
        allowlist_loader=lambda: allowlist_set
    )
    
    analyze.agent = agent_instance
    print("✅ Backend Agent and Database initialized.")
    
    yield

app = FastAPI(title="PS25 Phishing Intelligence Agent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(stream.router)
app.include_router(analyze.router)
app.include_router(cases.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}