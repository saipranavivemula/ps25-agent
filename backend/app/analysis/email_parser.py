import email
import re
from email import policy
from email.utils import parseaddr
from urllib.parse import urlparse

import tldextract
from bs4 import BeautifulSoup

URL_RE = re.compile(r"https?://[^\s<>\"')]+", re.I)
DOMAIN_LIKE = re.compile(r"(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})", re.I)
SPF_WORDS = {"pass", "fail", "softfail", "neutral", "temperror", "permerror"}


def _registered(host: str) -> str:
    """Main domain of a hostname (www.acmepay.com -> acmepay.com)."""
    host = (host or "").lower().strip(".")
    return tldextract.extract(host).top_domain_under_public_suffix or host


def _domain_of(address: str) -> str:
    return address.rsplit("@", 1)[-1].lower() if "@" in address else ""


def _auth_results(msg) -> dict:
    """Read SPF / DKIM / DMARC verdicts that the receiving mail server wrote."""
    header = " ".join(str(h) for h in msg.get_all("Authentication-Results", []))
    result = {}
    for key in ("spf", "dkim", "dmarc"):
        m = re.search(r"\b" + key + r"\s*=\s*([a-z]+)", header, re.I)
        result[key] = m.group(1).lower() if m else "none"
    if result["spf"] == "none":
        word = str(msg.get("Received-SPF", "")).strip().split(" ")[0].lower()
        if word in SPF_WORDS:
            result["spf"] = word
    return result


def analyse_email(raw: bytes) -> dict:
    """Pull out everything the risk engine needs from one raw .eml message."""
    msg = email.message_from_bytes(raw, policy=policy.default)
    from_addr = parseaddr(str(msg.get("From", "")))[1].lower()
    reply_to = parseaddr(str(msg.get("Reply-To", "")))[1].lower()
    return_path = parseaddr(str(msg.get("Return-Path", "")))[1].lower()
    from_dom = _domain_of(from_addr)

    body = msg.get_body(preferencelist=("html", "plain"))
    content = ""
    if body is not None:
        try:
            content = body.get_content()
        except Exception:
            content = ""

    links: list[str] = []
    mismatches: list[dict] = []
    text = content
    is_html = body is not None and body.get_content_type() == "text/html"
    if is_html:
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href.lower().startswith(("http://", "https://")):
                continue
            links.append(href)
            shown = a.get_text(" ", strip=True)
            m = DOMAIN_LIKE.search(shown)
            if m:
                real_host = urlparse(href).hostname or ""
                if _registered(m.group(1)) != _registered(real_host):
                    mismatches.append({"shown": shown[:80], "real": href[:200]})
        text = soup.get_text(" ", strip=True)

    links += URL_RE.findall(text)
    links = list(dict.fromkeys(links))  # remove duplicates, keep order
    hosts = sorted({urlparse(u).hostname or "" for u in links} - {""})

    return {
        "from": from_addr,
        "from_domain": from_dom,
        "subject": str(msg.get("Subject", "")),
        "reply_to_mismatch": bool(reply_to and _registered(_domain_of(reply_to)) != _registered(from_dom)),
        "return_path_mismatch": bool(return_path and _registered(_domain_of(return_path)) != _registered(from_dom)),
        "auth": _auth_results(msg),
        "links": links[:20],
        "link_hosts": hosts,
        "link_text_mismatch": bool(mismatches),
        "mismatched_links": mismatches[:5],
        "received_hops": len(msg.get_all("Received", [])),
        "has_html": is_html,
        "text": text[:5000],
    }