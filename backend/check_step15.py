# check_step15.py
import json

print("=== STEP 15 VERIFICATION ===\n")

try:
    with open("models/metrics.json", "r") as f:
        metrics = json.load(f)
    with open("models/calibration.json", "r") as f:
        calib = json.load(f)
        
    print("OK: models/metrics.json found.")
    print("OK: models/calibration.json found.\n")
    
    print("--- Text Model Metrics (Validation Set) ---")
    tm = metrics["text_model"]
    print(f"Threshold (t_high): {tm['t_high']}")
    print(f"False Positive Rate: {tm['false_positive_rate'] * 100:.2f}%")
    print(f"Precision at threshold: {tm['precision_at_threshold']}")
    print(f"Recall at threshold:    {tm['recall_at_threshold']}")
    print(f"Confusion Matrix: TN={tm['confusion_matrix']['true_negatives']}, FP={tm['confusion_matrix']['false_positives']}, FN={tm['confusion_matrix']['false_negatives']}, TP={tm['confusion_matrix']['true_positives']}")
    
    print("\n--- PR Curve Sample ---")
    print(f"Contains {len(metrics['pr_curve_sample'])} sampled points for the frontend chart.")
    
    print("\n✅ SUCCESS: Calibration data is ready.")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n=== DONE ===")