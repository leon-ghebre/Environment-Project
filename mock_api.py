from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

def generate_timeseries(metric):
    today = datetime.now()
    data = []

    for i in range(30):
        day = today - timedelta(days=30 - i)

        base = {
            "ph": 7,
            "turbidity_ntu": 5,
            "flow": 20,
            "water_level_cm": 100
        }.get(metric, 10)

        avg = base + random.uniform(-1, 1)

        data.append({
            "recorded_at": day.strftime("%Y-%m-%d"),
            "avg": round(avg, 2),
            "min": round(avg - random.uniform(0.5, 1.5), 2),
            "max": round(avg + random.uniform(0.5, 1.5), 2)
        })

    return data


@app.route("/timeseries")
def timeseries():
    metric = request.args.get("metric", "ph")
    return jsonify(generate_timeseries(metric))


@app.route("/sites")
def sites():
    return jsonify(["site_a", "site_b", "site_c"])


if __name__ == "__main__":
    app.run(debug=True)