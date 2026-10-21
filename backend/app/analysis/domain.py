import tldextract
from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein

# Characters attackers use to imitate other characters
CONFUSABLES = {
    "0": "o", "1": "l", "3": "e", "5": "s",
    "\u0430": "a",  # Cyrillic a
    "\u043e": "o",  # Cyrillic o
    "\u0435": "e",  # Cyrillic e
    "\u0440": "p",  # Cyrillic r (looks like p)
    "\u0441": "c",  # Cyrillic s (looks like c)
}

KEYWORDS = ["login", "secure", "verify", "account", "update",
            "support", "billing", "wallet", "signin"]


def skeleton(label: str) -> str:
    """Reduce a name to its 'look-alike skeleton' so tricks compare equal."""
    s = label.lower()
    s = "".join(CONFUSABLES.get(ch, ch) for ch in s)
    return s.replace("rn", "m").replace("vv", "w")


def _decode_idna(domain: str) -> str:
    """Turn punycode (xn--...) back into real Unicode letters, if possible."""
    try:
        return domain.encode("ascii").decode("idna")
    except Exception:
        return domain

def analyse_domain(domain: str, brands: list[str]) -> dict:
    """Score how strongly `domain` imitates one of the protected brands."""
    domain = domain.strip().lower()
    uni = _decode_idna(domain)
    ext = tldextract.extract(uni)
    label = ext.domain
    full = (ext.subdomain + "." + ext.domain).strip(".")
    label_skel = skeleton(label)
    full_skel = skeleton(full)

    best = {"brand": None, "score": 0.0, "edit_distance": None}
    best_sim = -1.0  # raw 0-100 score, kept separate so scales never mix
    for b in brands:
        b_skel = skeleton(tldextract.extract(b).domain)
        if b_skel and b_skel in full_skel:
            sim = 100.0  # the brand name is inside the domain (e.g. acmepay-login)
        else:
            sim = fuzz.ratio(label_skel, b_skel)  # near-misses such as acmepa1
        if sim > best_sim:
            best_sim = sim
            best = {
                "brand": b,
                "score": round(sim / 100.0, 3),
                "edit_distance": Levenshtein.distance(label_skel, b_skel),
            }

    return {
        "registered_domain": ext.top_domain_under_public_suffix,
        "suffix": ext.suffix,
        "unicode_domain": uni,
        "has_punycode": "xn--" in domain,
        "num_hyphens": domain.count("-"),
        "num_digits": sum(c.isdigit() for c in label),
        "keywords": [k for k in KEYWORDS if k in domain],
        "is_protected_domain": ext.top_domain_under_public_suffix in brands,
        "brand_in_subdomain": any(
            tldextract.extract(b).domain in ext.subdomain for b in brands
        ),
        "best_match": best,
    }