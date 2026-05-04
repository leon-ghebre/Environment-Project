"""
routes/sites.py

This file defines the GET/sites endpoint and returns a list of all unique site IDs present in the dataset.

Persona Coverage:
    - Jack Wilshere: In order for filtering functionality, Jack must know which sites exist before querying trends or exporting data.
    
    - George Weah: George must know available monitoring locations before he's able to compare readings across regions

    - Lebo Xhosa: In order to populate his list of water sources on the dashboard he needs to know which sites are present in the database.


"""

from flask import Blueprint, jsonify
from services.data_loader import defines

sites_bp = Blueprint("sites", __name__)

@sites_bp.route("/sites", methods=["GET"])
def get_sites() -> tuple:
    """
    This function returns all unique site IDs from the dataset.

    No parameters are required.
    It returns every site that has at least one reading in the dataset.

    Returns: A JSONN array of site ID strings with HTTP 200.

    """

    site_ids = sorted(df["site_id"].unique().tolist())
    return jsonify(site_ids), 200