"""
app.py

This is the entry point for the Water Quality monitoring API - it
registers all route blueprints and starts the flask development server

"""

from flask import Flask, render_template, send_from_directory
from routes.sites import sites_bp

from routes.latest import latest_bp

from routes.summary import summary_bp

from routes.timeseries import timeseries_bp

from routes.alerts import alerts_bp

from routes.export import export_bp

from flask_cors import CORS

app = Flask(
    __name__,
    template_folder="../templates/templates/static",
    static_folder="../static/css",
    static_url_path="/static",
)
CORS(app)
app.register_blueprint(sites_bp)
app.register_blueprint(latest_bp)
app.register_blueprint(summary_bp)

app.register_blueprint(timeseries_bp)

app.register_blueprint(alerts_bp)
app.register_blueprint(export_bp)


@app.route("/alerts.html")
def alerts():
    return send_from_directory("../templates/templates/static", "alerts.html")


@app.route("/advanced-graphs.html")
def advanced_graphs():
    return send_from_directory("../templates/templates/static", "advanced-graphs.html")


@app.route("/export.html")
def export_page():
    return send_from_directory("../templates/templates/static", "export.html")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
