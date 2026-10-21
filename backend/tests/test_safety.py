import socket

from app.analysis import safety
from app.analysis.safety import is_safe_public_url
from app.config import settings


def fake_dns(*ips):
    """Pretend DNS answered with these IP addresses."""
    def _fake(host, port, *args, **kwargs):
        rows = []
        for ip in ips:
            if ":" in ip:
                rows.append((socket.AF_INET6, socket.SOCK_STREAM, 6, "", (ip, port, 0, 0)))
            else:
                rows.append((socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port)))
        return rows
    return _fake


def test_public_address_is_allowed(monkeypatch):
    monkeypatch.setattr(settings, "allow_local_demo_hosts", "")
    monkeypatch.setattr(safety.socket, "getaddrinfo", fake_dns("93.184.216.34"))
    assert is_safe_public_url("https://example.com/") == (True, "ok")


def test_internal_addresses_are_blocked(monkeypatch):
    monkeypatch.setattr(settings, "allow_local_demo_hosts", "")
    for ip in ["10.0.0.5", "192.168.1.1", "127.0.0.1", "169.254.169.254", "100.64.0.1", "::1"]:
        monkeypatch.setattr(safety.socket, "getaddrinfo", fake_dns(ip))
        ok, why = is_safe_public_url("http://some-name.example/")
        assert ok is False, ip
        assert why == "resolves to a non-public address"


def test_one_bad_address_among_good_ones_blocks_the_url(monkeypatch):
    monkeypatch.setattr(settings, "allow_local_demo_hosts", "")
    monkeypatch.setattr(safety.socket, "getaddrinfo", fake_dns("93.184.216.34", "127.0.0.1"))
    assert is_safe_public_url("http://tricky.example/")[0] is False


def test_ipv4_hidden_inside_ipv6_is_blocked(monkeypatch):
    monkeypatch.setattr(settings, "allow_local_demo_hosts", "")
    monkeypatch.setattr(safety.socket, "getaddrinfo", fake_dns("::ffff:127.0.0.1"))
    assert is_safe_public_url("http://tricky.example/")[0] is False


def test_only_http_and_https_are_allowed():
    for url in ["ftp://example.com/x", "file:///etc/passwd", "javascript:alert(1)",
                "gopher://example.com", "http://", "not a url", ""]:
        assert is_safe_public_url(url)[0] is False, url


def test_unresolvable_name_is_refused(monkeypatch):
    monkeypatch.setattr(settings, "allow_local_demo_hosts", "")

    def boom(*args, **kwargs):
        raise socket.gaierror("no such host")

    monkeypatch.setattr(safety.socket, "getaddrinfo", boom)
    assert is_safe_public_url("https://nope.example/") == (False, "does not resolve")


def test_demo_host_is_allowed_only_when_configured(monkeypatch):
    monkeypatch.setattr(safety.socket, "getaddrinfo", fake_dns("127.0.0.1"))
    monkeypatch.setattr(settings, "allow_local_demo_hosts", "localhost:9000")
    assert is_safe_public_url("http://localhost:9000/") == (True, "allowed demo host")
    assert is_safe_public_url("http://localhost:9001/")[0] is False
    monkeypatch.setattr(settings, "allow_local_demo_hosts", "")
    assert is_safe_public_url("http://localhost:9000/")[0] is False