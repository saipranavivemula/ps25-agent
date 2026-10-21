import re
import sys

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from .text_model import load_model, predict_text, THRESHOLD

SAMPLES = [
    "URGENT: Your AcmePay account has been suspended. Verify your password now at http://acmepay-secure-login.com or it will be closed.",
    "Hi team, attaching the minutes from Tuesday's meeting. Let me know if I missed anything.",
    "Your invoice is overdue and legal action will begin tomorrow. Download the invoice from the link below.",
    "Your AcmePay statement for October is ready. Log in to the app to view it.",
]
SKIP = {"urltoken", "numtoken"}


def highlight(text: str, terms: list[dict]) -> str:
        words = {w.lower() for t in terms for w in t["term"].split()} - SKIP - ENGLISH_STOP_WORDS
        return re.sub(r"\w+",
                  lambda m: f"[[{m.group(0)}]]" if m.group(0).lower() in words else m.group(0),
                  text)


def show(text: str) -> None:
    r = predict_text(text)
    verdict = "PHISHING" if r["probability"] >= THRESHOLD else "LEGIT"
    print("-" * 70)
    print(f"p(phishing) = {r['probability']:.2f}   threshold = {THRESHOLD}   ->  {verdict}")
    print("top terms   :", ", ".join(f"{t['term']} ({t['weight']:.2f})" for t in r["top_terms"]) or "(none)")
    print("highlighted :", highlight(text, r["top_terms"]))


def show_features(n: int = 15) -> None:
    pipe = load_model()
    names = np.array(pipe.named_steps["tfidf"].get_feature_names_out())
    coef = pipe.named_steps["clf"].coef_[0]
    order = np.argsort(coef)
    print("Strongest PHISHING features:", ", ".join(names[order[::-1][:n]]))
    print("Strongest LEGIT features   :", ", ".join(names[order[:n]]))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--features"]:
        show_features()
    elif args == ["-i"]:
        print("Paste an email on ONE line, press Enter. Empty line quits.")
        while (line := input("\n> ").strip()):
            show(line)
    elif args:
        show(" ".join(args))
    else:
        for s in SAMPLES:
            show(s)