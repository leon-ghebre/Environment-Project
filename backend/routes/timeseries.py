"""
routes/timeseries.py

Defines the GET /timeseries endpoing.
Returns the aggregated water quality readings over time for a site/metric filter.

Persona coverage:
    - Jack Wilshere: 
        - Queries long date ranges across sites to identify patterns in the environment.
        - Supports hourly and daily aggregation time periods, giving him the ability to choose which period is appropriate for his research
"""

from flask import Blueprint, jsonify, request
from services.aggregation import get_trends
from services.data_loader import df
from validation.validators import validate_timeseries_params

timeseries_bp = Blueprint("timeseries", __name__)
@timeseries_bp.route("/timeseries", methods=["GET"]) #defines a GET endpoint that allows for frontend to request filtered and aggregated water data
def timeseries() -> tuple: 
    """
    timeseries() returns aggregated sensor readings over time for a site and metric. 
    - It aggregates data into hourly or daily time periods and returns the mean, minimum and maximum value per period.
    
    
    """
    site_id = request.args.get("site_id") 
    metric = request.args.get("metric", "ph")  #using ph as default if metric not specified (ph is widely understood and in every row)
    freq = request.args.get("freq", "D")  #gets time group for aggregation, using "D"(daily) as default
    start = request.args.get("start") 
    end = request.args.get("end")  

    

    result = get_trends(site_id, metric, freq, start, end)
    if result.empty:
        return jsonify({"error": "no data found for selected filters"}), 404  #handle empty result
    result["timestamp"] = result["timestamp"].astype(str)  #convert datetime to string format for use with JSON
    return jsonify(result.to_dict(orient="records")), 200  #convert dataframe to list of dictionary so it can be sent to frontend as JSON
