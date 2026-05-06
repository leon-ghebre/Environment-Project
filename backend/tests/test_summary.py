"""
test_summary.py

Unit tests for GET /summary endpoint.
Tests that the endpoint returns the latest core water quality metrics
for a site in a simplified low-bandwidth response.

Persona coverage:
    - Lebo Xhosa: summary endpoint is specifically designed for his
      low bandwidth connection — tests verify only essential fields
      are returned and response is correct
"""

import pytest
from datetime import datetime

from app import app
from database.database import Base, SessionLocal, engine
from database.models import Site, WaterReading


@pytest.fixture
def client():
    """Creates a test Flask client with a fresh test database."""
    app.config["TESTING"] = True
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    site = Site(
        site_code="site_test",
        name="Test Site",
        description="Test site for unit tests",
        is_active=True,
    )
    db.add(site)
    db.commit()
    db.refresh(site)

    older_reading = WaterReading(
        site_id=site.id,
        recorded_at=datetime(2023, 1, 1, 10, 0, 0),
        ph=6.5,
        turbidity_ntu=2.1,
        conductivity_uS_cm=300.0,
        water_temperature_c=17.0,
        water_level_cm=120.0,
        light_lux=500.0,
        status="normal",
        alert_triggered=False,
        alert_ph=False,
        alert_turbidity=False,
        alert_turbidity_crit=False,
        alert_conductivity=False,
        sensor_fault=False,
    )

    latest_reading = WaterReading(
        site_id=site.id,
        recorded_at=datetime(2023, 6, 1, 12, 0, 0),
        ph=7.2,
        turbidity_ntu=3.1,
        conductivity_uS_cm=450.0,
        water_temperature_c=18.5,
        water_level_cm=142.0,
        light_lux=800.0,
        status="normal",
        alert_triggered=False,
        alert_ph=False,
        alert_turbidity=False,
        alert_turbidity_crit=False,
        alert_conductivity=False,
        sensor_fault=False,
    )

    db.add(older_reading)
    db.add(latest_reading)
    db.commit()
    db.close()

    with app.test_client() as client:
        yield client

    Base.metadata.drop_all(bind=engine)


def test_summary_returns_200(client):
    """a GET /summary with valid site_code should return a HTTP 200."""
    response = client.get("/summary?site_code=site_test")
    assert response.status_code == 200


def test_summary_returns_correct_site_code(client):
    """The GET /summary should return the correct site_code in its response."""
    response = client.get("/summary?site_code=site_test")
    data = response.get_json()
    assert data["site_code"] == "site_test"


def test_summary_returns_latest_reading(client):
    """GET /summary should return the most recent reading not an older one."""
    response = client.get("/summary?site_code=site_test")
    data = response.get_json()
    assert data["ph"] == 7.2
    assert data["turbidity_ntu"] == 3.1
    assert data["conductivity_uS_cm"] == 450.0
    assert data["water_temperature_c"] == 18.5


def test_summary_returns_required_fields(client):
    """a GET /summary should return all the required fields."""
    response = client.get("/summary?site_code=site_test")
    data = response.get_json()
    required_fields = [
        "site_code",
        "recorded_at",
        "ph",
        "turbidity_ntu",
        "conductivity_uS_cm",
        "water_temperature_c",
        "status",
        "alert_triggered",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


def test_summary_excludes_weather_and_fault_fields(client):
    """GET /summary should not include weather or fault columns.

    Summary is a low bandwidth endpoint for Lebo Xhosa — only essential
    fields should be returned to minimise data transfer on poor connections.
    """
    response = client.get("/summary?site_code=site_test")
    data = response.get_json()
    excluded_fields = [
        "wx_temp_c",
        "wx_rh_pct",
        "wx_rain_mm_hr",
        "sensor_fault",
        "fault_reason",
        "light_lux",
        "water_level_cm",
        "alert_ph",
        "alert_turbidity",
        "alert_turbidity_crit",
        "alert_conductivity",
    ]
    for field in excluded_fields:
        assert field not in data, f"Field should be excluded: {field}"


def test_summary_missing_site_code_returns_400(client):
    """A GET /summary without a site_code should return  a HTTP 400."""
    response = client.get("/summary")
    assert response.status_code == 400


def test_summary_invalid_site_code_returns_400(client):
    """A GET /summary with an invalid site_code should return a HTTP 400."""
    response = client.get("/summary?site_code=fake_site")
    assert response.status_code == 400


def test_summary_invalid_site_code_returns_error_message(client):
    """A GET /summary with an invalid site_code should return an error thats descriptive."""
    response = client.get("/summary?site_code=fake_site")
    data = response.get_json()
    assert "error" in data
