"""Train the email-text classifier and measure it honestly."""
import json
import pathlib

import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from app.ml.text_model import MODEL_PATH, build_pipeline


def evaluate(pipe, df: pd.DataFrame, threshold: float = 0.5) -> dict:
    proba = pipe.predict_proba(df["text"])[:, 1]
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(df["label"], pred, labels=[0, 1]).ravel()
    p, r, f, _ = precision_recall_fscore_support(df["label"], pred, average="binary", zero_division=0)
    return {"n": int(len(df)), "precision": round(float(p), 4), "recall": round(float(r), 4),
            "f1": round(float(f), 4), "false_positive_rate": round(float(fp / max(fp + tn, 1)), 4),
            "confusion": [[int(tn), int(fp)], [int(fn), int(tp)]]}


def show(name: str, m: dict) -> None:
    print(f"{name:11} n={m['n']:4}  precision={m['precision']:.3f}  recall={m['recall']:.3f}  "
          f"false-positive-rate={m['false_positive_rate']:.3f}  confusion={m['confusion']}")


def main() -> None:
    train = pd.read_csv("data/train.csv")
    val = pd.read_csv("data/val.csv")
    test = pd.read_csv("data/test.csv")
    demo = pd.read_csv("data/test_demo.csv")

    pipe = build_pipeline()
    pipe.fit(train["text"], train["label"])

    results = {"validation": evaluate(pipe, val), "test": evaluate(pipe, test),
               "demo_test": evaluate(pipe, demo)}
    print("Trained on", len(train), "synthetic emails")
    for name, m in results.items():
        show(name, m)

    demo = demo.assign(prob=pipe.predict_proba(demo["text"])[:, 1])
    wrong = demo[(demo["prob"] >= 0.5).astype(int) != demo["label"]]
    print(f"\nHand-written demo emails the model got wrong: {len(wrong)} of {len(demo)}")
    for _, row in wrong.iterrows():
        kind = "MISSED PHISHING" if row["label"] == 1 else "FALSE ALARM"
        print(f"  {kind:15} p={row['prob']:.2f}  {row['text'][:85]}")

    pathlib.Path("models").mkdir(exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    results["model"] = "tfidf_logreg"
    results["trained_on"] = "synthetic emails (data/train.csv)"
    json.dump(results, open("models/text_metrics.json", "w"), indent=2)
    print("\nsaved", MODEL_PATH, "and models/text_metrics.json")


if __name__ == "__main__":
    main()