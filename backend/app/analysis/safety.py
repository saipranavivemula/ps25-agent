import ipaddress
import socket
from urllib.parse import urlparse

from ..config import settings


def _demo_hosts() -> set[str]:
    """Hosts (like localhost:9000) you explicitly allow for the local demo."""
    return {h.strip().lower() for h in settings.allow_local_demo_hosts.split(",") if h.strip()}


def is_safe_public_url(url: str) -> tuple[bool, str]:
    """True only for http(s) URLs whose host resolves to PUBLIC internet addresses.

    This stops 'SSRF': someone tricking our browser into opening internal pages
    (localhost, the router, cloud metadata) by submitting a crafted URL.
    """
    try:
        u = urlparse(url.strip())
        host = u.hostname
        port = u.port
    except ValueError:
        return False, "malformed URL"
    if u.scheme not in ("http", "https") or not host:
        return False, "unsupported scheme or missing host"

    if (host.lower() + (":" + str(port) if port else "")) in _demo_hosts():
        return True, "allowed demo host"

    try:
        infos = socket.getaddrinfo(host, port or (443 if u.scheme == "https" else 80),
                                   proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError):
        return False, "does not resolve"

    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0].split("%")[0])
        except ValueError:
            return False, "unreadable address"
        if ip.version == 6 and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if not ip.is_global:
            return False, "resolves to a non-public address"
    return True, "ok"