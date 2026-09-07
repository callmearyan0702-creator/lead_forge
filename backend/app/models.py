"""
ORM models.

Two tables:
- UploadBatch: one row per CSV upload, so results stay grouped and a
  dashboard can filter/compare across uploads.
- Lead: one row per lead in a batch, storing both the original
  (cleaned) fields and the scoring output.

`extra_fields` (JSON) holds whatever columns didn't map to a known lead
attribute, so uploads with unusual schemas don't lose data. This also
means adding a new "known" field later doesn't require a migration to
avoid data loss -- it's already sitting in extra_fields.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class UploadBatch(Base):
    __tablename__ = "upload_batches"

    id = Column(String, primary_key=True, default=_uuid)
    filename = Column(String, nullable=False)
    row_count = Column(Integer, default=0)
    column_mapping = Column(JSON, default=dict)  # detected CSV column -> canonical field
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    leads = relationship("Lead", back_populates="batch", cascade="all, delete-orphan")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=_uuid)
    batch_id = Column(String, ForeignKey("upload_batches.id"), nullable=False)

    # Canonical, cleaned lead fields (all optional -- CSVs are messy).
    company_name = Column(String, nullable=True)
    contact_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    company_size = Column(Float, nullable=True)
    annual_revenue = Column(Float, nullable=True)
    engagement_score = Column(Float, nullable=True)
    email_opens = Column(Float, nullable=True)
    website_visits = Column(Float, nullable=True)
    days_since_last_contact = Column(Float, nullable=True)
    budget = Column(Float, nullable=True)

    # Anything that didn't map to a known field above.
    extra_fields = Column(JSON, default=dict)

    # Scoring output.
    lead_score = Column(Float, nullable=True)          # 0-100
    score_label = Column(String, nullable=True)         # Hot / Warm / Cold
    explanation = Column(JSON, default=list)            # list of {feature, impact, direction}

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    batch = relationship("UploadBatch", back_populates="leads")
