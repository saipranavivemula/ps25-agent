"""Split data/emails.csv into train / validation / test files (70 / 15 / 15)."""
import pathlib

import pandas as pd
from sklearn.model_selection import train_test_split


def main(src: str = "data/emails.csv", seed: int = 42) -> None:
    df = pd.read_csv(src).dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(int)
    df["_key"] = df["text"].str.lower().str.strip()
    df = df.drop_duplicates("_key")

    train, rest = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=seed)
    val, test = train_test_split(rest, test_size=0.50, stratify=rest["label"], random_state=seed)

    out = pathlib.Path("data")
    cols = [c for c in ("text", "label", "kind", "source") if c in df.columns]
    for name, part in (("train", train), ("val", val), ("test", test)):
        part[cols].to_csv(out / f"{name}.csv", index=False)
        print(f"{name:5} rows={len(part):5} phishing={int(part.label.sum()):5} "
              f"legitimate={int((part.label == 0).sum()):5}")

    # safety check: no email may appear in two different splits
    keys = [set(p["_key"]) for p in (train, val, test)]
    shared = len(keys[0] & keys[1]) + len(keys[0] & keys[2]) + len(keys[1] & keys[2])
    print("emails shared between splits:", shared)


if __name__ == "__main__":
    main()