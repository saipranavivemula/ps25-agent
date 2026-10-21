import asyncio
from datetime import datetime, timedelta, timezone

import app.analysis.enrich as enrich_mod
from app.analysis.enrich import _age_days_from, enrich, tls_info, whois_info


class FakeResp:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_age_of_none_is_none():
    assert _age_days_from(None) is None


def test_age_of_a_datetime():
    d = datetime.now(timezone.utc) - timedelta(days=10)
    assert _age_days_from(d) == 10


def test_age_of_a_naive_datetime_is_treated_as_utc():
    d = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=5)
    assert _age_days_from(d) == 5


def test_age_uses_the_oldest_date_in_a_list():
    now = datetime.now(timezone.utc)
    assert _age_days_from([now - timedelta(days=3), now - timedelta(days=30)]) == 30


def test_age_is_never_negative():
    assert _age_days_from(datetime.now(timezone.utc) + timedelta(days=2)) == 0


def test_whois_info_parses_rdap_answer(monkeypatch):
    data = {
        "events": [{"eventAction": "registration", "eventDate": "2001-01-13T00:12:14.754Z"}],
        "entities": [{"roles": ["registrar"],
                      "vcardArray": ["vcard", [["fn", {}, "text", "Test Registrar Inc."]]]}],
    }
    monkeypatch.setattr(enrich_mod.httpx, "get", lambda *a, **k: FakeResp(data))
    r = whois_info("wikipedia.org")
    assert r["registrar"] == "Test Registrar Inc."
    assert r["age_days"] > 9000


def test_whois_info_survives_network_error(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("no network")

    monkeypatch.setattr(enrich_mod.httpx, "get", boom)
    r = whois_info("example.com")
    assert r["age_days"] is None
    assert "error" in r


def test_tls_info_on_unresolvable_host():
    r = tls_info("does-not-exist.invalid")
    assert r["tls_valid"] is False
    assert r["age_days"] is None


def test_enrich_combines_all_three_lookups(monkeypatch):
    async def fake_dns(domain):
        return {"A": ["1.2.3.4"], "MX": [], "NS": ["ns1.x."]}

    monkeypatch.setattr(enrich_mod, "dns_info", fake_dns)
    monkeypatch.setattr(enrich_mod, "whois_info", lambda d: {"age_days": 2, "registrar": "R"})
    monkeypatch.setattr(enrich_mod, "tls_info", lambda d: {"tls_valid": True, "age_days": 1})
    r = asyncio.run(enrich("evil.example"))
    assert r["dns"]["A"] == ["1.2.3.4"]
    assert r["whois"]["age_days"] == 2
    assert r["cert"]["age_days"] == 1


def test_enrich_survives_a_crashing_lookup(monkeypatch):
    async def bad_dns(domain):
        raise RuntimeError("boom")

    monkeypatch.setattr(enrich_mod, "dns_info", bad_dns)
    monkeypatch.setattr(enrich_mod, "whois_info", lambda d: {"age_days": 2})
    monkeypatch.setattr(enrich_mod, "tls_info", lambda d: {"tls_valid": True, "age_days": 1})
    r = asyncio.run(enrich("evil.example"))
    assert r["dns"] == {"A": [], "MX": [], "NS": []}
    assert r["whois"]["age_days"] == 2