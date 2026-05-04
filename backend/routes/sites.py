"""
routes/sites.py

Defines the GET /sites endpoint.
Returns a list of all unique site codes from the database.

Persona coverage:
    - All personas: prerequisite for every other endpoint
    - Jack Wilshere: populates site filter dropdown (US-01, US-02)
    - George Weah: discovers all monitoring locations (US-09)
    - Lebo Xhosa: builds list of water sources on dashboard (US-07)
"""

from flask import Blueprint, jsonify

from database.database import SessionLocal
from database.models import Site

sites_bp = Blueprint("sites", __name__)


@sites_bp.route("/sites", methods=["GET"])
def get_sites():
    """Returns all site codes available in the database.

    Returns:
        tuple: A JSON array of site code strings with HTTP 200.

    Example response:
        ["site_downstream", "site_reservoir", "site_upstream"]
    """
    db = SessionLocal()
    try:
        sites = db.query(Site.site_code).all()
        site_codes = sorted([site.site_code for site in sites])
        return jsonify(site_codes), 200
    finally:
        db.close()
