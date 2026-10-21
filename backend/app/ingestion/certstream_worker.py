import asyncio
import threading

import certstream

from ..analysis.domain import analyse_domain


def is_lookalike(domain: str, brands: list[str], threshold: float = 0.80) -> bool:
    r = analyse_domain(domain, brands)
    return (not r["is_protected_domain"]) and r["best_match"]["score"] >= threshold


def start_certstream(queue: asyncio.Queue, loop: asyncio.AbstractEventLoop,
                     brands: list[str], url: str,
                     seen: set[str] | None = None,
                     stats: dict | None = None) -> threading.Thread:
    """Listen to live certificate events in a background thread and queue look-alikes."""
    seen = seen if seen is not None else set()
    stats = stats if stats is not None else {}
    stats.setdefault("certs", 0)
    stats.setdefault("matches", 0)

    def on_event(message, context):
        if message.get("message_type") != "certificate_update":
            return
        stats["certs"] += 1
        try:
            domains = message["data"]["leaf_cert"]["all_domains"]
        except (KeyError, TypeError):
            return
        for dom in domains[:20]:
            dom = dom.lstrip("*.").lower()
            if not dom or dom in seen:
                continue
            try:
                hit = is_lookalike(dom, brands)
            except Exception:
                continue  # one odd domain must never stop the stream
            if hit:
                seen.add(dom)
                stats["matches"] += 1
                loop.call_soon_threadsafe(queue.put_nowait, ("certstream", dom))

    t = threading.Thread(
        target=certstream.listen_for_events,
        args=(on_event,),
        kwargs={"url": url},
        daemon=True,
    )
    t.start()
    return t