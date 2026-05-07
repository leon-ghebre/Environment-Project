from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

def generate_timeseries():
    today = datetime.now()
    data = []

    for i in range(30):
        day = today - timedelta(days=30 - i)

        ph = round(7 + random.uniform(-0.8, 0.8), 2)
        turbidity_ntu = round(5 + random.uniform(-2, 2), 2)
        flow = round(20 + random.uniform(-5, 5), 2)
        water_level_cm = round(100 + random.uniform(-10, 10), 2)

        conductivity_us_cm = round(450 + random.uniform(-30, 30), 2)
        water_temperature_c = round(18 + random.uniform(-3, 3), 2)

        wx_temp_c = round(21 + random.uniform(-5, 5), 2)
        wx_rh_pct = round(60 + random.uniform(-15, 15), 2)
        wx_rain_mm_hr = round(max(0, random.uniform(0, 5)), 2)

        light_lux = round(max(0, random.uniform(0, 1000)), 2)

        data.append({
            "recorded_at": day.strftime("%Y-%m-%d"),

            # water sensors
            "ph": ph,
            "turbidity_ntu": turbidity_ntu,
            "flow": flow,
            "water_level_cm": water_level_cm,
            "conductivity_us_cm": conductivity_us_cm,
            "water_temperature_c": water_temperature_c,

            # weather sensors
            "wx_temp_c": wx_temp_c,
            "wx_rh_pct": wx_rh_pct,
            "wx_rain_mm_hr": wx_rain_mm_hr,

            # environmental
            "light_lux": light_lux
        })

    return data


@app.route("/timeseries")
def timeseries():
    return jsonify(generate_timeseries())


@app.route("/sites")
def sites():
    return jsonify(["site_upstream", "site_downstream", "site_reservoir"])


if __name__ == "__main__":
    app.run(debug=True)