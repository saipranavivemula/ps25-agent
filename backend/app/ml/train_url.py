# app/ml/train_url.py
import joblib
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
from app.ml.url_model import url_features

def main():
    print("Loading data/urls.csv...")
    df = pd.read_csv("data/urls.csv")
    
    print("Extracting features...")
    X = pd.DataFrame([url_features(u) for u in df.url])
    y = df.label

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print("Training Random Forest...")
    clf = RandomForestClassifier(
        n_estimators=100,
        min_samples_leaf=2,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    clf.fit(X_tr, y_tr)

    proba = clf.predict_proba(X_te)[:, 1]
    p, r, f, _ = precision_recall_fscore_support(y_te, proba > 0.5, average="binary")

    print(f"Metrics on Test Set: Precision={p:.3f}, Recall={r:.3f}, F1={f:.3f}")
    
    # Save model
    joblib.dump({"model": clf, "columns": list(X.columns)}, "models/url_model.joblib")
    
    # Save metrics
    metrics = {
        "model": "random_forest",
        "precision": p,
        "recall": r,
        "f1": f,
        "auc": roc_auc_score(y_te, proba),
        "n_test": len(y_te)
    }
    with open("models/url_metrics.json", "w") as f_out:
        json.dump(metrics, f_out, indent=2)
        
    print("Saved model to models/url_model.joblib")
    print("Saved metrics to models/url_metrics.json")

if __name__ == "__main__":
    main()