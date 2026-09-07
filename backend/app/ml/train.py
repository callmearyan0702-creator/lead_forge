"""
Trains the lead-scoring model on synthetic data and saves it to disk.

Why synthetic data? This is a portfolio MVP with no proprietary CRM
history to train on. Rather than fake having "real" training data, we
generate a synthetic dataset from an explicit, documented rule (see
`_synthesize_conversion_probability`) that encodes reasonable B2B
sales intuition (bigger budget, more engagement, more recent contact,
larger company => more likely to convert). This keeps the project
honest for a resume/interview context: the README states plainly that
the model is trained on synthetic data and describes exactly how, and
outlines how a real deployment would instead train on historical
CRM/won-lost data.

Run with:  python -m app.ml.train
"""
import pathlib

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

from app.ml.features import FEATURE_COLUMNS

MODEL_DIR = pathlib.Path(__file__).parent / "artifacts"
MODEL_PATH = MODEL_DIR / "lead_scorer.json"

RNG = np.random.default_rng(42)
N_SAMPLES = 6000


def _generate_synthetic_leads(n: int) -> pd.DataFrame:
    company_size = RNG.lognormal(mean=3.5, sigma=1.2, size=n).clip(1, 20000)
    annual_revenue = (company_size * RNG.uniform(15000, 60000, size=n)).clip(10000, 5e8)
    engagement_score = RNG.beta(2, 2, size=n) * 100
    email_opens = RNG.poisson(lam=3 + engagement_score / 20, size=n)
    website_visits = RNG.poisson(lam=2 + engagement_score / 15, size=n)
    days_since_last_contact = RNG.exponential(scale=20, size=n).clip(0, 365)
    budget = (annual_revenue * RNG.uniform(0.001, 0.02, size=n)).clip(500, 2e6)

    return pd.DataFrame({
        "company_size": company_size,
        "annual_revenue": annual_revenue,
        "engagement_score": engagement_score,
        "email_opens": email_opens,
        "website_visits": website_visits,
        "days_since_last_contact": days_since_last_contact,
        "budget": budget,
    })


def _synthesize_conversion_probability(df: pd.DataFrame) -> np.ndarray:
    """Ground-truth rule used to label synthetic training data.

    Encodes: more engagement, more recent contact, healthier budget
    relative to company size, and higher email/site activity all push
    conversion probability up. Coefficients are chosen for plausible
    scale, not fit to any real dataset.
    """
    z = (
        0.035 * df["engagement_score"]
        + 0.15 * df["email_opens"]
        + 0.10 * df["website_visits"]
        - 0.02 * df["days_since_last_contact"]
        + 0.0000015 * df["budget"]
        + 0.00002 * df["company_size"]
        - 3.0
    )
    prob = 1 / (1 + np.exp(-z))
    noise = RNG.normal(0, 0.06, size=len(df))
    return np.clip(prob + noise, 0.01, 0.99)


def train_and_save() -> dict:
    df = _generate_synthetic_leads(N_SAMPLES)
    prob = _synthesize_conversion_probability(df)
    label = RNG.binomial(1, prob)

    X = df[FEATURE_COLUMNS]
    X_train, X_test, y_train, y_test = train_test_split(
        X, label, test_size=0.2, random_state=42, stratify=label
    )

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save_model(MODEL_PATH)

    return {"auc": auc, "n_train": len(X_train), "n_test": len(X_test)}


if __name__ == "__main__":
    metrics = train_and_save()
    print(f"Model trained. Test AUC: {metrics['auc']:.3f} "
          f"(train={metrics['n_train']}, test={metrics['n_test']})")
    print(f"Saved to {MODEL_PATH}")
