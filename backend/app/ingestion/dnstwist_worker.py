import asyncio
import json
import pathlib
import shutil
import subprocess
import sys


def _dnstwist_path() -> str:
    """Find the dnstwist program installed inside this virtual environment."""
    bin_dir = pathlib.Path(sys.executable).parent
    for name in ("dnstwist.exe", "dnstwist"):
        p = bin_dir / name
        if p.exists():
            return str(p)
    return shutil.which("dnstwist") or "dnstwist"


def _to_ascii(domain: str) -> str:
    """Normalise to plain ASCII (punycode) so every domain looks the same."""
    try:
        return domain.encode("idna").decode("ascii").lower()
    except Exception:
        return domain.lower()


def lookalikes(domain: str, fuzzers: str | None = None, timeout: int = 240) -> list[str]:
    """Registered look-alike variants of `domain`. Blocking; can take a while."""
    cmd = [_dnstwist_path(), "--registered", "--format", "json"]
    if fuzzers:
        cmd += ["--fuzzers", fuzzers]
    cmd.append(domain)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=timeout)
        rows = json.loads(out.stdout or "[]")
    except Exception:
        return []

    found: list[str] = []
    for row in rows:
        if row.get("fuzzer") == "*original":
            continue
        d = _to_ascii(row.get("domain", ""))
        if d and d not in found:
            found.append(d)
    return found


async def watch_brands(queue: asyncio.Queue, brands: list[str],
                       interval_hours: float = 6.0, seen: set[str] | None = None) -> None:
    """Forever: look up variants of each protected brand and queue only NEW ones."""
    seen = seen if seen is not None else set()
    while True:
        for brand in brands:
            variants = await asyncio.to_thread(lookalikes, brand)
            for d in variants:
                if d not in seen:
                    seen.add(d)
                    await queue.put(("dnstwist", d))
        await asyncio.sleep(interval_hours * 3600)