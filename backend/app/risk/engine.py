# app/risk/engine.py

def contributions(ev: dict) -> list[dict]:
    """Calculates individual signal contributions based on the evidence dict."""
    out = []
    
    def add(signal, value, cap, detail):
        if value > 0:
            # Apply the cap and round
            val = round(min(value, cap), 3)
            out.append({"signal": signal, "contribution": val, "detail": detail})

    # 1. Domain Lookalike
    d = ev.get("domain", {})
    sim = d.get("best_match", {}).get("score", 0)
    if sim >= 0.80:
        brand = d["best_match"].get("brand", "protected brand")
        add("lookalike_domain", 0.45 * sim, 0.45, f"Imitates {brand}")

    # 2. Brand Keywords
    if d.get("keywords") and sim >= 0.6:
        add("brand_keywords", 0.10, 0.10, "Keywords: " + ", ".join(d["keywords"]))

    # 3. Domain Age (WHOIS)
    w = ev.get("whois", {})
    age = w.get("age_days")
    if age is not None:
        v = 0.0
        if age < 7: v = 0.20
        elif age < 30: v = 0.12
        elif age < 90: v = 0.05
        if v > 0:
            add("domain_age", v, 0.20, f"Registered {age} days ago")

    # 4. Certificate Age
    c = ev.get("cert", {})
    cert_age = c.get("age_days")
    if cert_age is not None and cert_age < 7:
        add("cert_age", 0.05, 0.05, "Certificate issued within 7 days")

    # 5. Email Auth
    em = ev.get("email", {})
    if em:
        fails = [k for k, v in em.get("auth", {}).items() if v in {"fail", "softfail"}]
        v = 0.05 * len(fails) + (0.08 if em.get("reply_to_mismatch") else 0)
        if v > 0:
            fail_str = ", ".join(fails) if fails else "none"
            add("email_auth", v, 0.25, f"Failed SPF/DKIM/DMARC: {fail_str}")

    # 6. Link Mismatch
    if em.get("link_text_mismatch"):
        add("link_mismatch", 0.15, 0.15, "Link text differs from actual href destination")

    # 7. NLP Text Model
    n = ev.get("nlp", {}).get("probability", 0)
    if n >= 0.5:
        add("nlp_text", 0.30 * n, 0.30, f"Phishing-like language (p={n:.2f})")

    # 8. URL Model
    u = ev.get("url_model", {}).get("probability", 0)
    if u >= 0.5:
        add("url_model", 0.25 * u, 0.25, f"Suspicious URL pattern (p={u:.2f})")

    # 9. Website Forms
    ws = ev.get("website", {})
    forms = ws.get("forms", [])
    if any(f.get("hasPassword") and f.get("posts_to_other_host") for f in forms):
        add("password_form", 0.25, 0.25, "Password form posts to another host")

    # 10. Vision Impersonation
    if ev.get("vision", {}).get("impersonation"):
        brand = ev["vision"].get("best_brand_match", "brand")
        add("vision_impersonation", 0.40, 0.40, f"Page looks like {brand}")

    # Sort highest contribution first
    return sorted(out, key=lambda r: -r["contribution"])


def score_case(ev: dict) -> tuple[float, list[dict]]:
    """
    Combines contributions using a Noisy-OR model.
    Returns (final_score, reasons_list)
    """
    reasons = contributions(ev)
    survive = 1.0
    
    # Noisy-OR: 1 - (1 - c1) * (1 - c2) * ...
    for r in reasons:
        survive *= (1 - r["contribution"])
        
    final_score = round(1.0 - survive, 3)
    return final_score, reasons