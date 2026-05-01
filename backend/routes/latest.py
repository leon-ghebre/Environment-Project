"""
latest.py

Route for returning the most recent water quality reading for a site.

Persona:
    - Lebo Xhosa: Needs immediate status without complex data
"""

from flask import Blueprint, jsonify, request

from database.database import SessionLocal
from database.models import Site, WaterReading

latest_bp = Blueprint("latest", __name__)


@latest_bp.route("/latest", methods=["GET"])
def get_latest():
    """
    GET /latest?site_code= ...

    Query Paramameters:
        site_code (str): id name of site

    Returns:
        JSON containing latest reading + status information
    """
    site_code = request.args.get("site_code")

    # get the site code from the query parameters
    if not site_code:
        return jsonify({"error": "site_code is required"}), 400

    db = SessionLocal()

    try:
        # look up site code and check it exists
        site = db.query(Site).filter(Site.site_code == site_code).first()

        if site is None:
            return jsonify({"error": f"Invalid site_code: {site_code}"}), 404

        # return last readings for that site code or error if nothing
        reading = (
            db.query(WaterReading)
            .filter(WaterReading.site_id == site.id)
            .order_by(WaterReading.recorded_at.desc())
            .first()
        )

        if reading is None:
            return jsonify({"error": f"No readings for {site_code}"}), 404

        # json response
        return (
            jsonify(
                {
                    "site_id": site.id,
                    "site_code": site.site_code,
                    "name": site.name,
                    "description": site.description,
                    "recorded_at": reading.recorded_at.isoformat(),
                    "ph": reading.ph,
                    "turbidity_ntu": reading.turbidity_ntu,
                    "conductivity_uS_cm": reading.conductivity_uS_cm,
                    "water_temperature_c": reading.water_temperature_c,
                    "water_level_cm": reading.water_level_cm,
                    "status": reading.status,
                    "alert_triggered": reading.alert_triggered,
                    "sensor_fault": reading.sensor_fault,
                    "fault_reason": reading.fault_reason,
                }
            ),
            200,
        )

    finally:
        db.close()
