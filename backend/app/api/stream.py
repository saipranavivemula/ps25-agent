import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..events import publish, subscribe

router = APIRouter(prefix="/api")


@router.get("/stream")
async def stream():
    return StreamingResponse(
        subscribe(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/dev/emit")
async def dev_emit():
    """Demo helper: fires one test event so you can watch the stream."""
    publish("agent.step", {"case_id": 0, "stage": "monitor",
                           "message": "test event", "ts": time.time()})
    return {"sent": True}