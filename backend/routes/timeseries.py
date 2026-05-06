"""
routes/timeseries.py

Defines the GET /timeseries endpoint.
Returns aggregated water quality readings over time for a site and metric.

Delegates aggregation to services/aggregation.py which loads the
filtered query into pandas for resampling. This route only handles
HTTP concerns — extracting parameters, validating, and returning JSON.

Persona coverage:
- Jack Wilshere: primary use case — queries long date ranges to
 identify environmental trends. Supports daily and hourly aggregation
 so he can choose the resolution appropriate for his research (US-03)

- George Weah: use case - compares current readings against historical trends to
 determine whether a change is just a short-term fluctuation or is actually a developing
 contamination risk (US-10)
"""

from flask import Blueprint, jsonify, request

from config import VALID_FREQUENCIES, VALID_METRICS
from database.database import SessionLocal
from services.aggregation import get_trends
from services.filters import get_valid_site_codes

timeseries_bp = Blueprint("timeseries", __name__)


@timeseries_bp.route("/timeseries", methods=["GET"])
def timeseries() -> tuple:
    """Returns aggregated sensor readings over time for a site and metric.

    Sensor fault rows are excluded from the aggregation,
      so that faulty readings do not skew results.

    Query Parameters:
    site_code (str): Required. The site code to query (e.g. "site_upstream").
    metric (str): Optional. Sensor column to aggregate. Default: "ph".
    Must be one of VALID_METRICS in config.py.
    freq (str): Optional. Aggregation frequency. Default: "D" (daily).
    "D" for daily, "h" for hourly.
    start (str): Optional. Start date YYYY-MM-DD inclusive.
    end (str): Optional. End date YYYY-MM-DD inclusive.

    Returns:
    tuple: A JSON array of aggregated readings with HTTP 200.
    HTTP 400 if any parameter is missing or invalid.
    HTTP 404 if no data matches the selected filters.
    """
    site_code = request.args.get("site_code")
    metric = request.args.get("metric", "ph")
    freq = request.args.get("freq", "D")
    start = request.args.get("start")
    end = request.args.get("end")

    db = SessionLocal()
    try:
        valid_site_codes = get_valid_site_codes(db)

        if not site_code:
            return jsonify({"error": "site_code is required"}), 400

        if site_code not in valid_site_codes:
            return jsonify({"error": f"invalid site_code: {site_code}"}), 400

        if metric not in VALID_METRICS:
            valid = ", ".join(VALID_METRICS)
            return jsonify({"error": f"invalid metric: {metric} — must be one of: {valid}"}), 400

        if freq not in VALID_FREQUENCIES:
            return jsonify({"error": "invalid frequency — must be 'h' or 'D'"}), 400

        result = get_trends(db, site_code, metric, freq, start, end)
        if result.empty:
            return jsonify({"error": "no data found for selected filters"}), 404

        result["recorded_at"] = result["recorded_at"].astype(str)
        return jsonify(result.to_dict(orient="records")), 200

    finally:
        db.close()
