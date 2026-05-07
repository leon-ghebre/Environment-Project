"""
test_alerts.py

Unit tests for GET /alerts endpoint
Tests that alert events are returned and filtered correctly
"""

from datetime import datetime

import pytest
from app import app
from database.database import Base, SessionLocal, engine
from database.models import Alert, Site, WaterReading


@pytest.fixture
def client():
    """Creates a test Flask client with a fresh test database."""
    app.config["TESTING"] = True
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # adding the test sites
    site = Site(
        site_code="site_test",
        name="Test Site",
        description="Test site description",
        is_active=True,
    )
    other_site = Site(
        site_code="site_other",
        name="Other Site",
        description="Other test site",
        is_active=True,
    )

    db.add(site)
    db.add(other_site)
    db.commit()
    db.refresh(site)
    db.refresh(other_site)

    # adding the readings
    reading = WaterReading(
        site_id=site.id,
        recorded_at=datetime(2023, 1, 1, 10, 0, 0),
        ph=7.0,
        turbidity_ntu=8.5,
        conductivity_uS_cm=300.0,
        water_temperature_c=18.0,
        water_level_cm=70.0,
        status="warning",
        alert_triggered=True,
        sensor_fault=False,
        fault_reason=None,
    )

    critical_reading = WaterReading(
        site_id=other_site.id,
        recorded_at=datetime(2023, 1, 2, 10, 0, 0),
        ph=5.8,
        turbidity_ntu=12.0,
        conductivity_uS_cm=1600.0,
        water_temperature_c=19.0,
        water_level_cm=72.0,
        status="critical",
        alert_triggered=True,
        sensor_fault=False,
        fault_reason=None,
    )

    db.add(reading)
    db.add(critical_reading)
    db.commit()
    db.refresh(reading)
    db.refresh(critical_reading)

    # adding the alerts
    warning_alert = Alert(
        site_id=site.id,
        source_reading_id=reading.id,
        started_at=datetime(2026, 5, 6, 10, 0, 0),
        alert_type="turbidity",
        severity="warning",
        message="Turbidity warning detected",
    )

    critical_alert = Alert(
        site_id=other_site.id,
        source_reading_id=critical_reading.id,
        started_at=datetime(2026, 5, 5, 10, 0, 0),
        alert_type="conductivity",
        severity="critical",
        message="Conductivity critical alert detected",
    )

    db.add(warning_alert)
    db.add(critical_alert)
    db.commit()
    db.close()

    with app.test_client() as client:
        yield client

    Base.metadata.drop_all(bind=engine)


def test_alerts_returns_200(client):
    """GET /alerts should return HTTP 200."""
    response = client.get("/alerts")
    assert response.status_code == 200


def test_alerts_returns_list(client):
    """GET /alerts should return a JSON list."""
    response = client.get("/alerts")
    data = response.get_json()
    assert isinstance(data, list)


def test_alerts_returns_required_fields(client):
    """GET /alerts should retunr the expected alert fields."""
    response = client.get("/alerts")
    data = response.get_json()

    required_fields = [
        "site_code",
        "site_name",
        "timestamp",
        "alert_type",
        "severity",
        "message",
        "value",
        "unit",
        "source_reading_id",
    ]

    for field in required_fields:
        assert field in data[0], f"Missing field: {field}"


def test_alerts_returns_alerts_newest_first(client):
    """GET /alerts should return alerts ordered by newest first"""
    response = client.get("/alerts")
    data = response.get_json()

    assert data[0]["timestamp"] == "2026-05-06T10:00:00"
    assert data[1]["timestamp"] == "2026-05-05T10:00:00"


def test_alerts_filters_by_site_code(client):
    """GET /alerts should filter alerts by site_code"""
    response = client.get("/alerts?site_code=site_test")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["site_code"] == "site_test"


def test_alerts_invalid_site_code_returns_400(client):
    """GET /alerts with invalid site_code should return HTTP 400"""
    response = client.get("/alerts?site_code=fake_site")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid site_code"


def test_alerts_filters_by_warning_severity(client):
    """GET /alerts should filter warning alerts"""
    response = client.get("/alerts?severity=warning")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["severity"] == "warning"


def test_alerts_filters_by_critical_severity(client):
    """GET /alerts should filter critical alerts"""
    response = client.get("/alerts?severity=critical")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["severity"] == "critical"


def test_alerts_invalid_severity_returns_400(client):
    """GET /alerts with invalid severity should return HTTP 400"""
    response = client.get("/alerts?severity=medium")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid severity"


def test_alerts_filters_by_start_date(client):
    """GET /alerts should return alerts after the start date"""
    response = client.get("/alerts?start=2026-05-06")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["timestamp"] == "2026-05-06T10:00:00"


def test_alerts_filters_by_end_date(client):
    """GET /alerts should return alerts before the end date"""
    response = client.get("/alerts?end=2026-05-05T23:59:59")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["timestamp"] == "2026-05-05T10:00:00"


def test_alerts_invalid_start_date_returns_400(client):
    """GET /alerts with invalid start date should return HTTP 400"""
    response = client.get("/alerts?start=not-a-date")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid start date"


def test_alerts_invalid_end_date_returns_400(client):
    """GET /alerts with invalid end date should return HTTP 400"""
    response = client.get("/alerts?end=not-a-date")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid end date"


def test_alerts_returns_value_and_unit(client):
    """GET /alerts should include sensor value and unit for known alert types"""
    response = client.get("/alerts?site_code=site_test")
    data = response.get_json()

    assert data[0]["value"] == 8.5
    assert data[0]["unit"] == "NTU"
