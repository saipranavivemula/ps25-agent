# app/api/cases.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db, audit
from app.models import Case, Action, Feedback
from pydantic import BaseModel

router = APIRouter(prefix="/api")

@router.get("/cases")
def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.created_at.desc()).all()

@router.get("/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c: raise HTTPException(404, "Case not found")
    return c

class ReviewRequest(BaseModel):
    verdict: str # "confirmed", "false_positive", "unsure"
    note: str = ""
    analyst: str = "analyst"

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