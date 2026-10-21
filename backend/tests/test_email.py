from pathlib import Path

from app.analysis.email_parser import analyse_email

EMAILS = Path(__file__).resolve().parent.parent / "demo" / "emails"


def load(name: str) -> dict:
    return analyse_email((EMAILS / name).read_bytes())


def make(headers: str, body: str, ctype: str = "text/html") -> bytes:
    raw = (
        "From: Someone <someone@acmepay.com>\n"
        "To: student@example.com\n"
        "Subject: test\n"
        "MIME-Version: 1.0\n"
        f"Content-Type: {ctype}; charset=utf-8\n"
        f"{headers}\n"
        f"{body}\n"
    )
    return raw.encode("utf-8")


def test_legit_newsletter_is_clean():
    r = load("legit_newsletter.eml")
    assert r["from_domain"] == "acmepay.com"
    assert r["auth"] == {"spf": "pass", "dkim": "pass", "dmarc": "pass"}
    assert r["reply_to_mismatch"] is False
    assert r["link_text_mismatch"] is False
    assert len(r["links"]) == 2


def test_phish_fails_auth_and_has_fake_link():
    r = load("phish_urgent.eml")
    assert r["auth"] == {"spf": "fail", "dkim": "fail", "dmarc": "fail"}
    assert r["reply_to_mismatch"] is True
    assert r["return_path_mismatch"] is True
    assert r["link_text_mismatch"] is True
    assert r["mismatched_links"][0]["real"].startswith("http://acmepay-secure-login.com")
    assert r["received_hops"] == 2
    assert "suspended" in r["text"]


def test_borderline_email_looks_alarming_but_is_clean():
    r = load("borderline.eml")
    assert r["auth"]["dmarc"] == "pass"
    assert r["link_text_mismatch"] is False
    assert r["reply_to_mismatch"] is False
    assert "acmebank.com" in r["link_hosts"][0]


def test_missing_authentication_header_gives_none():
    r = analyse_email(make("", "<p>hi</p>"))
    assert r["auth"] == {"spf": "none", "dkim": "none", "dmarc": "none"}


def test_received_spf_header_is_used_as_fallback():
    r = analyse_email(make("Received-SPF: softfail (domain does not match)", "<p>hi</p>"))
    assert r["auth"]["spf"] == "softfail"


def test_plain_text_email_links_are_found():
    r = analyse_email(make("", "Please visit https://example.org/a now", ctype="text/plain"))
    assert r["has_html"] is False
    assert r["links"] == ["https://example.org/a"]
    assert r["link_text_mismatch"] is False


def test_scripts_are_removed_from_text():
    r = analyse_email(make("", "<p>hello</p><script>alert('x')</script>"))
    assert "alert" not in r["text"]
    assert "hello" in r["text"]


def test_mailto_links_are_ignored():
    r = analyse_email(make("", '<a href="mailto:a@b.com">mail us</a>'))
    assert r["links"] == []


def test_link_text_without_a_domain_is_not_flagged():
    r = analyse_email(make("", '<a href="https://evil.example.net/x">Click here</a>'))
    assert r["link_text_mismatch"] is False
    assert r["links"] == ["https://evil.example.net/x"]


def test_garbage_input_does_not_crash():
    r = analyse_email(b"this is not an email at all")
    assert r["from_domain"] == ""
    assert r["links"] == []
    assert r["auth"]["spf"] == "none"


def test_long_text_is_truncated():
    r = analyse_email(make("", "<p>" + "word " * 5000 + "</p>"))
    assert len(r["text"]) <= 5000