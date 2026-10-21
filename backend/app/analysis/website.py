import asyncio
import os
import pathlib
from urllib.parse import urlparse

import tldextract
from playwright.async_api import async_playwright

from ..config import settings
from .safety import is_safe_public_url

_SEM = asyncio.Semaphore(2)  # never run more than 2 browsers at once

PAGE_FACTS_JS = r"""
() => ({
  title: document.title || "",
  forms: [...document.forms].map(f => ({
    action: f.action || "",
    method: (f.method || "get").toLowerCase(),
    hasPassword: !!f.querySelector("input[type=password]"),
    inputs: [...f.querySelectorAll("input")].map(i => (i.type || "text") + ":" + (i.name || ""))
  })),
  iframes: document.querySelectorAll("iframe").length,
  linkCount: document.querySelectorAll("a[href]").length,
  text: document.body ? document.body.innerText.slice(0, 3000) : ""
})
"""


def _registered(host: str) -> str:
    host = (host or "").lower()
    return tldextract.extract(host).top_domain_under_public_suffix or host


async def _guard(route, request, cache: dict) -> None:
    """Allow a request only if its host is safe. Applies to redirects and sub-requests too."""
    url = request.url
    if url.startswith(("data:", "blob:", "about:")):
        await route.continue_()
        return
    p = urlparse(url)
    key = (p.hostname or "") + ":" + str(p.port or "")
    if key not in cache:
        cache[key] = (await asyncio.to_thread(is_safe_public_url, url))[0]
    if cache[key]:
        await route.continue_()
    else:
        await route.abort()


async def _inspect(url: str, shot_path: pathlib.Path, timeout_ms: int) -> dict:
    cache: dict = {}
    args = ["--no-sandbox"] if os.environ.get("PS25_NO_SANDBOX") else []  # only needed inside Docker
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=args)
        try:
            ctx = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                accept_downloads=False,
                ignore_https_errors=True,  # phishing sites often have broken certificates
            )
            await ctx.route("**/*", lambda route, request: _guard(route, request, cache))
            page = await ctx.new_page()
            resp = await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            await page.wait_for_timeout(1200)
            await page.screenshot(path=str(shot_path), full_page=False)
            facts = await page.evaluate(PAGE_FACTS_JS)
            final_url = page.url
            status = resp.status if resp else None
        finally:
            await browser.close()

    page_host = _registered(urlparse(final_url).hostname or "")
    for f in facts["forms"]:
        action_host = _registered(urlparse(f["action"]).hostname or "")
        f["posts_to_other_host"] = bool(action_host) and action_host != page_host
    return {
        "final_url": final_url,
        "status": status,
        "redirected": _registered(urlparse(url).hostname or "") != page_host,
        "title": facts["title"],
        "forms": facts["forms"],
        "password_form": any(f["hasPassword"] for f in facts["forms"]),
        "posts_to_other_host": any(f["hasPassword"] and f["posts_to_other_host"] for f in facts["forms"]),
        "iframes": facts["iframes"],
        "link_count": facts["linkCount"],
        "text": facts["text"],
        "screenshot": str(shot_path),
    }


async def inspect_site(url: str, case_id: int | str = 0, timeout_ms: int = 12000) -> dict:
    """Open `url` in a locked-down headless browser; return a screenshot path and page facts."""
    ok, why = await asyncio.to_thread(is_safe_public_url, url)
    if not ok:
        return {"skipped": True, "reason": why}

    out_dir = pathlib.Path(settings.artifacts_dir) / str(case_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    async with _SEM:
        try:
            return await asyncio.wait_for(_inspect(url, out_dir / "screenshot.png", timeout_ms), timeout=30)
        except asyncio.TimeoutError:
            return {"error": "inspection timed out after 30 seconds"}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {str(e)[:150]}"}