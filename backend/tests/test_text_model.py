import json
import pathlib

import pandas as pd
import pytest

from app.ml.text_model import predict_text, clean_text

ROOT = pathlib.Path(__file__).resolve().parents[1]
PHISH = ("URGENT: Your account has been suspended. Verify your password immediately "
         "at http://acmepay-secure-login.com or it will be closed.")
LEGIT = ("Hi team, I have attached the minutes from Tuesday's meeting. "
         "Please let me know if I missed anything.")


def test_probability_is_valid():
    assert 0.0 <= predict_text(PHISH)["probability"] <= 1.0


def test_obvious_phishing_is_flagged():
    assert predict_text(PHISH)["probability"] > 0.5


def test_obvious_legit_is_not_flagged():
    assert predict_text(LEGIT)["probability"] < 0.5


def test_same_input_gives_same_output():
    assert predict_text(PHISH) == predict_text(PHISH)


def test_empty_text_does_not_crash():
    assert predict_text("")["probability"] == 0.0
    assert predict_text(None)["probability"] == 0.0


def test_top_terms_come_from_the_text():
    terms = predict_text(PHISH)["top_terms"]
    assert terms, "phishing text should have explainable terms"
    assert all(t["weight"] > 0 for t in terms)
    # bigrams may contain the masking tokens, which are not in the raw text
    words = {w for t in terms for w in t["term"].split()} - {"urltoken", "numtoken"}
    assert all(w in PHISH.lower() for w in words)


def test_metrics_file_is_complete():
    m = json.loads((ROOT / "models" / "text_metrics.json").read_text())
    assert {"validation", "test", "demo_test"} <= m.keys()
    for split in ("validation", "test", "demo_test"):
        assert {"n", "precision", "recall", "f1"} <= m[split].keys()
        assert m[split]["n"] > 0


def test_demo_set_does_not_regress():
    path = ROOT / "data" / "test_demo.csv"
    if not path.exists():
        pytest.skip("data/test_demo.csv missing")
    df = pd.read_csv(path).dropna()
    pred = [predict_text(t)["probability"] >= 0.5 for t in df.text]
    tp = sum(p and l == 1 for p, l in zip(pred, df.label))
    fp = sum(p and l == 0 for p, l in zip(pred, df.label))
    recall = tp / max((df.label == 1).sum(), 1)
    assert recall >= 0.80, f"demo recall fell to {recall:.2f}"
    assert fp == 0, f"{fp} legitimate demo emails flagged"

def test_clean_text_masks_links_and_numbers():
    out = clean_text("Pay at http://evil-site.com now, ref 123456")
    assert "evil" not in out
    assert "urltoken" in out and "numtoken" in out