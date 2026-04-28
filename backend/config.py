"""
config.py

This is the core configuration for the water quality monitoring api.
All the constraints, valid values and thresholds are defined here.
This means that changing a value here will update that value across
the entiere codebase.
"""

# Dataset
CSV_PATH = "data/water_quality.csv"

# Database
DATABASE_URL = "sqlite:///./water_quality.db"

# Valid metrics describe the core water quality sensor readings that will be
# used in the timeseries, summary and export endpoints.
# Unlike some other columns used throughout the backend, these columns are
# valid as a timeseries metric
VALID_METRICS = [
    "ph",
    "turbidity_ntu",
    "conductivity_uS_cm",
    "water_temperature_c",
    "water_level_cm",
    "light_lux",
]

# Weather context columns that will be available in export but not valid for
# a timeseries metric
WEATHER_COLUMNS = ["wx_temp_c", "wx_rh_pct", "wx_rain_mm_hr"]

# Alert flag columns - boolean indicators that're derived from sensor readings
ALERT_COLUMNS = [
    "alert_triggered",
    "alert_ph",
    "alert_turbidity",
    "alert_turbidity_crit",
    "alert_conductivity",
]

# Fault columns: our own self created columns that are used to identify and
# label sensor errors
FAULT_COLUMNS = ["sensor_fault", "fault_reason"]

# Valid time frequencies
VALID_FREQUENCIES = ["h", "D"]

# Status values that're used in the dataset
VALID_STATUSES = ["normal", "warning", "critical"]

# Data validation thresholds
PH_MIN = 0
PH_MAX = 14

TURBIDITY_MIN = 0
CONDUCTIVITY_MIN = 0

# Alert configuration
# Lebo Xhosa's acceptance criteria: alert triggers when reading deviates
# by more than 20% from the 24hr average
ALERT_DEVIATION_THRESHOLD = 0.2

# Configuration of export
# Jack Wilshere's acceptance criteria: exported file includes timestamps,
# site IDs and measurement values
EXPORT_COLUMNS = [
    "timestamp",
    "site_id",
    "ph",
    "turbidity_ntu",
    "conductivity_uS_cm",
    "water_temperature_c",
    "water_level_cm",
    "light_lux" "status",
    "alert_triggered",
    "alert_ph",
    "alert_turbidity",
    "alert_turbidity_crit",
    "alert_conductivity",
    "wx_temp_c",
    "wx_rh_pct",
    "wx_rain_mm_hr",
    "sensor_fault",
    "fault_reason",
]
