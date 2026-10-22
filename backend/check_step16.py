# check_step16.py
from app.analysis.explain import generate_summary

print("=== STEP 16 VERIFICATION ===\n")

# Simulate the evidence that your Agent (Step 19) will collect
mock_evidence = {
    "domain": {
        "best_match": {"brand": "acmepay.com", "score": 0.92},
        "keywords": ["login", "secure"]
    },
    "whois": {
        "age_days": 2
    },
    "website": {
        "forms": [
            {"hasPassword": True, "posts_to_other_host": True}
        ]
    },
    "vision": {
        "impersonation": True,
        "best_brand_match": "acmepay"
    },
    "nlp": {
        "probability": 0.95
    },
    "url_model": {
        "probability": 0.88
    }
}

summary = generate_summary(mock_evidence)
print("--- Generated Summary ---")
print(summary)
print("-------------------------\n")

# Check if it contains the key facts
assert "acmepay.com" in summary
assert "2 days ago" in summary
assert "password form" in summary
assert "Screenshot visually matches" in summary

print("✅ SUCCESS: Explainability module correctly generated the summary.")

# Test a low-risk case
mock_low = {"domain": {"best_match": {"brand": "google.com", "score": 0.1}}}
summary_low = generate_summary(mock_low)
print("\n--- Low Risk Summary ---")
print(summary_low)

print("\n=== DONE ===")