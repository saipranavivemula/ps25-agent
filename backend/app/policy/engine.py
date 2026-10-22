# app/policy/engine.py

# Group the signals into logical "families" to enforce the 2-family rule
FAMILIES = {
    "domain": {"lookalike_domain", "brand_keywords", "domain_age", "cert_age"},
    "email": {"email_auth", "link_mismatch", "nlp_text"},
    "web": {"password_form", "vision_impersonation"},
    "url": {"url_model"}
}

def decide(score: float, reasons: list[dict], target: str, is_email: bool = False, 
           high_threshold: float = 0.85, medium_threshold: float = 0.70, 
           auto_actions: bool = False, allowlist: set = None) -> dict:
    """
    Evaluates the risk score and determines the policy decision and actions.
    """
    if allowlist is None:
        allowlist = set()

    # 1. Allowlist Check (Highest Priority)
    if target in allowlist:
        return {
            "decision": "low",
            "actions": [],
            "needs_approval": False,
            "why": "Target is explicitly allowlisted."
        }

    # 2. Identify which evidence families triggered
    hit_families = set()
    for r in reasons:
        sig = r["signal"]
        for fam, signals in FAMILIES.items():
            if sig in signals:
                hit_families.add(fam)

    # 3. Determine Decision Level
    if score >= high_threshold:
        if len(hit_families) >= 2:
            level = "high"
        else:
            # Downgrade to medium if only one family of evidence is present
            level = "medium"
            why = f"Score is high ({score}), but only 1 evidence family ({list(hit_families)[0]}). Downgraded to medium."
    elif score >= medium_threshold:
        level = "medium"
        why = f"Score ({score}) crossed medium threshold."
    else:
        level = "low"
        why = f"Score ({score}) is below medium threshold."

    # Overwrite 'why' if we didn't downgrade
    if level == "high":
        why = f"Score ({score}) crossed high threshold with {len(hit_families)} independent evidence families."
    elif level == "low":
        why = f"Score ({score}) is below medium threshold."

    # 4. Determine Actions based on level
    actions = []
    needs_approval = False

    if level == "high":
        actions = ["block_url", "report_registrar", "ticket"]
        if is_email:
            actions.append("quarantine_email")
            
        if not auto_actions:
            needs_approval = True
            
    elif level == "medium":
        actions = ["ticket", "warn_users"]
        if is_email:
            actions.append("quarantine_email")
        # Medium always requires analyst review
        needs_approval = True
        
    else: # Low
        actions = ["monitor"]
        needs_approval = False

    return {
        "decision": level,
        "actions": actions,
        "needs_approval": needs_approval,
        "why": why,
        "families_hit": sorted(list(hit_families))
    }