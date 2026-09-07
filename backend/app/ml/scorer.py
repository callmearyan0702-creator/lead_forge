"""
Inference-time scoring + explainability.

Loads the trained XGBoost model once (module-level singleton) and
exposes `score_leads(df) -> (scores, labels, explanations)`.

Explanations come from SHAP's TreeExplainer, which is exact and fast
for tree models (no sampling/approximation needed, unlike model-
agnostic SHAP methods). For each lead we surface the top 3 features by
|impact| and phrase them in plain English so the dashboard can show
"why" a lead scored the way it did without the user needing to know
what SHAP is.
"""
import pathlib

import numpy as np
import pandas as pd
import shap
import xgboost as xgb

from app.ml.features import FEATURE_COLUMNS, DEFAULT_VALUES, FEATURE_LABELS

MODEL_PATH = pathlib.Path(__file__).parent / "artifacts" / "lead_scorer.json"

_model: xgb.XGBClassifier | None = None
_explainer: shap.TreeExplainer | None = None


def _load():
    global _model, _explainer
    if _model is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(
                "Model artifact not found. Run `python -m app.ml.train` "
                "from the backend directory first."
            )
        _model = xgb.XGBClassifier()
        _model.load_model(MODEL_PATH)
        _explainer = shap.TreeExplainer(_model)
    return _model, _explainer


def _prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values with neutral defaults and enforce column order."""
    features = pd.DataFrame(index=df.index)
    for col in FEATURE_COLUMNS:
        if col in df.columns:
            features[col] = pd.to_numeric(df[col], errors="coerce").fillna(DEFAULT_VALUES[col])
        else:
            features[col] = DEFAULT_VALUES[col]
    return features[FEATURE_COLUMNS].astype(float)


def _label_for_score(score: float) -> str:
    if score >= 70:
        return "Hot"
    if score >= 40:
        return "Warm"
    return "Cold"


def _explain_row(shap_values_row: np.ndarray, feature_values: pd.Series, top_n: int = 3) -> list[dict]:
    """Turn one row of SHAP values into ranked, human-readable explanations."""
    order = np.argsort(-np.abs(shap_values_row))[:top_n]
    explanations = []
    for idx in order:
        feature = FEATURE_COLUMNS[idx]
        impact = float(shap_values_row[idx])
        value = feature_values[feature]
        direction = "increased" if impact > 0 else "decreased"
        label = FEATURE_LABELS[feature]

        if feature == "days_since_last_contact":
            detail = f"Last contact was {value:.0f} days ago, which {direction} the score."
        elif feature in {"annual_revenue", "budget"}:
            detail = f"{label.capitalize()} of ${value:,.0f} {direction} the score."
        else:
            detail = f"{label.capitalize()} of {value:,.0f} {direction} the score."

        explanations.append({
            "feature": feature,
            "impact": round(impact, 4),
            "direction": direction,
            "detail": detail,
        })
    return explanations


def score_leads(df: pd.DataFrame) -> tuple[list[float], list[str], list[list[dict]]]:
    """Score a dataframe of leads.

    Returns three parallel lists (one entry per row): 0-100 scores,
    Hot/Warm/Cold labels, and per-lead explanation lists.
    """
    if df.empty:
        return [], [], []

    model, explainer = _load()
    features = _prepare_features(df)

    probabilities = model.predict_proba(features)[:, 1]
    scores = [round(float(p) * 100, 1) for p in probabilities]
    labels = [_label_for_score(s) for s in scores]

    shap_values = explainer.shap_values(features)
    explanations = [
        _explain_row(shap_values[i], features.iloc[i])
        for i in range(len(features))
    ]

    return scores, labels, explanations
