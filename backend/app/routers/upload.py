"""
CSV upload endpoint.

Flow: read CSV -> detect + clean columns -> score with the ML model ->
persist batch + leads -> return everything to the client in one
response so the dashboard can render immediately without a second
round trip.
"""
import io

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import UploadBatch, Lead
from app.schemas import UploadResponse
from app.services.data_cleaning import clean_dataframe
from app.ml.scorer import score_leads

router = APIRouter(prefix="/api/upload", tags=["upload"])
settings = get_settings()


@router.post("", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    raw_bytes = await file.read()
    if len(raw_bytes) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.max_upload_mb}MB limit.")

    try:
        df = pd.read_csv(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="The uploaded CSV has no rows.")

    if len(df) > settings.max_upload_rows:
        raise HTTPException(
            status_code=400,
            detail=f"CSV has {len(df)} rows, which exceeds the {settings.max_upload_rows} row limit.",
        )

    result = clean_dataframe(df)
    cleaned = result.dataframe

    if cleaned.empty:
        raise HTTPException(
            status_code=422,
            detail="No usable rows remained after cleaning. Check that the CSV has recognizable lead data.",
        )

    scores, labels, explanations = score_leads(cleaned)

    batch = UploadBatch(
        filename=file.filename,
        row_count=len(cleaned),
        column_mapping=result.column_mapping,
    )
    db.add(batch)
    db.flush()  # assigns batch.id without committing yet

    leads = []
    for i, row in cleaned.iterrows():
        lead = Lead(
            batch_id=batch.id,
            company_name=row.get("company_name"),
            contact_name=row.get("contact_name"),
            email=row.get("email"),
            industry=row.get("industry"),
            company_size=_none_if_nan(row.get("company_size")),
            annual_revenue=_none_if_nan(row.get("annual_revenue")),
            engagement_score=_none_if_nan(row.get("engagement_score")),
            email_opens=_none_if_nan(row.get("email_opens")),
            website_visits=_none_if_nan(row.get("website_visits")),
            days_since_last_contact=_none_if_nan(row.get("days_since_last_contact")),
            budget=_none_if_nan(row.get("budget")),
            extra_fields=row.get("extra_fields") or {},
            lead_score=scores[i],
            score_label=labels[i],
            explanation=explanations[i],
        )
        db.add(lead)
        leads.append(lead)

    db.commit()
    for lead in leads:
        db.refresh(lead)
    db.refresh(batch)

    return UploadResponse(batch=batch, leads=leads, warnings=result.warnings)


def _none_if_nan(value):
    try:
        if value is None or pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return float(value)
