from datetime import datetime, timezone

from sqlalchemy import (JSON, Boolean, DateTime, Float, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class Case(Base):
    """One suspected threat (a domain, URL or email)."""
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    source: Mapped[str] = mapped_column(String(32))        # certstream|dnstwist|email|manual
    target: Mapped[str] = mapped_column(String(512))
    target_type: Mapped[str] = mapped_column(String(16))   # domain|url|email
    status: Mapped[str] = mapped_column(String(24), default="new")
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    decision: Mapped[str] = mapped_column(String(16), default="low")
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    summary: Mapped[str] = mapped_column(Text, default="")
    seconds: Mapped[float] = mapped_column(Float, default=0.0)  # detection time

    evidence = relationship("Evidence", back_populates="case", cascade="all, delete")
    actions = relationship("Action", back_populates="case", cascade="all, delete")


class Evidence(Base):
    """Raw findings from one analyzer, attached to a case."""
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    kind: Mapped[str] = mapped_column(String(24))          # domain|cert|dns|whois|email|website|nlp|url_model|vision
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    case = relationship("Case", back_populates="evidence")


class Action(Base):
    """What the system did, or would do, about a case."""
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    type: Mapped[str] = mapped_column(String(24))          # block_url|quarantine_email|report_registrar|ticket|...
    state: Mapped[str] = mapped_column(String(24), default="simulated")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    case = relationship("Case", back_populates="actions")


class AuditLog(Base):
    """Append-only history. Never update or delete rows here."""
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    actor: Mapped[str] = mapped_column(String(64))         # system or analyst name
    event: Mapped[str] = mapped_column(String(64))
    case_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)


class Feedback(Base):
    """Analyst verdicts, later used for retraining."""
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    analyst: Mapped[str] = mapped_column(String(64))
    verdict: Mapped[str] = mapped_column(String(24))       # confirmed|false_positive|unsure
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AllowlistEntry(Base):
    """Domains that must never be blocked."""
    __tablename__ = "allowlist"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain: Mapped[str] = mapped_column(String(255), unique=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    added_by: Mapped[str] = mapped_column(String(64), default="system")


class PolicyRow(Base):
    """Editable decision policy (one row)."""
    __tablename__ = "policy"

    id: Mapped[int] = mapped_column(primary_key=True)
    high_threshold: Mapped[float] = mapped_column(Float, default=0.85)
    medium_threshold: Mapped[float] = mapped_column(Float, default=0.60)
    auto_actions_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)