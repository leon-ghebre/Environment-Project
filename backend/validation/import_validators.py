"""
import_validators.py

Validation helpers used when importing water quality CSV readings
in scripts/import_water.py

These functions check missing values, alert flags, sensor ranges, and whether
the CSV status matches the expected alert threshold rules
(based on data/alert_rules.md)
"""

import pandas as pd

from config import (
    CONDUCTIVITY_MAX,
    CONDUCTIVITY_MIN,
    LIGHT_MAX,
    LIGHT_MIN,
    PH_MAX,
    PH_MIN,
    TURBIDITY_MAX,
    TURBIDITY_MIN,
    VALID_STATUSES,
    WATER_LEVEL_MAX,
    WATER_LEVEL_MIN,
    WATER_TEMP_MAX,
    WATER_TEMP_MIN,
    WX_RAIN_MAX,
    WX_RAIN_MIN,
    WX_RH_MAX,
    WX_RH_MIN,
    WX_TEMP_MAX,
    WX_TEMP_MIN,
)


def clean_number(value):
    """Convert missing pandas values into None for database storage

    Args:
        value: Value from a CSV row

    Returns:
        - Original value, or None if the value is missing
    """
    if pd.isna(value):
        return None

    return value


def calculate_status(ph, turbidity, conductivity):
    """Calculate water quality status from core sensor readings
    based of data/alert_rules.md

    Args:
        ph: pH reading
        turbidity: Turbidity reading in NTU
        conductivity: Conductivity reading in uS/cm

    Returns:
        Status string: normal, warning, or critical
    """
    critical = (
        (ph is not None and (ph < 6.0 or ph > 9.0))
        or (turbidity is not None and turbidity > 10)
        or (conductivity is not None and conductivity > 1500)
    )

    warning = (
        (ph is not None and (ph < 6.5 or ph > 8.5))
        or (turbidity is not None and turbidity > 5)
        or (conductivity is not None and conductivity > 500)
    )

    if critical:
        return "critical"

    if warning:
        return "warning"

    return "normal"


def check_alert_flag(value, column_name, fault_reasons):
    """Validate that an alert flag is either 0 or 1

    Args:
        value: Alert flag value from the CSV
        column_name: Name of the alert column being checked
        fault_reasons: List that validation messages are added to

    Returns:
        Boolean version of the alert flag
    """
    if pd.isna(value):
        fault_reasons.append(f"{column_name} is missing")
        return False

    if value in [0, 1]:
        return bool(value)

    fault_reasons.append(f"{column_name} must be 0 or 1")
    return False


def is_outside_range(value, minimum, maximum):
    """Returns True if a value exists but is outside range

    Args:
        value: value of measurement
        minimum: lowest acceptable value
        maximum: highest acceptable value

    Returns:
        Boolean of True if outside range, otherwise its False

    """

    if value is None:
        return False
    if value < minimum:
        return True
    if value > maximum:
        return True

    return False


def validate_row(
    ph,
    turbidity,
    conductivity,
    water_temp,
    water_level,
    light,
    wx_temp,
    wx_rh,
    wx_rain,
    og_status,
):
    """Validate one water quality row and confirm its status value

    Args:
        ph: pH reading
        turbidity: Turbidity reading in NTU
        conductivity: Conductivity reading in uS/cm
        water_temp: Water temperature reading
        water_level: Water levl reading
        light: Light reading in lux
        wx_temp: Weather temperature reading
        wx_rh: Weather relative humidity reading
        wx_rain: Weather rainfall reading
        og_status: Status value from the CSV

    Returns:
        tuple: Final status, sensor fault flag, and fault reason
    """
    fault_reasons = []

    if is_outside_range(ph, PH_MIN, PH_MAX):
        fault_reasons.append("pH outside possible range 0-14")

    if is_outside_range(turbidity, TURBIDITY_MIN, TURBIDITY_MAX):
        fault_reasons.append("turbidity outside expected range")

    if is_outside_range(conductivity, CONDUCTIVITY_MIN, CONDUCTIVITY_MAX):
        fault_reasons.append("conductivity outside expected range")

    if is_outside_range(water_temp, WATER_TEMP_MIN, WATER_TEMP_MAX):
        fault_reasons.append("water temperature outside expected range")

    if is_outside_range(water_level, WATER_LEVEL_MIN, WATER_LEVEL_MAX):
        fault_reasons.append("water level outside expected range")

    if water_level == 800.0:
        fault_reasons.append("water level sensor overflow — reading capped at 800cm")

    if is_outside_range(light, LIGHT_MIN, LIGHT_MAX):
        fault_reasons.append("light outside expected range")

    if is_outside_range(wx_temp, WX_TEMP_MIN, WX_TEMP_MAX):
        fault_reasons.append("weather temperature outside expected range")

    if is_outside_range(wx_rh, WX_RH_MIN, WX_RH_MAX):
        fault_reasons.append("relative humidity outside 0-100 range")

    if is_outside_range(wx_rain, WX_RAIN_MIN, WX_RAIN_MAX):
        fault_reasons.append("rainfall outside expected range")

    if fault_reasons:
        final_status = "warning"
    else:
        calculated_status = calculate_status(ph, turbidity, conductivity)

        if pd.isna(og_status) or og_status == "":
            fault_reasons.append("status is missing")
            final_status = calculated_status
        elif og_status not in VALID_STATUSES:
            fault_reasons.append("invalid status value")
            final_status = calculated_status
        elif og_status != calculated_status:
            fault_reasons.append("status does not match threshold rules")
            final_status = calculated_status
        else:
            final_status = og_status

    if fault_reasons:
        return final_status, True, ", ".join(fault_reasons)

    return final_status, False, None
