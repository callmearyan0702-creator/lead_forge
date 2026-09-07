"""
FastAPI application entrypoint.

Kept intentionally thin: app setup + middleware + router registration
only. All logic lives in services/routers so this file stays readable
as the project grows (e.g. adding an auth router later is just one
more `app.include_router(...)` line).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import upload, leads

settings = get_settings()

# Creates tables if they don't exist yet. Fine for an MVP; a real       

# deployment would swap this for Alembic migrations (see README).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Industrial AI Lead Intelligence",
    description="Upload a lead CSV, get ML-scored + explainable leads back.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin_list,https://lead-forge-kwm46p1rf-jinx18.vercel.app],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(leads.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
