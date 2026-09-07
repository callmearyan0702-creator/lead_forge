"""
Read/query endpoints for leads and upload batches, plus CSV export.

Filtering/search/sorting all happen in SQL (not in Python after
fetching everything) so this stays reasonably fast as row counts grow
past what fits comfortably in memory -- one of the easy wins for
"structured so it can scale later" without adding new infrastructure.
"""
import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead, UploadBatch
from app.schemas import LeadOut, BatchOut, BatchSummary

router = APIRouter(prefix="/api", tags=["leads"])

SORTABLE_FIELDS = {
    "lead_score": Lead.lead_score,
    "company_name": Lead.company_name,
    "annual_revenue": Lead.annual_revenue,
    "engagement_score": Lead.engagement_score,
    "created_at": Lead.created_at,
}


@router.get("/batches", response_model=list[BatchSummary])
def list_batches(db: Session = Depends(get_db)):
    batches = db.query(UploadBatch).order_by(UploadBatch.created_at.desc()).all()
    summaries = []
    for batch in batches:
        scores = [l.lead_score for l in batch.leads if l.lead_score is not None]
        summaries.append(BatchSummary(
            id=batch.id,
            filename=batch.filename,
            row_count=batch.row_count,
            created_at=batch.created_at,
            avg_score=round(sum(scores) / len(scores), 1) if scores else None,
            hot_count=sum(1 for l in batch.leads if l.score_label == "Hot"),
            warm_count=sum(1 for l in batch.leads if l.score_label == "Warm"),
            cold_count=sum(1 for l in batch.leads if l.score_label == "Cold"),
        ))
    return summaries


@router.get("/batches/{batch_id}", response_model=BatchOut)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(UploadBatch).filter(UploadBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found.")
    return batch


@router.get("/leads", response_model=list[LeadOut])
def list_leads(
    batch_id: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search company, contact, or email"),
    label: Optional[str] = Query(None, description="Filter by Hot / Warm / Cold"),
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    sort_by: str = Query("lead_score", description="lead_score | company_name | annual_revenue | engagement_score | created_at"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(500, le=2000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Lead)

    if batch_id:
        query = query.filter(Lead.batch_id == batch_id)
    if label:
        query = query.filter(Lead.score_label == label)
    if min_score is not None:
        query = query.filter(Lead.lead_score >= min_score)
    if max_score is not None:
        query = query.filter(Lead.lead_score <= max_score)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(
            Lead.company_name.ilike(like),
            Lead.contact_name.ilike(like),
            Lead.email.ilike(like),
        ))

    sort_col = SORTABLE_FIELDS.get(sort_by, Lead.lead_score)
    sort_col = sort_col.desc().nullslast() if sort_dir == "desc" else sort_col.asc().nullslast()
    query = query.order_by(sort_col)

    return query.offset(offset).limit(limit).all()


@router.get("/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return lead


@router.get("/leads-export/csv")
def export_leads_csv(
    batch_id: Optional[str] = None,
    label: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Lead)
    if batch_id:
        query = query.filter(Lead.batch_id == batch_id)
    if label:
        query = query.filter(Lead.score_label == label)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(
            Lead.company_name.ilike(like),
            Lead.contact_name.ilike(like),
            Lead.email.ilike(like),
        ))
    leads = query.order_by(Lead.lead_score.desc()).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "company_name", "contact_name", "email", "industry", "company_size",
        "annual_revenue", "engagement_score", "email_opens", "website_visits",
        "days_since_last_contact", "budget", "lead_score", "score_label",
        "top_reason",
    ])
    for lead in leads:
        top_reason = lead.explanation[0]["detail"] if lead.explanation else ""
        writer.writerow([
            lead.company_name, lead.contact_name, lead.email, lead.industry,
            lead.company_size, lead.annual_revenue, lead.engagement_score,
            lead.email_opens, lead.website_visits, lead.days_since_last_contact,
            lead.budget, lead.lead_score, lead.score_label, top_reason,
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scored_leads.csv"},
    )
