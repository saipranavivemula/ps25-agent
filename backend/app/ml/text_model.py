import re

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_PATH = "models/text_model.joblib"
THRESHOLD = 0.5  # placeholder; the real value comes from Step 15
URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.I)
LONG_NUMBER_RE = re.compile(r"\d{4,}")


def clean_text(text: str) -> str:
    """Normalise an email before the model sees it.

    Every link becomes the word 'urltoken' and long numbers become 'numtoken', so the
    model learns from the WORDS around a link (the URL model judges the link itself).
    """
    text = URL_RE.sub(" urltoken ", str(text))
    text = LONG_NUMBER_RE.sub(" numtoken ", text)
    return re.sub(r"\s+", " ", text).lower().strip()


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=clean_text, ngram_range=(1, 2), min_df=2,
                                  max_features=50000, sublinear_tf=True, strip_accents="unicode")),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", C=2.0)),
    ])


_pipe = None


def load_model(path: str = MODEL_PATH):
    """Load the trained model once and keep it in memory."""
    global _pipe
    if _pipe is None:
        _pipe = joblib.load(path)
    return _pipe


def top_terms(text: str, k: int = 8) -> list[dict]:
    """Words that pushed the score towards 'phishing' (used to highlight the email)."""
    pipe = load_model()
    vec, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
    x = vec.transform([text])
    names = np.array(vec.get_feature_names_out())
    contrib = x.multiply(clf.coef_[0]).toarray()[0]
    idx = np.argsort(-contrib)[:k]
    return [{"term": str(names[i]), "weight": round(float(contrib[i]), 4)}
            for i in idx if contrib[i] > 0 and names[i] not in ("urltoken", "numtoken")]


def predict_text(text: str) -> dict:
    """Probability that the email's language is phishing-like, plus the words behind it."""
    if not text or not str(text).strip():
        return {"probability": 0.0, "top_terms": []}
    pipe = load_model()
    prob = float(pipe.predict_proba([text])[0][1])
    return {"probability": round(prob, 4), "top_terms": top_terms(text)}