import asyncio
import json
from typing import AsyncIterator

_subscribers: set[asyncio.Queue] = set()


def publish(event_type: str, payload: dict) -> None:
    """Send an event to every connected listener (never blocks, never crashes)."""
    msg = json.dumps({"type": event_type, "data": payload}, default=str)
    for q in list(_subscribers):
        try:
            q.put_nowait(msg)
        except asyncio.QueueFull:
            pass  # a slow listener just misses this event


async def subscribe() -> AsyncIterator[str]:
    """Yield events as Server-Sent-Event text frames."""
    q: asyncio.Queue = asyncio.Queue(maxsize=200)
    _subscribers.add(q)
    try:
        while True:
            try:
                msg = await asyncio.wait_for(q.get(), timeout=15)
                yield "data: " + msg + "\n\n"
            except asyncio.TimeoutError:
                yield ": ping\n\n"   # keeps the connection alive
    finally:
        _subscribers.discard(q)