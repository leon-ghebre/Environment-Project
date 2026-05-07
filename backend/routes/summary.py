"""
routes/summary.py

Defines the GET /summary endpoint.
Returns the latest core water quality metrics for a site.

Returns a simplified subset of the latest reading — only the fields
needed for Lebo's binary dashboard. Weather columns, fault columns,
and individual alert flags are excluded to keep the response simple
and fast to parse on a low bandwidth connection.

Persona coverage:
    - Lebo Xhosa: The four metric values provide the one-sentence
      explanation when he taps a source (US-07). Simpler response than
      /latest means less data over a poor connection.

    - George Weah: secondary use — headline numbers for a site at a glance
      before deciding whether to investigate trends in detail (US-09)
"""

from flask import Blueprint, jsonify, request
from database.database import SessionLocal
from database.models import Site, WaterReading
from services.filters import get_valid_site_codes
from validation.validators import validate_site_id

summary_bp = Blueprint("summary", __name__)


@summary_bp.route("/summary", methods=["GET"])
def get_summary() -> tuple:
    """
    Rreturns the latest core water quality metrics for a site.

    Returns only the four core sensor readings, status, and alert_triggered flag.
    All other columns are omitted.

    Query Parameters:
        site_code (str): Required. The site code to query (e.g. "site_upstream").

    Returns:
        tuple: A JSON object with core metrics and HTTP 200.
               HTTP 400 if site_id is missing or invalid.
               HTTP 404 if no data exists for the site.

    """

    site_code = request.args.get("site_code")

    db = SessionLocal()
    try:
        valid_site_codes = get_valid_site_codes(db)

        error = validate_site_id(site_code, valid_site_codes)
        if error:
            return jsonify({"error": error}), 400

        site = db.query(Site).filter(Site.site_code == site_code).first()
        if site is None:
            return jsonify({"error": f"invalid site_code: {site_code}"}), 400

        latest = (
            db.query(WaterReading)
            .filter(WaterReading.site_id == site.id)
            .order_by(WaterReading.recorded_at.desc())
            .first()
        )

        if latest is None:
            return jsonify({"error": f"no data found for site: {site_code}"}), 404

        return (
            jsonify(
                {
                    "site_code": site_code,
                    "recorded_at": latest.recorded_at.isoformat(),
                    "ph": latest.ph,
                    "turbidity_ntu": latest.turbidity_ntu,
                    "conductivity_uS_cm": latest.conductivity_uS_cm,
                    "water_temperature_c": latest.water_temperature_c,
                    "status": latest.status,
                    "alert_triggered": latest.alert_triggered,
                }
            ),
            200,
        )

    finally:
        db.close()
