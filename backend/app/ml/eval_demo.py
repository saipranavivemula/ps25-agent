import sys
import pandas as pd
from .text_model import predict_text

path = sys.argv[1] if len(sys.argv) > 1 else "data/test_demo.csv"
df = pd.read_csv(path).dropna()


df["p"] = [predict_text(t)["probability"] for t in df.text]
df = df.sort_values("p", ascending=False)

print(f"{'label':>5} {'p':>5}  text")
for _, r in df.iterrows():
    flag = ""
    if r.label == 1 and r.p < 0.5: flag = "  <-- MISSED"
    if r.label == 0 and r.p >= 0.5: flag = "  <-- FALSE ALARM"
    print(f"{int(r.label):>5} {r.p:5.2f}  {r.text[:70]}{flag}")

print("\nThreshold trade-off on the demo set (for understanding only, do NOT pick your final threshold here):")
for t in (0.3, 0.4, 0.5, 0.6):
    pred = df.p >= t
    tp = int((pred & (df.label == 1)).sum()); fp = int((pred & (df.label == 0)).sum())
    fn = int((~pred & (df.label == 1)).sum())
    print(f"  t={t:.1f}  precision={tp/max(tp+fp,1):.2f}  recall={tp/max(tp+fn,1):.2f}  false_alarms={fp}")