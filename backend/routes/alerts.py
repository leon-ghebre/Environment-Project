"""
alerts.py

Route for returning alert events from the database

Personas:
    - George Weah: Needs structured alert data (site, timestamp, severity)
      to monitor contamination risks across locations
    - Lebo Xhosa: Needs simple nd readable messages to quickly understand
      whether water is safe

"""

from datetime import datetime
from flask import Blueprint, jsonify, request
from database.database import SessionLocal
from database.models import Alert, Site


alerts_bp = Blueprint("alerts", __name__)


def parse_date(date_text):
    """Convert ISO date text into a datetime object."""

    if not date_text:
        return None
    try:
        return datetime.fromisoformat(date_text)
    except ValueError:
        return "invalid"


def get_alert_value_and_unit(alert):
    """Return the sensor value and unit linked to this alert"""

    reading = alert.source_reading

    if reading is None:
        return None, None

    if alert.alert_type == "turbidity":
        return reading.turbidity_ntu, "NTU"

    if alert.alert_type == "ph":
        return reading.ph, "pH"

    if alert.alert_type == "conductivity":
        return reading.conductivity_uS_cm, "µS/cm"

    return None, None


@alerts_bp.route("/alerts", methods=["GET"])
def get_alerts():
    """
    Return alert events with optional site, severity and date filters

    Query parameters:
    - site_code (optional): Filters alerts to a specific monitoring site
    - severity (optional): Filters alerts by severity ('warning' or 'critical')
    - start (optional): Start date (ISO format YYYY-MM-DD)
    - end (optional): End date not inclusive (ISO format YYYY-MM-DD)

    Returns:
    - List of alert objects containing:
        site_code: identifier of the site
        site_name: human-readable site name
        timestamp: when the alert occurred
        alert_type: type of issue (e.g. turbidity, ph)
        severity: warning or critical
        message: one-sentence explanation (Lebo persona)
        value: sensor reading that triggered the alert
        unit: unit of measurement
    """

    site_code = request.args.get("site_code")
    severity = request.args.get("severity")
    start = request.args.get("start")
    end = request.args.get("end")

    db = SessionLocal()

    try:
        query = db.query(Alert).join(Site)

        if site_code:
            # check site exists
            site = db.query(Site).filter(Site.site_code == site_code).first()

            if site is None:
                return jsonify({"error": "Invalid site_code"}), 400

            query = query.filter(Alert.site_id == site.id)

        if severity:
            if severity not in ["warning", "critical"]:
                return jsonify({"error": "Invalid severity"}), 400

            query = query.filter(Alert.severity == severity)

        start_date = parse_date(start)
        end_date = parse_date(end)

        if start_date == "invalid":
            return jsonify({"error": "Invalid start date"}), 400

        if end_date == "invalid":
            return jsonify({"error": "Invalid end date"}), 400

        if start_date:
            query = query.filter(Alert.started_at >= start_date)

        if end_date:
            query = query.filter(Alert.started_at <= end_date)

        alerts = query.order_by(Alert.started_at.desc()).all()

        response = []

        for alert in alerts:
            value, unit = get_alert_value_and_unit(alert)

            response.append(
                {
                    "site_code": alert.site.site_code,
                    "site_name": alert.site.name,
                    "timestamp": alert.started_at.isoformat(),
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "value": value,
                    "unit": unit,
                    "source_reading_id": alert.source_reading_id,
                }
            )

        return jsonify(response), 200

    finally:
        db.close()
