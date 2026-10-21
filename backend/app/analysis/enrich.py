import asyncio
import socket
import ssl
import time
from datetime import datetime, timezone

import dns.asyncresolver
import dns.resolver
import httpx
import tldextract


def _age_days_from(value) -> int | None:
    """Days since a date. Accepts a datetime, a list of them, or None."""
    def aware(v):
        if not isinstance(v, datetime):
            return None
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)

    values = value if isinstance(value, list) else [value]
    values = [v for v in map(aware, values) if v]
    if not values:
        return None
    return max(0, (datetime.now(timezone.utc) - min(values)).days)
async def dns_info(domain: str) -> dict:
    """Look up IP addresses (A), mail servers (MX) and name servers (NS)."""
    errors: dict[str, str] = {}

    async def one(rtype: str):
        # Try the system DNS first, then public DNS servers as a fallback
        for nameservers in (None, ["8.8.8.8", "1.1.1.1"]):
            res = dns.asyncresolver.Resolver()
            res.lifetime = 5
            if nameservers:
                res.nameservers = nameservers
            try:
                answer = await res.resolve(domain, rtype)
                return rtype, [r.to_text() for r in answer]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                return rtype, []  # a real "no such record" answer
            except Exception as e:
                errors[rtype] = type(e).__name__
        return rtype, []

    result = dict(await asyncio.gather(*(one(t) for t in ("A", "MX", "NS"))))
    if errors:
        result["errors"] = errors
    return result


def whois_info(domain: str) -> dict:
    """Registration facts via RDAP over HTTPS (classic WHOIS port 43 is often blocked)."""
    main = tldextract.extract(domain).top_domain_under_public_suffix or domain
    try:
        r = httpx.get(
            "https://rdap.org/domain/" + main,
            timeout=8,
            follow_redirects=True,
            headers={"Accept": "application/rdap+json"},
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:100]}", "age_days": None}

    created = None
    for ev in data.get("events", []):
        if ev.get("eventAction") == "registration":
            created = ev.get("eventDate")

    registrar = None
    for ent in data.get("entities", []):
        if "registrar" in ent.get("roles", []):
            try:
                for item in ent["vcardArray"][1]:
                    if item[0] == "fn":
                        registrar = item[3]
            except (KeyError, IndexError, TypeError):
                pass

    age = None
    if created:
        try:
            age = _age_days_from(datetime.fromisoformat(created.replace("Z", "+00:00")))
        except ValueError:
            pass
    return {"registrar": registrar, "created": created, "age_days": age}

def tls_info(domain: str, port: int = 443) -> dict:
    """Read the HTTPS certificate. A failed handshake is itself a clue."""
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((domain, port), timeout=4) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as tls:
                cert = tls.getpeercert()
        issuer = dict(x[0] for x in cert.get("issuer", ()))
        started = ssl.cert_time_to_seconds(cert["notBefore"])
        return {
            "tls_valid": True,
            "issuer": issuer.get("organizationName") or issuer.get("commonName"),
            "not_before": cert["notBefore"],
            "age_days": int((time.time() - started) // 86400),
            "san": [v for k, v in cert.get("subjectAltName", ()) if k == "DNS"][:10],
        }
    except Exception as e:
        return {"tls_valid": False, "error": f"{type(e).__name__}: {str(e)[:100]}", "age_days": None}


async def enrich(domain: str) -> dict:
    """Run all three lookups in parallel; a slow one never blocks the others."""
    loop = asyncio.get_running_loop()

    async def guarded(awaitable, timeout, fallback):
        try:
            return await asyncio.wait_for(awaitable, timeout)
        except Exception:
            return fallback

    d, w, t = await asyncio.gather(
        guarded(dns_info(domain), 14, {"A": [], "MX": [], "NS": []}),
        guarded(loop.run_in_executor(None, whois_info, domain), 12,
                {"error": "whois timed out", "age_days": None}),
        guarded(loop.run_in_executor(None, tls_info, domain), 8,
                {"tls_valid": False, "error": "tls timed out", "age_days": None}),
    )
    return {"dns": d, "whois": w, "cert": t}