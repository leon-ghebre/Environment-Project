"""
filters.py

Database query functions for filtering water quality data.
All filtering logic lives here — routes call these functions
rather than querying the database directly.

Persona coverage:
    - Jack Wilshere: date range and site filtering directly implements
      his US-02 acceptance criteria for focused dataset analysis

    - George Weah: filtering by site and date enables historical trend
      comparison for contamination risk assessment (US-10)

    - Lebo Xhosa: site filtering retrieves his specific water sources
      for the binary status dashboard (US-07)
"""

from database.database import SessionLocal
from database.models import Site, WaterReading


def get_site_by_code(db: SessionLocal, site_code: str) -> Site | None:
    """
    Looks up a site by its site_code string.

    Arguments:
    - db: Active SQLAlchemy databasee session.
    - site_code: The site identifier string from the request parameters.

    Returns:
    - The matching Site object or None if not founnd.
    """

    return db.query(Site).filter(Site.site_code == site_code).first()


def get_valid_site_codes(db: SessionLocal) -> list:
    """
    Returns a list of all valid site code strings.

    Arguments:
    - db: Active SQLAlchemy database sessionn.


    Returns:
    -  Alist of site_code strings for all sites.
    """

    sites = db.query(Site.site_code).all()
    return [site.site_code for site in sites]


def filter_water_data(
    db: SessionLocal, site_code: str, start_date: str | None = None, end_date: str | None = None
):
    """
    Filters water readings by the site and optional date range.

    Argumennts:
        - db: Active SQLAlchemy database session.
        - site_code: The site identifier string (e.g. "site_upstream")
        - start_date: Optional ISO 8601 date string
        - end_date Optionnal ISO 8601 date string

    Returns:
        - A SQLAlchemy query of WaterREading rows that are ordered by recorded_at,
         or None if the site_code doesn't exist.
    """
    site = get_site_by_code(db, site_code)

    if site is None:
        return None

    query = db.query(WaterReading.site_id == site.id)

    if start_date:
        query = query.filter(WaterReading.recorded_at >= start_date)

    if end_date:
        query = query.filter(WaterReading.recorded_at <= end_date)

    return query.order_by(WaterReading.recorded_at)
