# app/analysis/explain.py

def generate_summary(ev: dict) -> str:
    """
    Takes the raw evidence dictionary and generates a human-readable summary.
    """
    parts = []

    # 1. Domain & Brand Impersonation
    domain_ev = ev.get("domain", {})
    best_match = domain_ev.get("best_match", {})
    brand = best_match.get("brand")
    sim = best_match.get("score", 0)
    
    if brand and sim >= 0.80:
        parts.append(f"Domain imitates {brand} ({int(sim*100)}% similarity).")
    elif domain_ev.get("keywords"):
        parts.append(f"Domain contains suspicious keywords: {', '.join(domain_ev['keywords'])}.")

    # 2. Domain Age (WHOIS)
    whois_ev = ev.get("whois", {})
    age = whois_ev.get("age_days")
    if age is not None:
        if age < 30:
            parts.append(f"Registered very recently ({age} days ago).")
        elif age < 90:
            parts.append(f"Registered recently ({age} days ago).")

    # 3. Website/DOM Analysis
    website_ev = ev.get("website", {})
    forms = website_ev.get("forms", [])
    has_pw_form = any(f.get("hasPassword") for f in forms)
    posts_other = any(f.get("posts_to_other_host") for f in forms)
    
    if has_pw_form and posts_other:
        parts.append("Page has a password form that posts to another host.")
    elif has_pw_form:
        parts.append("Page contains a password field.")

    # 4. Vision (Brand Impersonation)
    vision_ev = ev.get("vision", {})
    if vision_ev.get("impersonation"):
        brand_vision = vision_ev.get("best_brand_match", "a protected brand")
        parts.append(f"Screenshot visually matches {brand_vision} login page.")

    # 5. Email Text (NLP)
    nlp_ev = ev.get("nlp", {})
    nlp_prob = nlp_ev.get("probability", 0)
    if nlp_prob >= 0.5:
        parts.append(f"Email text flagged as phishing-like (p={nlp_prob:.2f}).")

    # 6. URL Structure Model
    url_ev = ev.get("url_model", {})
    url_prob = url_ev.get("probability", 0)
    if url_prob >= 0.5:
        parts.append(f"URL structure flagged as malicious (p={url_prob:.2f}).")

    # 7. Fallback if nothing triggered
    if not parts:
        return "No strong malicious signals detected."

    # Join them into a single paragraph
    return " ".join(parts)