# check_step13.py
import json
from app.ml.url_model import predict_url

print("=== STEP 13 VERIFICATION ===\n")

# 1. Load metrics
try:
    m = json.load(open("models/url_metrics.json"))
    print(f"OK: URL Model loaded. F1: {m['f1']:.3f}")
except Exception as e:
    print("FAIL: Could not load metrics", e)

# 2. Test predictions
tests = [
    ("https://github.com/explore", "legit"),
    ("https://google.com", "legit"),
    ("http://acmepay-secure-login.com/verify?id=123", "phishing"),
    ("http://apple-id-locked.co/update", "phishing"),
]

print("\n--- Predictions ---")
for url, label in tests:
    res = predict_url(url)
    prob = res['probability']
    print(f"[{label:8s}] p={prob:.3f} | {url}")

print("\n=== DONE ===")