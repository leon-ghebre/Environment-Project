from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

SITE_CODES = ["site_upstream", "site_downstream", "site_reservoir"]

METRICS = {
    "ph": {"base": 7.1, "variance": 0.35},
    "turbidity_ntu": {"base": 4.8, "variance": 1.1},
    "water_level_cm": {"base": 96.0, "variance": 8.0},
    "conductivity_us_cm": {"base": 420.0, "variance": 35.0},
    "water_temperature_c": {"base": 12.0, "variance": 4.0},
    "wx_temp_c": {"base": 14.0, "variance": 6.0},
    "wx_rh_pct": {"base": 72.0, "variance": 12.0},
    "wx_rain_mm_hr": {"base": 0.4, "variance": 1.8},
    "light_lux": {"base": 550.0, "variance": 260.0},
}

SITE_OFFSETS = {
    "site_upstream": -0.25,
    "site_downstream": 0.4,
    "site_reservoir": 0.15,
}

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()

def daterange(start_date, end_date):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)

def generate_metric_value(metric, site_code, day):
    cfg = METRICS[metric]
    base = cfg["base"]
    variance = cfg["variance"]
    site_offset = SITE_OFFSETS.get(site_code, 0)

    seasonal = ((day.timetuple().tm_yday % 30) - 15) / 15

    if metric == "ph":
        value = base + site_offset + random.uniform(-variance, variance)
    elif metric == "turbidity_ntu":
        value = base + site_offset + random.uniform(-variance, variance) + max(0, seasonal * 0.6)
    elif metric == "water_level_cm":
        value = base + site_offset * 10 + random.uniform(-variance, variance)
    elif metric == "conductivity_us_cm":
        value = base + site_offset * 20 + random.uniform(-variance, variance)
    elif metric == "water_temperature_c":
        value = base + seasonal * 3 + random.uniform(-variance, variance)
    elif metric == "wx_temp_c":
        value = base + seasonal * 5 + random.uniform(-variance, variance)
    elif metric == "wx_rh_pct":
        value = max(35, min(100, base - seasonal * 10 + random.uniform(-variance, variance)))
    elif metric == "wx_rain_mm_hr":
        raw = base + random.uniform(-variance, variance)
        value = max(0, raw)
    elif metric == "light_lux":
        value = max(0, base + seasonal * 160 + random.uniform(-variance, variance))
    else:
        value = base + random.uniform(-variance, variance)

    return round(value, 2)

@app.route("/")
def home():
    return render_template("index.html")
    

@app.route("/sites")
def sites():
    return jsonify(SITE_CODES)

@app.route("/timeseries")
def timeseries():
    site_code = request.args.get("site_code")
    metric = request.args.get("metric")
    freq = request.args.get("freq", "D")
    start = request.args.get("start")
    end = request.args.get("end")

    if not site_code or site_code not in SITE_CODES:
        return jsonify({"error": "Invalid or missing site_code"}), 400

    if not metric or metric not in METRICS:
        return jsonify({"error": "Invalid or missing metric"}), 400

    if freq != "D":
        return jsonify({"error": "Only daily frequency (freq=D) is supported"}), 400

    try:
        end_date = parse_date(end) if end else datetime.now().date()
        start_date = parse_date(start) if start else end_date - timedelta(days=7)
    except ValueError:
        return jsonify({"error": "Dates must be in YYYY-MM-DD format"}), 400

    if start_date > end_date:
        return jsonify({"error": "start must be before or equal to end"}), 400

    data = []
    for day in daterange(start_date, end_date):
        data.append({
            "site_code": site_code,
            "recorded_at": day.strftime("%Y-%m-%d"),
            metric: generate_metric_value(metric, site_code, day)
        })

    return jsonify(data)

@app.route("/api/alerts")
def alerts():
    from_date_str = request.args.get("from")

    try:
        from_date = parse_date(from_date_str) if from_date_str else datetime.now().date()
    except ValueError:
        return jsonify({"error": "from must be YYYY-MM-DD"}), 400

    today = datetime.now().date()
    if from_date > today:
        return jsonify([])

    alerts_data = []
    current = from_date

    while current <= today:
        for site_code in SITE_CODES:
            if random.random() < 0.22:
                metric = random.choice(list(METRICS.keys()))
                severity = random.choice(["low", "medium", "high"])
                alerts_data.append({
                    "id": f"{site_code}-{metric}-{current.isoformat()}-{random.randint(100,999)}",
                    "site_code": site_code,
                    "metric": metric,
                    "severity": severity,
                    "message": f"{metric} threshold exceeded at {site_code}",
                    "timestamp": f"{current.isoformat()}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00"
                })
        current += timedelta(days=1)

    return jsonify(alerts_data)

if __name__ == "__main__":
    app.run(debug=True)