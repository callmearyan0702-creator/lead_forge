"""
CSV column detection + cleaning.

Real-world lead CSVs never use the same column names twice ("Company"
vs "company_name" vs "Account"). This module maps common variants onto
a small set of canonical fields using fuzzy, case-insensitive keyword
matching, then cleans/coerces the resulting columns.

Design note: detection is intentionally simple (substring/alias
matching) rather than an ML classifier. For a resume-scale MVP this is
easier to reason about, easier to test, and easy to extend by just
adding aliases -- a good tradeoff to call out in an interview.
"""
import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# Canonical field -> list of column-name substrings that should map to it.
# Checked in order; first match wins. Keep aliases lowercase.
FIELD_ALIASES: dict[str, list[str]] = {
    "company_name": ["company name", "company", "account name", "account", "organization", "business name"],
    "contact_name": ["contact name", "full name", "lead name", "name"],
    "email": ["email"],
    "industry": ["industry", "sector", "vertical"],
    "company_size": ["company size", "employees", "headcount", "num employees", "team size"],
    "annual_revenue": ["annual revenue", "revenue", "company revenue"],
    "engagement_score": ["engagement score", "engagement"],
    "email_opens": ["email opens", "opens", "emails opened"],
    "website_visits": ["website visits", "site visits", "page views", "visits"],
    "days_since_last_contact": ["days since last contact", "last contact", "days since contact"],
    "budget": ["budget", "deal size", "opportunity value", "estimated budget"],
}

NUMERIC_FIELDS = {
    "company_size", "annual_revenue", "engagement_score", "email_opens",
    "website_visits", "days_since_last_contact", "budget",
}

TEXT_FIELDS = {"company_name", "contact_name", "email", "industry"}


@dataclass
class CleaningResult:
    dataframe: pd.DataFrame
    column_mapping: dict[str, str]         # original column -> canonical field
    warnings: list[str] = field(default_factory=list)


def _normalize(col: str) -> str:
    return re.sub(r"[_\-]+", " ", col.strip().lower())


def detect_columns(raw_columns: list[str]) -> dict[str, str]:
    """Map original CSV column names to canonical field names.

    Returns {original_column_name: canonical_field}. Columns with no
    confident match are simply absent from the mapping (they end up in
    extra_fields downstream, nothing is silently dropped).
    """
    mapping: dict[str, str] = {}
    used_fields: set[str] = set()

    for col in raw_columns:
        normalized = _normalize(col)
        for canonical, aliases in FIELD_ALIASES.items():
            if canonical in used_fields:
                continue
            if any(alias in normalized for alias in aliases):
                mapping[col] = canonical
                used_fields.add(canonical)
                break
    return mapping


def _coerce_numeric(series: pd.Series) -> pd.Series:
    """Strip common junk ($, commas, %, whitespace) and coerce to float."""
    cleaned = (
        series.astype(str)
        .str.replace(r"[\$,%]", "", regex=True)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "None": np.nan, "N/A": np.nan, "n/a": np.nan})
    )
    return pd.to_numeric(cleaned, errors="coerce")


def clean_dataframe(df: pd.DataFrame) -> CleaningResult:
    """Detect columns, coerce types, and drop unusable rows.

    Rows missing every meaningful signal (all numeric fields empty) are
    dropped rather than scored, since a score would be meaningless
    (and misleadingly precise) without any input signal.
    """
    warnings: list[str] = []
    mapping = detect_columns(list(df.columns))

    if not mapping:
        warnings.append(
            "No recognizable lead columns were detected. All columns were "
            "kept as extra fields; scoring will rely on default values."
        )

    cleaned = pd.DataFrame(index=df.index)

    for original_col, canonical in mapping.items():
        series = df[original_col]
        if canonical in NUMERIC_FIELDS:
            cleaned[canonical] = _coerce_numeric(series)
        else:
            cleaned[canonical] = series.astype(str).str.strip().replace({"nan": None, "": None})

    # Ensure every canonical column exists even if not present in the CSV,
    # so downstream code (scoring/schemas) never has to special-case
    # missing columns.
    for canonical in FIELD_ALIASES:
        if canonical not in cleaned.columns:
            cleaned[canonical] = np.nan if canonical in NUMERIC_FIELDS else None

    # Deduplicate exact-duplicate rows (common in exported CRM lists).
    before = len(cleaned)
    cleaned = cleaned.drop_duplicates()
    if before != len(cleaned):
        warnings.append(f"Removed {before - len(cleaned)} duplicate row(s).")

    # Drop rows with zero numeric signal -- nothing for the model to score.
    numeric_cols = [c for c in NUMERIC_FIELDS if c in cleaned.columns]
    has_signal = cleaned[numeric_cols].notna().any(axis=1) if numeric_cols else pd.Series(True, index=cleaned.index)
    dropped = int((~has_signal).sum())
    if dropped:
        warnings.append(f"Skipped {dropped} row(s) with no usable numeric data.")
    cleaned = cleaned[has_signal]

    # Preserve any unmapped original columns as extra_fields (JSON per row),
    # using the still-aligned index before we reset it below.
    unmapped_cols = [c for c in df.columns if c not in mapping]
    if unmapped_cols:
        extras = df.loc[cleaned.index, unmapped_cols]
        cleaned["extra_fields"] = extras.apply(lambda row: row.dropna().astype(str).to_dict(), axis=1)
    else:
        cleaned["extra_fields"] = [{} for _ in range(len(cleaned))]

    cleaned = cleaned.reset_index(drop=True)

    return CleaningResult(dataframe=cleaned, column_mapping=mapping, warnings=warnings)
