"""
app.py

This is the entry point for the Water Quality monitoring API - it
registers all route blueprints and starts the flask development server

"""

from flask import Flask

from routes.sites import sites_bp

# from routes.latest import latest_bp

# from routes.summary import summary_bp
# from routes.timeseries import timeseries_bp
# from routes.alerts import alerts_bp
# from routes.export import export_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(sites_bp)
# app.register_blueprint(latest_bp)
# app.register_blueprint(summary_bp)
# app.register_blueprint(timeseries_bp)
# pp.register_blueprint(alerts_bp)
# app.register_blueprint(export_bp)

if __name__ == "__main__":
    app.run(debug=True)
