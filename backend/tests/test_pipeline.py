"""
Basic tests covering the parts most likely to break silently:
column detection, cleaning edge cases, and the upload -> score ->
query -> export flow through the actual API.

Run with:  pytest  (from the backend/ directory)
"""
import io
import os
import tempfile

_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_db.name}")

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.services.data_cleaning import detect_columns, clean_dataframe


def test_detect_columns_common_variants():
    columns = ["Company Name", "Contact Full Name", "email", "# of Employees", "Deal Size"]
    mapping = detect_columns(columns)
    assert mapping["Company Name"] == "company_name"
    assert mapping["email"] == "email"
    assert mapping["Deal Size"] == "budget"


def test_clean_dataframe_drops_empty_and_duplicate_rows():
    df = pd.DataFrame({
        "Company": ["Acme", "Acme", "Empty Co"],
        "Revenue": ["$1,000,000", "$1,000,000", ""],
    })
    result = clean_dataframe(df)
    # duplicate removed, empty-signal row dropped -> 1 row left
    assert len(result.dataframe) == 1
    assert result.dataframe.iloc[0]["company_name"] == "Acme"


@pytest.fixture()
def client():
    from app.main import app
    return TestClient(app)


def test_upload_and_query_flow(client):
    csv_content = (
        "Company,Contact,Email,Engagement Score,Budget,Days Since Last Contact\n"
        "Acme,Jane,jane@acme.com,90,50000,1\n"
        "Cold Co,Bob,bob@cold.com,5,500,200\n"
    )
    resp = client.post(
        "/api/upload",
        files={"file": ("leads.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["batch"]["row_count"] == 2
    scores = {l["company_name"]: l["lead_score"] for l in body["leads"]}
    assert scores["Acme"] > scores["Cold Co"]

    list_resp = client.get("/api/leads")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2

    export_resp = client.get("/api/leads-export/csv")
    assert export_resp.status_code == 200
    assert "lead_score" in export_resp.text
