# app/api/cases.py
import json
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db, audit
from app.models import Case, Action, Feedback, PolicyRow, AllowlistEntry, AuditLog
from pydantic import BaseModel

router = APIRouter(prefix="/api")

# 👇 This class MUST be defined before the functions that use it
class ReviewRequest(BaseModel):
    verdict: str # "confirmed", "false_positive", "unsure"
    note: str = ""
    analyst: str = "analyst"

@router.get("/cases")
def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.created_at.desc()).all()

@router.get("/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c: raise HTTPException(404, "Case not found")
    
    # Convert the list of Evidence objects into a dictionary
    ev_dict = {}
    for e in c.evidence:
        ev_dict[e.kind] = e.data
        
    return {
        "id": c.id,
        "created_at": c.created_at,
        "source": c.source,
        "target": c.target,
        "target_type": c.target_type,
        "status": c.status,
        "risk_score": c.risk_score,
        "decision": c.decision,
        "reasons": c.reasons,
        "summary": c.summary,
        "seconds": c.seconds,
        "evidence": ev_dict
    }

@router.post("/cases/{case_id}/review")
def review_case(case_id: int, req: ReviewRequest, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c: raise HTTPException(404, "Case not found")
    
    c.status = req.verdict
    fb = Feedback(case_id=case_id, analyst=req.analyst, verdict=req.verdict, note=req.note)
    db.add(fb)
    
    audit(db, actor=req.analyst, event="case.reviewed", case_id=case_id, details={"verdict": req.verdict})
    return {"status": "ok", "case_status": c.status}

@router.get("/actions")
def list_actions(db: Session = Depends(get_db)):
    return db.query(Action).order_by(Action.created_at.desc()).all()

@router.post("/actions/{action_id}/approve")
def approve_action(action_id: int, db: Session = Depends(get_db)):
    act = db.query(Action).filter(Action.id == action_id).first()
    if not act: raise HTTPException(404, "Action not found")
    
    if act.state == "executed":
        return {"status": "already_executed", "action_id": action_id}

    # --- SIMULATE THE ACTION EXECUTION ---
    if act.type == "block_url":
        domain = act.payload.get("domain", "unknown.com")
        with open("blocklist.txt", "a") as f:
            f.write(f"{domain}\n")
        print(f"  -> [SIMULATED] Blocked {domain} (appended to blocklist.txt)")
    
    elif act.type == "report_registrar":
        print(f"  -> [SIMULATED] Generated report for case {act.case_id}")
    
    elif act.type == "ticket":
        print(f"  -> [SIMULATED] Created SOC Ticket for case {act.case_id}")
        
    else:
        print(f"  -> [SIMULATED] Executed action: {act.type} for case {act.case_id}")

    # Update DB state
    act.state = "executed"
    audit(db, actor="analyst", event="action.executed", case_id=act.case_id, details={"type": act.type})
    db.commit()
    
    return {"status": "executed", "action_id": action_id, "type": act.type}

@router.post("/actions/{action_id}/rollback")
def rollback_act(action_id: int, db: Session = Depends(get_db)):
    act = db.query(Action).filter(Action.id == action_id).first()
    if not act: raise HTTPException(404, "Action not found")
    
    if act.type == "block_url":
        domain = act.payload.get("domain")
        if domain:
            print(f"  -> [SIMULATED] Rolled back block for {domain}")
            
    act.state = "rolled_back"
    audit(db, actor="analyst", event="action.rolled_back", case_id=act.case_id, details={"type": act.type})
    db.commit()
    return {"status": "rolled_back", "action_id": action_id}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    cases = db.query(Case).all()
    high = sum(1 for c in cases if c.decision == "high")
    medium = sum(1 for c in cases if c.decision == "medium")
    low = sum(1 for c in cases if c.decision == "low")
    
    # 👇 NEW: Count cases waiting for review
    awaiting = sum(1 for c in cases if c.status == "awaiting_review")
    
    # Calculate median detection time
    times = sorted([c.seconds for c in cases if c.seconds > 0])
    median = times[len(times)//2] if times else 0.0

    return {
        "total": len(cases),
        "by_decision": {"high": high, "medium": medium, "low": low},
        "awaiting_review": awaiting, # 👈 NEW: Return the count
        "median_detection_seconds": median
    }

@router.get("/policy")
def get_policy(db: Session = Depends(get_db)):
    p = db.query(PolicyRow).first()
    allowlist = [a.domain for a in db.query(AllowlistEntry).all()]
    
    if not p:
        return {
            "high_threshold": 0.85, 
            "medium_threshold": 0.70, 
            "auto_actions_enabled": False,
            "allowlist": allowlist
        }
    return {
        "high_threshold": p.high_threshold,
        "medium_threshold": p.medium_threshold,
        "auto_actions_enabled": p.auto_actions_enabled,
        "allowlist": allowlist
    }

class PolicyUpdateRequest(BaseModel):
    high_threshold: float
    medium_threshold: float
    auto_actions_enabled: bool
    allowlist: list[str] = []

@router.put("/policy")
def update_policy(req: PolicyUpdateRequest, db: Session = Depends(get_db)):
    p = db.query(PolicyRow).first()
    if not p:
        p = PolicyRow()
        db.add(p)
    
    p.high_threshold = req.high_threshold
    p.medium_threshold = req.medium_threshold
    p.auto_actions_enabled = req.auto_actions_enabled
    
    # Update Allowlist: Delete old ones, add new ones
    db.query(AllowlistEntry).delete()
    for domain in req.allowlist:
        db.add(AllowlistEntry(domain=domain, reason="Added from UI", added_by="admin"))
    
    audit(db, actor="admin", event="policy.updated", details={"high": p.high_threshold, "medium": p.medium_threshold})
    db.commit()
    return {"status": "ok"}

@router.get("/models/metrics")
def get_model_metrics():
    metrics = {}
    
    # Path relative to the backend folder
    text_metrics_path = "models/text_metrics.json"
    url_metrics_path = "models/url_metrics.json"
    
    if os.path.exists(text_metrics_path):
        with open(text_metrics_path) as f:
            metrics["text_model"] = json.load(f)
            
    if os.path.exists(url_metrics_path):
        with open(url_metrics_path) as f:
            metrics["url_model"] = json.load(f)
            
    return metrics

# 👇 THIS IS THE NEW AUDIT LOG ENDPOINT 👇
@router.get("/audit")
def get_audit_log(db: Session = Depends(get_db)):
    # Join AuditLog with Case to get the target URL
    logs = db.query(AuditLog, Case.target).outerjoin(Case, AuditLog.case_id == Case.id).order_by(AuditLog.ts.desc()).limit(100).all()
    
    result = []
    for log, target in logs:
        result.append({
            "id": log.id,
            "ts": log.ts,
            "actor": log.actor,
            "event": log.event,
            "case_id": log.case_id,
            "target": target,
            "details": log.details
        })
    return result