"""
test_sites.py

Unit tests for GET /sites endpoint.
Tests that the endpoint returns all site codes from the database.
"""

import pytest
from app import app
from database.database import Base, SessionLocal, engine
from database.models import Site


@pytest.fixture
def client():
    """Creates a test Flask client with a fresh test database."""
    app.config["TESTING"] = True
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    # add test sites
    db.add(Site(site_code="site_test_a", name="Test Site A", is_active=True))
    db.add(Site(site_code="site_test_b", name="Test Site B", is_active=True))
    db.commit()
    db.close()

    with app.test_client() as client:
        yield client

    Base.metadata.drop_all(bind=engine)


def test_get_sites_returns_200(client):
    """GET /sites should return HTTP 200."""
    response = client.get("/sites")
    assert response.status_code == 200


def test_get_sites_returns_list(client):
    """GET /sites should return a JSON array."""
    response = client.get("/sites")
    data = response.get_json()
    assert isinstance(data, list)


def test_get_sites_returns_correct_codes(client):
    """GET /sites should return the correct site codes."""
    response = client.get("/sites")
    data = response.get_json()
    assert "site_test_a" in data
    assert "site_test_b" in data


def test_get_sites_returns_sorted(client):
    """GET /sites should return site codes in alphabetical order."""
    response = client.get("/sites")
    data = response.get_json()
    assert data == sorted(data)
