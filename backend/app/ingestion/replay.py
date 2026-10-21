import asyncio
import json
import pathlib


def load_feed(path: str = "demo/feed.jsonl") -> list[tuple[str, str]]:
    """Read the feed file into a list of (source, target) pairs."""
    items = []
    text = pathlib.Path(path).read_text(encoding="utf-8-sig")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            items.append((row["source"], row["target"]))
        except (ValueError, KeyError):
            continue  # skip a broken line instead of crashing
    return items


async def replay(queue: asyncio.Queue, path: str = "demo/feed.jsonl",
                 delay: float = 2.0, loop_forever: bool = False) -> None:
    """Drip-feed candidates into the queue so the dashboard looks alive."""
    while True:
        for source, target in load_feed(path):
            await queue.put((source, target))
            await asyncio.sleep(delay)
        if not loop_forever:
            return