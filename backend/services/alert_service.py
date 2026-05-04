"""
alert_service.py

Contains the logic for creating alert records from water readings
"""

from database.models import Alert

from config import (
    PH_CRITICAL_MIN,
    PH_CRITICAL_MAX,
    CONDUCTIVITY_CRITICAL_LIMIT,
)


def get_ph_severity(ph):
    """Return severtiy for pH alert based on SANS 241 thresholds."""

    if ph is not None and (ph < PH_CRITICAL_MIN or ph > PH_CRITICAL_MAX):
        return "critical"

    return "warning"


def get_conductivity_severity(conductivity):
    """Return severity for conductivity alert based on thresholds."""

    if conductivity is not None and conductivity > CONDUCTIVITY_CRITICAL_LIMIT:
        return "critical"

    return "warning"


def create_alert_events_for_reading(db, reading):
    """Create alert records for any alerts triggered by a reading.

    Args:
        db: Active database
        reading: WaterReading object
    """

    alerts = []

    # turbidity already has separate warning and critical flags in the dataset
    # alert_turbidity = turbidity > 5 NTU
    # alert_turbidity_crit = turbidity > 10 NTU
    # so we can use these directly instead of recalculating thresholds

    # check critical first to avoid duplicate alerts
    if reading.alert_turbidity_crit:
        alerts.append(
            {
                "alert_type": "turbidity",
                "severity": "critical",
                "message": (
                    "Critical turbidity detected. Water is very "
                    "cloudy and may be unsafe for drinking or cleaning. "
                    "Avoid using this water."
                ),
            }
        )

    elif reading.alert_turbidity:
        alerts.append(
            {
                "alert_type": "turbidity",
                "severity": "warning",
                "message": (
                    "Turbidity is above recommended levels. Water may be "
                    "cloudy and less safe for drinking or cleaning. "
                    "Treat or boil before use."
                ),
            }
        )

    # alert_ph only tells us if somethings, so we calculate severity
    if reading.alert_ph:
        severity = get_ph_severity(reading.ph)

        if severity == "critical":
            message = (
                "Critical pH level detected. Water may be unsafe for "
                "drinking and could irritate skin during cleaning. "
                "Avoid using this water."
            )
        else:
            message = (
                "pH is outside the recommended range. Water quality may "
                "be affected for drinking and cleaning. Use with caution."
            )

        alerts.append(
            {
                "alert_type": "ph",
                "severity": severity,
                "message": message,
            }
        )

    # conductivity
    if reading.alert_conductivity:
        severity = get_conductivity_severity(reading.conductivity_uS_cm)

        if severity == "critical":
            message = (
                "Critical conductivity detected. This may indicate "
                "contamination or high salt levels. Avoid using this water."
            )
        else:
            message = (
                "Conductivity is above recommended levels. This may indicate "
                "increased salts or runoff. Use with caution."
            )

        alerts.append(
            {
                "alert_type": "conductivity",
                "severity": severity,
                "message": message,
            }
        )

    # sensor fault comes from validation, not original dataset rules
    if reading.sensor_fault:
        alerts.append(
            {
                "alert_type": "sensor_fault",
                "severity": "warning",
                "message": reading.fault_reason or "Sensor fault detected.",
            }
        )

    # save to database w/ each alert becomes its own row in alert_events table
    for alert in alerts:
        db.add(
            Alert(
                site_id=reading.site_id,
                source_reading_id=reading.id,
                alert_type=alert["alert_type"],
                severity=alert["severity"],
                message=alert["message"],
                started_at=reading.recorded_at,
                ended_at=None,  # not tracking durations in MVP
            )
        )
