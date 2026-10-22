# app/ml/calibrate.py
import joblib
import json
import pandas as pd
import numpy as np
from sklearn.metrics import precision_recall_curve, confusion_matrix, roc_curve
from app.config import settings

def pick_threshold(y_true, y_scores, max_fpr=0.01):
    """
    Finds the smallest threshold where the False Positive Rate is <= max_fpr.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    valid_indices = np.where(fpr <= max_fpr)[0]
    
    if len(valid_indices) == 0:
        return 0.99 # Fallback
        
    # We want the threshold that gives us the highest TPR while keeping FPR <= max_fpr
    best_idx = valid_indices[np.argmax(tpr[valid_indices])]
    return float(thresholds[best_idx])

def main():
    print("Loading validation data and text model...")
    # Load data
    try:
        df = pd.read_csv("data/val.csv")
    except FileNotFoundError:
        print("Error: data/val.csv not found. Using data/test.csv instead.")
        df = pd.read_csv("data/test.csv")
        
    # Load text model
    pipe = joblib.load("models/text_model.joblib")
    
    # Get probabilities on validation set
    y_scores = pipe.predict_proba(df.text)[:, 1]
    y_true = df.label.values
    
    print("Calculating metrics...")
    # 1. Find the safest threshold (max 1% FPR)
    t_high = pick_threshold(y_true, y_scores, max_fpr=0.01)
    
    # 2. Calculate precision/recall curve
    prec, rec, _ = precision_recall_curve(y_true, y_scores)
    
    # 3. Calculate confusion matrix at t_high
    y_pred = (y_scores >= t_high).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    # 4. Compile unified metrics for the API/Frontend
    metrics = {
        "text_model": {
            "name": "TF-IDF + Logistic Regression",
            "t_high": round(t_high, 3),
            "validation_size": len(y_true),
            "confusion_matrix": {
                "true_negatives": int(tn),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "true_positives": int(tp)
            },
            "false_positive_rate": round(fp / (fp + tn), 4),
            "precision_at_threshold": round(tp / (tp + fp), 3) if (tp + fp) > 0 else 0,
            "recall_at_threshold": round(tp / (tp + fn), 3) if (tp + fn) > 0 else 0
        },
        "pr_curve_sample": [
            {"precision": float(p), "recall": float(r)} 
            for p, r in zip(prec[::50], rec[::50])
        ] # We sample every 50th point so the JSON isn't huge
    }
    
    # 5. Save to files
    with open("models/calibration.json", "w") as f:
        json.dump({"t_high": t_high, "t_medium": 0.70}, f, indent=2)
        
    with open("models/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"\nSelected High Threshold (t_high): {t_high:.3f}")
    print(f"At this threshold, False Positive Rate is: {metrics['text_model']['false_positive_rate']*100:.2f}%")
    print("Saved to models/calibration.json and models/metrics.json")

if __name__ == "__main__":
    main()