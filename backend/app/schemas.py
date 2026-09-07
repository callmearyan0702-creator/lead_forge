"""
Pydantic schemas -- the API's public contract.

Kept separate from the ORM models (app/models.py) on purpose: the DB
shape and the API shape are allowed to diverge (e.g. we may want to
rename a field in the API without a migration, or hide internal
columns), and future features like auth-scoped fields are easier to
add here without touching persistence code.
"""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class ExplanationItem(BaseModel):
    feature: str
    impact: float          # signed SHAP contribution
    direction: str          # "increased" | "decreased"
    detail: str              # human-readable sentence


class LeadOut(BaseModel):
    id: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[float] = None
    annual_revenue: Optional[float] = None
    engagement_score: Optional[float] = None
    email_opens: Optional[float] = None
    website_visits: Optional[float] = None
    days_since_last_contact: Optional[float] = None
    budget: Optional[float] = None
    extra_fields: dict[str, Any] = {}
    lead_score: Optional[float] = None
    score_label: Optional[str] = None
    explanation: list[ExplanationItem] = []

    model_config = {"from_attributes": True}


class BatchOut(BaseModel):
    id: str
    filename: str
    row_count: int
    column_mapping: dict[str, str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    batch: BatchOut
    leads: list[LeadOut]
    warnings: list[str] = []


class BatchSummary(BaseModel):
    id: str
    filename: str
    row_count: int
    created_at: datetime
    avg_score: Optional[float] = None
    hot_count: int = 0
    warm_count: int = 0
    cold_count: int = 0
