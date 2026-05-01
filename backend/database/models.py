"""
models.py

Defines the database tables used in the water quality monitoring backend

This file contains:
- Site: stores information about each monitoring location
- WaterReading: stores timestamped sensor readings for each site
- Alert: stores warning or critical alerts linked to a site and reading
"""

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base


# stores details about each water monitoring site.
class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    site_code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    is_active = Column(Boolean, default=True)

    # stores all water readings linked to this site
    readings = relationship("WaterReading", back_populates="site")

    # stores all alerts linked to this site
    alerts = relationship("Alert", back_populates="site")


# stores a time stamped sensor reading for a site
class WaterReading(Base):
    __tablename__ = "water_readings"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(
        Integer,
        ForeignKey("sites.id"),
        nullable=False,
        index=True,
    )
    recorded_at = Column(DateTime, nullable=False, index=True)

    ph = Column(Float, nullable=True)
    turbidity_ntu = Column(Float, nullable=True)
    conductivity_uS_cm = Column(Float, nullable=True)
    water_temperature_c = Column(Float, nullable=True)
    water_level_cm = Column(Float, nullable=True)
    light_lux = Column(Float, nullable=True)

    status = Column(String, nullable=False, index=True)

    alert_triggered = Column(Boolean, nullable=False, default=False)
    alert_ph = Column(Boolean, default=False)
    alert_turbidity = Column(Boolean, default=False)
    alert_turbidity_crit = Column(Boolean, default=False)
    alert_conductivity = Column(Boolean, default=False)

    wx_temp_c = Column(Float, nullable=True)
    wx_rh_pct = Column(Float, nullable=True)
    wx_rain_mm_hr = Column(Float, nullable=True)

    # true when a row contains impossible data
    sensor_fault = Column(Boolean, default=False)
    fault_reason = Column(String, nullable=True)  # why its flagged true

    # links each reading back to the site it belongs to
    site = relationship("Site", back_populates="readings")

    # stores alerts triggered by this specific reading
    alerts = relationship("Alert", back_populates="source_reading")


# stores warning or critical alert events
class Alert(Base):
    __tablename__ = "alert_events"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(
        Integer,
        ForeignKey("sites.id"),
        nullable=False,
        index=True,
    )
    source_reading_id = Column(
        Integer,
        ForeignKey("water_readings.id"),
        nullable=False,
        index=True,
    )

    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)

    message = Column(String, nullable=False)

    started_at = Column(DateTime, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)  # none = still active

    # links each alert back to the site it belongs to
    site = relationship("Site", back_populates="alerts")

    # links each alert back to the reading that triggered it
    source_reading = relationship("WaterReading", back_populates="alerts")
