"""
aggregation.py

Time series aggregation for water quality data.
Loads filtered database query results into pandas for resampling.

Persona coverage:
    - Jack Wilshere: hourly and daily aggregation directly implements
      his US-03 trend chart acceptance criteria.
    - George Weah: historical trend comparison for US-10.
"""

import pandas as pd

from database.models import WaterReading
from services.filters import get_site_by_code


def get_trends(
    db,
    site_code: str,
    metric: str,
    freq: str = "D",
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """Returns aggregated sensor readings over time for a site and metric.

    Args:
        db: Active SQLAlchemy database session.
        site_code: The site identifier string (e.g. "site_upstream").
        metric: The sensor column to aggregate (e.g. "ph", "turbidity_ntu").
        freq: Aggregation frequency — "D" for daily, "h" for hourly.
        start_date: Optional ISO 8601 date string — inclusive start (YYYY-MM-DD).
        end_date: Optional ISO 8601 date string — inclusive end (YYYY-MM-DD).

    Returns:
        A DataFrame with columns: recorded_at, avg, min, max.
        Returns an empty DataFrame if no data matches the filters.
    """
    site = get_site_by_code(db, site_code)
    if site is None:
        return pd.DataFrame()

    query = db.query(WaterReading).filter(
        WaterReading.site_id == site.id,
        WaterReading.sensor_fault == False,  # noqa: E712
    )

    if start_date:
        query = query.filter(WaterReading.recorded_at >= start_date)

    if end_date:
        query = query.filter(WaterReading.recorded_at <= end_date)

    rows = query.order_by(WaterReading.recorded_at).all()

    if not rows:
        return pd.DataFrame()

    data = pd.DataFrame(
        [
            {
                "recorded_at": row.recorded_at,
                metric: getattr(row, metric),
            }
            for row in rows
        ]
    )

    data = data.dropna(subset=[metric])

    if data.empty:
        return pd.DataFrame()

    trend = (
        data.set_index("recorded_at")
        .resample(freq)[metric]
        .agg(["mean", "min", "max"])
        .dropna()
        .reset_index()
        .rename(columns={"mean": "avg"})
    )

    return trend
