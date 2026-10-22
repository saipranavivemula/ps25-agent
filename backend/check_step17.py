# check_step17.py
from app.risk.engine import score_case

print("=== STEP 17 VERIFICATION ===\n")

# Test 1: Single weak signal should stay low
ev_weak = {"cert": {"age_days": 1}}
score_weak, reasons_weak = score_case(ev_weak)
print(f"Test 1 (Weak signal): Score = {score_weak} (Expected < 0.1)")
print(f"Reasons: {reasons_weak}\n")

# Test 2: Empty evidence should be 0.0
score_empty, _ = score_case({})
print(f"Test 2 (No signals): Score = {score_empty} (Expected 0.0)\n")

# Test 3: A full-blown phishing attack (Should be very high)
ev_strong = {
    "domain": {"best_match": {"score": 0.90, "brand": "acmepay.com"}, "keywords": ["login", "secure"]},
    "whois": {"age_days": 2},
    "website": {"forms": [{"hasPassword": True, "posts_to_other_host": True}]},
    "vision": {"impersonation": True, "best_brand_match": "acmepay"},
    "nlp": {"probability": 0.95},
    "url_model": {"probability": 0.88}
}
score_strong, reasons_strong = score_case(ev_strong)
print(f"Test 3 (Strong signals): Score = {score_strong} (Expected > 0.80)")
print("Top Reasons:")
for r in reasons_strong:
    print(f" - {r['signal']}: +{r['contribution']} ({r['detail']})")

assert score_weak < 0.1
assert score_empty == 0.0
assert score_strong > 0.80

print("\n✅ SUCCESS: Risk Engine math is correct.")
print("\n=== DONE ===")