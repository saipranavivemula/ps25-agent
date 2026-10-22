# app/api/analyze.py
from fastapi import APIRouter, BackgroundTasks, UploadFile, File
from pydantic import BaseModel
from app.agent.investigator import InvestigationAgent
from app.db import SessionLocal, audit
from app.models import Case, Action, Evidence

router = APIRouter(prefix="/api")

# Global agent instance (initialized in main.py)
agent: InvestigationAgent = None

# ⚡ CHANGED: Added 'async' here
async def run_agent_in_background(source: str, target: str, raw_email: bytes = None):
    db = SessionLocal()
    try:
        # 1. Run the AI pipeline
        # ⚡ CHANGED: Using 'await' instead of 'asyncio.run()'
        result = await agent.investigate(source, target, raw_email)
        
        # 2. Save Case to DB
        new_case = Case(
            source=source, 
            target=target, 
            target_type="email" if raw_email else "domain",
            risk_score=result["score"], 
            decision=result["decision"]["decision"],
            reasons=result["reasons"], 
            summary=result["summary"], 
            status="new" if result["decision"]["decision"] == "low" else "awaiting_review",
            seconds=result["latency_seconds"]
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        
        # 3. Save individual Evidence records
        for kind, data in result["evidence"].items():
            if data:
                ev_record = Evidence(case_id=new_case.id, kind=kind, data=data)
                db.add(ev_record)
        
        # 4. Save Actions to DB
        for act_type in result["decision"]["actions"]:
            new_act = Action(
                case_id=new_case.id, 
                type=act_type, 
                state="pending_approval" if result["decision"]["needs_approval"] else "simulated",
                payload={"domain": target}
            )
            db.add(new_act)
            
        # 5. Save Audit Log
        audit(db, actor="system", event="case.created", case_id=new_case.id, details={"target": target})
        
    except Exception as e:
        print(f"Error in background agent: {e}")
    finally:
        db.close()

class URLRequest(BaseModel):
    url: str

@router.post("/analyze/url")
def analyze_url(req: URLRequest, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(run_agent_in_background, "manual", req.url)
    return {"status": "processing", "message": "Agent started. Watch /api/stream for updates."}

@router.post("/analyze/email")
def analyze_email(bg_tasks: BackgroundTasks, file: UploadFile = File(...)):
    raw = file.file.read()
    bg_tasks.add_task(run_agent_in_background, "email", file.filename, raw)
    return {"status": "processing", "message": "Agent started. Watch /api/stream for updates."}