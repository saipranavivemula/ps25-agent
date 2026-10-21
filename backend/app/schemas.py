from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Reason(BaseModel):
    signal: str
    contribution: float
    detail: str = ""


class TimelineItem(BaseModel):
    ts: str
    stage: str          # monitor | investigate | verify | assess | respond
    message: str


class ActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    state: str          # simulated | pending_approval | executed | failed | rolled_back
    payload: dict = Field(default_factory=dict)


class CaseBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    source: str
    target: str
    target_type: str
    status: str
    risk_score: float
    decision: str       # high | medium | low


class CaseFull(CaseBrief):
    reasons: list[Reason] = Field(default_factory=list)
    summary: str = ""
    evidence: dict = Field(default_factory=dict)
    actions: list[ActionOut] = Field(default_factory=list)
    timeline: list[TimelineItem] = Field(default_factory=list)


class PolicyOut(BaseModel):
    high_threshold: float
    medium_threshold: float
    auto_actions_enabled: bool
    allowlist: list[str] = Field(default_factory=list)


class AnalyzeUrlIn(BaseModel):
    url: str


class ReviewIn(BaseModel):
    verdict: str        # confirmed | false_positive | unsure
    note: str = ""