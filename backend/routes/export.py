"""
export.py

Provides the endpoint to be able to download filtered water quality
as a CSV file with /GET export

Filters are:
    - monitoring site (site_code)
    - start date
    - end date

Persona Coverage:
    - Jack Wilshere: a reseacher who needs to download raw filtered
    site analysis data for offline analysis. This lets him have a clean
    CSV file with data he can upload to external data analysis tools
    rather than having to copy and paste readings from the dashboard

"""

from config import EXPORT_COLUMNS
from flask import Blueprint, Response, jsonify, request

import csv
from io import StringIO
from datetime import datetime
from database.database import SessionLocal
from database.models import Site, WaterReading

export_bp = Blueprint("export", __name__)


@export_bp.route("/export", methods=["GET"])
def export_csv():
    """

    query params:
        - site_code (required):  'site_upstream', site_downstream',
        'site_resovoir'
        - start (optional): YYYY-MM-DD
        - end (optional): YYYY-MM-DD

    """

    site_code = request.args.get("site_code")
    start = request.args.get("start")
    end = request.args.get("end")

    if not site_code:
        return jsonify({"error": "site_code is required"}), 400

    db = SessionLocal()

    try:
        # query by the site_code first
        query = db.query(WaterReading).join(Site).filter(Site.site_code == site_code)

        # add date queries if they've been added
        if start:
            try:
                start_date = datetime.strptime(start, "%Y-%m-%d")  # iso format
            except ValueError:
                return jsonify({"error": "start must be YYYY-MM-DD"}), 400

            query = query.filter(WaterReading.recorded_at >= start_date)

        if end:
            try:
                end_date = datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "end must be YYYY-MM-DD"}), 400

            query = query.filter(WaterReading.recorded_at <= end_date)

        readings = query.order_by(WaterReading.recorded_at.asc()).all()

        if not readings:
            return jsonify({"error": "no data found for selected filters"}), 404

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()

        for reading in readings:
            row = {}
            for column in EXPORT_COLUMNS:
                if column == "timestamp":
                    value = reading.recorded_at.strftime("%Y-%m-%dT%H:%M:%S")
                elif column == "site_code":
                    value = site_code
                else:
                    value = getattr(reading, column, None)

                row[column] = value

            writer.writerow(row)

        csv_data = output.getvalue()
        output.close()

        # create custom filename based on filters (easier to recognise)
        filename = f"water_quality_{site_code}"

        if start and end:
            filename += f"_{start}_to_{end}"
        elif start:
            filename += f"_from_{start}"
        elif end:
            filename += f"_to_{end}"

        filename += ".csv"

        # return the downloadable csv file
        # disposition = download as attachment not as page
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as error:
        print(f"Export error: {error}")
        return jsonify({"error": "server error"}), 500

    finally:
        db.close()


"""
