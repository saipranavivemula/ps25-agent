# app/ml/url_model.py
import math
import re
import tldextract
from collections import Counter
from urllib.parse import urlparse
import joblib
import pandas as pd

def entropy(s: str) -> float:
    if not s:
        return 0.0
    c = Counter(s)
    n = len(s)
    return -sum(v / n * math.log2(v / n) for v in c.values())

def url_features(url: str) -> dict:
    # Ensure URL has a scheme for parsing
    if "://" not in url:
        url = "http://" + url
        
    u = urlparse(url)
    ext = tldextract.extract(u.netloc)
    host = u.netloc.lower()
    
    return {
        "url_len": len(url),
        "host_len": len(host),
        "num_dots": host.count("."),
        "num_hyphens": host.count("-"),
        "num_digits": sum(ch.isdigit() for ch in host),
        "num_subdomains": len([s for s in ext.subdomain.split(".") if s]),
        "has_at": int("@" in url),
        "has_ip_host": int(bool(re.fullmatch(r"[\d.]+", ext.domain))),
        "is_https": int(u.scheme == "https"),
        "path_len": len(u.path),
        "num_params": len(u.query.split("&")) if u.query else 0,
        "host_entropy": entropy(ext.domain),
        "tld_len": len(ext.suffix),
        "has_punycode": int("xn--" in host),
        "keyword_hits": sum(
            k in url.lower() for k in ["login", "secure", "verify", "update", "account"]
        )
    }

# --- Inference helper (used later in Step 19) ---
_loaded_model = None

def load_url_model():
    global _loaded_model
    if _loaded_model is None:
        try:
            _loaded_model = joblib.load("models/url_model.joblib")
        except FileNotFoundError:
            raise FileNotFoundError("URL model not found. Run 'python -m app.ml.train_url' first.")
    return _loaded_model

def predict_url(url: str) -> dict:
    bundle = load_url_model()
    clf = bundle["model"]
    cols = bundle["columns"]
    
    feats = url_features(url)
    X = pd.DataFrame([feats])[cols]
    
    prob = float(clf.predict_proba(X)[0][1])
    
    # Get top 3 features driving the decision
    importances = sorted(zip(cols, clf.feature_importances_), key=lambda x: -x[1])[:3]
    top_features = [{"feature": k, "importance": float(v)} for k, v in importances]
    
    return {"probability": prob, "top_features": top_features}