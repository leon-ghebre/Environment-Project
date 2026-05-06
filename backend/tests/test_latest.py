"""
test_latest.py

Unit tests for GET /latest endpoint.
Tests that the endpoint returns the most recent water quality reading for a valid site.
"""

from datetime import datetime

import pytest
from app import app
from database.database import Base, SessionLocal, engine
from database.models import Site, WaterReading


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

    # add an old and a new reading
    older_reading = WaterReading(
        site_id=site.id,
        recorded_at=datetime(2023, 1, 1, 10, 0, 0),
        ph=6.8,
        turbidity_ntu=3.0,
        conductivity_uS_cm=250.0,
        water_temperature_c=18.0,
        water_level_cm=70.0,
        status="normal",
        alert_triggered=False,
        sensor_fault=False,
        fault_reason=None,
    )

    latest_reading = WaterReading(
        site_id=site.id,
        recorded_at=datetime(2023, 1, 1, 11, 0, 0),
        ph=7.2,
        turbidity_ntu=4.5,
        conductivity_uS_cm=300.0,
        water_temperature_c=19.0,
        water_level_cm=72.0,
        status="warning",
        alert_triggered=True,
        sensor_fault=False,
        fault_reason=None,
    )

    db.add(older_reading)
    db.add(latest_reading)
    db.commit()
    db.close()

    with app.test_client() as client:
        yield client

    Base.metadata.drop_all(bind=engine)


def test_latest_returns_200(client):
    """GET /latest should return HTTP 200 for a valid site."""
    response = client.get("/latest?site_code=site_test")
    assert response.status_code == 200


def test_latest_returns_required_fields(client):
    """GET /latest should return all required fields"""
    response = client.get("/latest?site_code=site_test")
    data = response.get_json()

    required_fields = [
        "site_code",
        "name",
        "description",
        "recorded_at",
        "ph",
        "turbidity_ntu",
        "conductivity_uS_cm",
        "water_temperature_c",
        "water_level_cm",
        "status",
        "alert_triggered",
        "sensor_fault",
        "fault_reason",
    ]

    for field in required_fields:
        assert field in data, f"Missing field: {field}"


def test_latest_returns_correct_site_code(client):
    """GET /latest should return the requested site code"""
    response = client.get("/latest?site_code=site_test")
    data = response.get_json()

    assert data["site_code"] == "site_test"


def test_latest_returns_most_recent_reading(client):
    """GET /latest should return the newest reading for the site"""
    response = client.get("/latest?site_code=site_test")
    data = response.get_json()

    assert data["ph"] == 7.2
    assert data["recorded_at"] == "2023-01-01T11:00:00"
    assert data["status"] == "warning"


def test_latest_missing_site_code_returns_400(client):
    """GET /latest without site_code should return HTTP 400."""
    response = client.get("/latest")

    assert response.status_code == 400
    assert response.get_json()["error"] == "site_code is required"


def test_latest_invalid_site_code_returns_400(client):
    """GET /latest with an invalid site_code should return HTTP 400."""
    response = client.get("/latest?site_code=fake_site")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid site_code: fake_site"


def test_latest_valid_site_with_no_readings_returns_404(client):
    """GET /latest should return HTTP 404 when a valid site has no readings."""
    response = client.get("/latest?site_code=site_empty")

    assert response.status_code == 404
    assert response.get_json()["error"] == "No readings for site_empty"
