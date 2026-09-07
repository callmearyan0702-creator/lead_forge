"""
Shared feature definitions for the lead-scoring model.

Having ONE place that defines the feature list + defaults + human-
readable labels means training and inference can never drift apart
(a classic source of silent bugs in ML services).
"""

# Order matters: this is the exact column order the model is trained on
# and expects at inference time.
FEATURE_COLUMNS = [
    "company_size",
    "annual_revenue",
    "engagement_score",
    "email_opens",
    "website_visits",
    "days_since_last_contact",
    "budget",
]

# Sensible fallback values when a lead is missing a field, chosen to be
# "neutral" (roughly median-ish for synthetic training data) rather than
# zero, so missing data doesn't automatically tank a score.
DEFAULT_VALUES = {
    "company_size": 50,
    "annual_revenue": 1_000_000,
    "engagement_score": 50,
    "email_opens": 3,
    "website_visits": 5,
    "days_since_last_contact": 14,
    "budget": 20_000,
}

# Human-readable labels + short descriptions used when turning SHAP
# values into plain-English explanations.
FEATURE_LABELS = {
    "company_size": "company size",
    "annual_revenue": "annual revenue",
    "engagement_score": "engagement score",
    "email_opens": "email opens",
    "website_visits": "website visits",
    "days_since_last_contact": "days since last contact",
    "budget": "stated budget",
}
