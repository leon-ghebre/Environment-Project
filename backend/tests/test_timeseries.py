"""
test_timeseries.py

Unit tests for GET /timeseries endpoint.
Tests aggregated water quality readings over time for a site and metric.
Persona coverage:

    - Jack Wilshere: trend analysis across date ranges and sites (US-03)

    - George Weah: historical comparison for contamination detection (US-10)
"""

import pytest
from datetime import datetime

from app import app
from database.database import Base, SessionLocal, engine
from database.models import Site, WaterReading


@pytest.fixture
def client():
    """This creates a test Flask client with a fresh test database."""
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

    # add readings across two days for aggregation testing
    readings = [
        WaterReading(
            site_id=site.id,
            recorded_at=datetime(2023, 1, 1, 6, 0, 0),
            ph=7.0,
            turbidity_ntu=2.0,
            conductivity_uS_cm=300.0,
            water_temperature_c=15.0,
            water_level_cm=100.0,
            light_lux=500.0,
            status="normal",
            alert_triggered=False,
            alert_ph=False,
            alert_turbidity=False,
            alert_turbidity_crit=False,
            alert_conductivity=False,
            sensor_fault=False,
        ),
        WaterReading(
            site_id=site.id,
            recorded_at=datetime(2023, 1, 1, 12, 0, 0),
            ph=7.4,
            turbidity_ntu=3.0,
            conductivity_uS_cm=350.0,
            water_temperature_c=17.0,
            water_level_cm=110.0,
            light_lux=800.0,
            status="normal",
            alert_triggered=False,
            alert_ph=False,
            alert_turbidity=False,
            alert_turbidity_crit=False,
            alert_conductivity=False,
            sensor_fault=False,
        ),
        WaterReading(
            site_id=site.id,
            recorded_at=datetime(2023, 1, 2, 6, 0, 0),
            ph=6.8,
            turbidity_ntu=4.0,
            conductivity_uS_cm=400.0,
            water_temperature_c=14.0,
            water_level_cm=105.0,
            light_lux=400.0,
            status="normal",
            alert_triggered=False,
            alert_ph=False,
            alert_turbidity=False,
            alert_turbidity_crit=False,
            alert_conductivity=False,
            sensor_fault=False,
        ),
        # sensor fault row — should be excluded from aggregation
        WaterReading(
            site_id=site.id,
            recorded_at=datetime(2023, 1, 2, 12, 0, 0),
            ph=99.0,
            turbidity_ntu=5.0,
            conductivity_uS_cm=450.0,
            water_temperature_c=16.0,
            water_level_cm=108.0,
            light_lux=600.0,
            status="warning",
            alert_triggered=True,
            alert_ph=False,
            alert_turbidity=False,
            alert_turbidity_crit=False,
            alert_conductivity=False,
            sensor_fault=True,
            fault_reason="pH outside possible range 0-14",
        ),
    ]

    for reading in readings:
        db.add(reading)
    db.commit()
    db.close()

    with app.test_client() as client:
        yield client

    Base.metadata.drop_all(bind=engine)


def test_timeseries_returns_200(client):
    """The GET/timeseries endpoint with valid paramaterss should return HTTP 200."""
    response = client.get("/timeseries?site_code=site_test&metric=ph&freq=D")
    assert response.status_code == 200


def test_timeseries_returns_list(client):
    """The GET/timeseries enndpoint should return a JSON array."""
    response = client.get("/timeseries?site_code=site_test&metric=ph&freq=D")
    data = response.get_json()
    assert isinstance(data, list)


def test_timeseries_returns_correct_fields(client):
    """The GET/timeseries endppoint should return recorded_at, avg, min and max per bucket."""
    response = client.get("/timeseries?site_code=site_test&metric=ph&freq=D")
    data = response.get_json()
    assert len(data) > 0
    first = data[0]
    assert "recorded_at" in first
    assert "avg" in first
    assert "min" in first
    assert "max" in first


def test_timeseries_daily_aggregation(client):
    """The GET/timeseries endpoint with freq=D should return one row per day."""
    response = client.get("/timeseries?site_code=site_test&metric=ph&freq=D")
    data = response.get_json()
    # two days of data — expect 2 rows
    assert len(data) == 2


def test_timeseries_hourly_aggregation(client):
    """The GET/timeseries endpoinnt with freq=h should return one row per hour."""
    response = client.get("/timeseries?site_code=site_test&metric=ph&freq=h")
    data = response.get_json()
    # 3 valid readings at different hours (fault row excluded) — expect 3 rows
    assert len(data) == 3


def test_timeseries_excludes_sensor_fault_rows(client):
    """The GET/timeseries endpont should exclude sensor fault rows from aggregation.

    The fixture includes a fault row with ph=99.0 on 2023-01-02.
    The daily average for that day should only reflect the valid reading
    (ph=6.8) not the faulty one.
    """
    response = client.get("/timeseries?site_code=site_test&metric=ph&freq=D")
    data = response.get_json()
    day_two = next(r for r in data if "2023-01-02" in r["recorded_at"])
    assert day_two["avg"] == pytest.approx(6.8, abs=0.01)
    assert day_two["max"] == pytest.approx(6.8, abs=0.01)


def test_timeseries_default_metric_is_ph(client):
    """GET/timeseries endpoint without metric param should default to ph."""
    response = client.get("/timeseries?site_code=site_test&freq=D")
    assert response.status_code == 200


def test_timeseries_default_freq_is_daily(client):
    """The GET/timeseries enndpoint without freq param should default to daily."""
    response = client.get("/timeseries?site_code=site_test&metric=ph")
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == 2


def test_timeseries_date_range_filter(client):
    """GET/timeseries endpoint with start and end should return only data in range."""
    response = client.get(
        "/timeseries?site_code=site_test&metric=ph&freq=D&start=2023-01-01&end=2023-01-02"
    )
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == 1
    assert "2023-01-01" in data[0]["recorded_at"]


def test_timeseries_missing_site_code_returns_400(client):
    """GET/timeseries endpoint without site_code should return HTTP 400."""
    response = client.get("/timeseries?metric=ph&freq=D")
    assert response.status_code == 400


def test_timeseries_invalid_site_code_returns_400(client):
    """GET/timeseries endpoint with invalid site_code should return HTTP 400."""
    response = client.get("/timeseries?site_code=fake_site&metric=ph")
    assert response.status_code == 400


def test_timeseries_invalid_metric_returns_400(client):
    """GET/timeseries ennndpoint with invalid metric should return HTTP 400."""
    response = client.get("/timeseries?site_code=site_test&metric=invalid_col")
    assert response.status_code == 400


def test_timeseries_invalid_freq_returns_400(client):
    """GET/timeseries endpoint  with invalid frequency should return HTTP 400."""
    response = client.get("/timeseries?site_code=site_test&metric=ph&freq=weekly")
    assert response.status_code == 400


def test_timeseries_no_data_in_range_returns_404(client):
    """GET/timeseries endpoint with date range outside data should return HTTP 404."""
    response = client.get(
        "/timeseries?site_code=site_test&metric=ph&freq=D&start=2099-01-01&end=2099-12-31"
    )
    assert response.status_code == 404
