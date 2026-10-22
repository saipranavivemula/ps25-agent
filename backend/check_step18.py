# check_step18.py
from app.policy.engine import decide

print("=== STEP 18 VERIFICATION ===\n")

# Test 1: Allowlisted domain (Even with a high score, it should do nothing)
res1 = decide(score=0.99, reasons=[{"signal": "lookalike_domain"}], target="acmepay.com", allowlist={"acmepay.com"})
print("Test 1 (Allowlist):")
print(f"Decision: {res1['decision']} | Actions: {res1['actions']} | Why: {res1['why']}\n")

# Test 2: High score, but ONLY ONE family of evidence (Should downgrade to MEDIUM)
res2 = decide(score=0.88, reasons=[{"signal": "lookalike_domain"}], target="fake-acmepay.com")
print("Test 2 (High score, 1 family):")
print(f"Decision: {res2['decision']} | Actions: {res2['actions']} | Why: {res2['why']}\n")

# Test 3: High score with TWO families of evidence (Should be HIGH)
res3 = decide(score=0.92, reasons=[{"signal": "lookalike_domain"}, {"signal": "password_form"}], target="fake-acmepay.com")
print("Test 3 (High score, 2 families):")
print(f"Decision: {res3['decision']} | Actions: {res3['actions']} | Needs Approval: {res3['needs_approval']}\n")

# Test 4: Low score
res4 = decide(score=0.30, reasons=[{"signal": "cert_age"}], target="random-site.com")
print("Test 4 (Low score):")
print(f"Decision: {res4['decision']} | Actions: {res4['actions']} | Why: {res4['why']}\n")

# Assertions
assert res1["decision"] == "low"
assert res2["decision"] == "medium"
assert res3["decision"] == "high" and res3["needs_approval"] is True
assert res4["decision"] == "low"

print("✅ SUCCESS: Policy engine correctly enforces allowlists, evidence families, and action gates.")
print("\n=== DONE ===")