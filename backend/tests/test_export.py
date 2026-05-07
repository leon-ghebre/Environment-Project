"""
test_export.py

Unit tests for GET /export endpoint.
Tests that filtered water quality readings are returned as a downloadable CSV
"""

from datetime import datetime

import pytest
from app import app
from config import EXPORT_COLUMNS
from database.database import Base, SessionLocal, engine
from database.models import Site, WaterReading


@pytest.fixture
def client():
    """Creates a test Flask client with a fresh test database."""
    app.config["TESTING"] = True
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # add the sites
    site = Site(
        site_code="site_test",
        name="Test Site",
        description="Test site description",
        is_active=True,
    )

    empty_site = Site(
        site_code="site_empty",
        name="Empty Site",
        description="Valid site with no readings",
        is_active=True,
    )

    db.add(site)
    db.add(empty_site)
    db.commit()
    db.refresh(site)

    # add the water readings
    reading_one = WaterReading(
        site_id=site.id,
        recorded_at=datetime(2026, 5, 5, 10, 0, 0),
        ph=7.0,
        turbidity_ntu=3.5,
        conductivity_uS_cm=250.0,
        water_temperature_c=18.0,
        water_level_cm=70.0,
        status="normal",
        alert_triggered=False,
        sensor_fault=False,
        fault_reason=None,
    )

    reading_two = WaterReading(
        site_id=site.id,
        recorded_at=datetime(2026, 5, 6, 10, 0, 0),
        ph=7.4,
        turbidity_ntu=6.5,
        conductivity_uS_cm=300.0,
        water_temperature_c=19.0,
        water_level_cm=72.0,
        status="warning",
        alert_triggered=True,
        sensor_fault=False,
        fault_reason=None,
    )

    db.add(reading_one)
    db.add(reading_two)
    db.commit()
    db.close()

    with app.test_client() as client:
        yield client

    Base.metadata.drop_all(bind=engine)


def test_export_returns_200(client):
    """GET /export should return HTTP 200 for a valid site with readings"""
    response = client.get("/export?site_code=site_test")
    assert response.status_code == 200


def test_export_returns_csv_content_type(client):
    """GET /export should return CSV content"""
    response = client.get("/export?site_code=site_test")
    assert "text/csv" in response.content_type


def test_export_returns_attachment_filename(client):
    """GET /export should return a downloadable CSV filename"""
    response = client.get("/export?site_code=site_test")
    content_disposition = response.headers["Content-Disposition"]

    assert "attachment" in content_disposition
    assert "water_quality_site_test.csv" in content_disposition


def test_export_returns_csv_header(client):
    """GET /export should return CSV headers matching EXPORT_COLUMNS."""
    response = client.get("/export?site_code=site_test")
    csv_text = response.data.decode()
    header = csv_text.splitlines()[0]

    assert header == ",".join(EXPORT_COLUMNS)


def test_export_returns_csv_rows(client):
    """GET /export should return CSV rows for matching readings"""
    response = client.get("/export?site_code=site_test")
    csv_text = response.data.decode()
    rows = csv_text.splitlines()

    assert len(rows) == 3  # header + 2 readings


def test_export_orders_rows_by_timestamp_ascending(client):
    """GET /export should return readings oldest first"""
    response = client.get("/export?site_code=site_test")
    csv_text = response.data.decode()

    assert csv_text.index("2026-05-05T10:00:00") < csv_text.index("2026-05-06T10:00:00")


def test_export_filters_by_start_date(client):
    """GET /export should filter readings by start date"""
    response = client.get("/export?site_code=site_test&start=2026-05-06")
    csv_text = response.data.decode()

    assert response.status_code == 200
    assert "2026-05-06T10:00:00" in csv_text
    assert "2026-05-05T10:00:00" not in csv_text


def test_export_filters_by_end_date(client):
    """GET /export should filter readings by end date"""
    response = client.get("/export?site_code=site_test&end=2026-05-06")
    csv_text = response.data.decode()

    assert response.status_code == 200
    assert "2026-05-05T10:00:00" in csv_text
    assert "2026-05-06T10:00:00" not in csv_text

    # note in this implementation, end date is at midnight


def test_export_filename_includes_date_filters(client):
    """GET /export filename should include selected date filters"""
    response = client.get("/export?site_code=site_test&start=2026-05-05&end=2026-05-06")
    content_disposition = response.headers["Content-Disposition"]

    assert "water_quality_site_test_2026-05-05_to_2026-05-06.csv" in content_disposition


def test_export_missing_site_code_returns_400(client):
    """GET /export without site_code should return HTTP 400"""
    response = client.get("/export")

    assert response.status_code == 400
    assert response.get_json()["error"] == "site_code is required"


def test_export_invalid_start_date_returns_400(client):
    """GET /export with invalid start date should return HTTP 400"""
    response = client.get("/export?site_code=site_test&start=invalid-date")

    assert response.status_code == 400
    assert response.get_json()["error"] == "start must be YYYY-MM-DD"


def test_export_invalid_end_date_returns_400(client):
    """GET /export with invalid end date should return HTTP 400"""
    response = client.get("/export?site_code=site_test&end=invalid-date")

    assert response.status_code == 400
    assert response.get_json()["error"] == "end must be YYYY-MM-DD"


def test_export_no_data_returns_404(client):
    """GET /export should return HTTP 404 when no readings match filter"""
    response = client.get("/export?site_code=site_empty")

    assert response.status_code == 404
    assert response.get_json()["error"] == "no data found for selected filters"
