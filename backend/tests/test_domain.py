from app.analysis.domain import analyse_domain

BRANDS = ["acmepay.com", "acmebank.com"]


def lookalike(domain: str) -> bool:
    r = analyse_domain(domain, BRANDS)
    return (not r["is_protected_domain"]) and r["best_match"]["score"] >= 0.80


def test_homoglyph_rn_matches_brand():
    r = analyse_domain("acrnepay-login.com", BRANDS)  # rn looks like m
    assert r["best_match"]["brand"] == "acmepay.com"
    assert r["best_match"]["score"] >= 0.80


def test_protected_domain_not_flagged():
    r = analyse_domain("acmepay.com", BRANDS)
    assert r["is_protected_domain"] is True
    assert lookalike("acmepay.com") is False


def test_brand_plus_keywords():
    r = analyse_domain("acmepay-secure-login.com", BRANDS)
    assert lookalike("acmepay-secure-login.com")
    assert "secure" in r["keywords"] and "login" in r["keywords"]


def test_digit_swap_matches_brand():
    assert lookalike("acmepa1.com")  # 1 looks like l


def test_unrelated_names_not_flagged():
    assert lookalike("acme-weather.com") is False
    assert lookalike("google.com") is False


def test_brand_hidden_in_subdomain():
    r = analyse_domain("acmepay.com.account-check.net", BRANDS)
    assert r["is_protected_domain"] is False
    assert r["brand_in_subdomain"] is True
    assert lookalike("acmepay.com.account-check.net")


def test_cyrillic_homoglyph():
    domain = "\u0430cmepay.com"  # first letter is a Cyrillic 'a'
    r = analyse_domain(domain, BRANDS)
    assert r["is_protected_domain"] is False
    assert r["best_match"]["score"] >= 0.80


def test_punycode_flag():
    r = analyse_domain("xn--80ak6aa92e.com", BRANDS)
    assert r["has_punycode"] is True


def test_case_and_spaces_ignored():
    r = analyse_domain("  ACMEPAY.COM  ", BRANDS)
    assert r["is_protected_domain"] is True


def test_no_brands_gives_no_match():
    r = analyse_domain("example.com", [])
    assert r["best_match"]["brand"] is None
    assert r["best_match"]["score"] == 0.0


def test_keywords_found():
    r = analyse_domain("verify-account-update.com", BRANDS)
    assert {"verify", "account", "update"} <= set(r["keywords"])


def test_short_brand_fragments_not_flagged():
    assert lookalike("pay.com") is False
    assert lookalike("bank.com") is False
    assert lookalike("acmeplumbing.com") is False