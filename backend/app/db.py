from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings
from .models import AuditLog, Base, PolicyRow, utcnow

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create all tables, and a default policy row if none exists."""
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(PolicyRow).count() == 0:
            db.add(PolicyRow(
                high_threshold=settings.high_threshold,
                medium_threshold=settings.medium_threshold,
                auto_actions_enabled=settings.auto_actions_enabled,
            ))
            db.commit()


def get_db():
    """FastAPI dependency: opens a session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def audit(db, actor: str, event: str, case_id: int | None = None, details: dict | None = None) -> None:
    """Add one row to the append-only audit log."""
    db.add(AuditLog(ts=utcnow(), actor=actor, event=event, case_id=case_id, details=details or {}))
    db.commit()