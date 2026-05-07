"""
import_water.py

Imports water quality CSV readings into the SQLite database

This script:
- creates database tables if they do not already exist
- loads water_quality.csv into the databse
- parses timestamps
- removes rows with missing timestamps
- skips duplicate site/timestamp readings
- inserts site and reading records into the database

"""

import pandas as pd

from config import CSV_PATH
from database.database import Base, SessionLocal, engine
from database.models import Site, WaterReading
from validation.import_validators import (
    clean_number,
    check_alert_flag,
    validate_row,
)
from services.alert_service import create_alert_events_for_reading


def get_or_create_site(db, site_code, name, description, latitude, longitude):
    """Returns an existing site or creates it if it does not exist
    which allows the database to be refreshed with new added data

    Args:
        db: active sqlalechemy database
        site_code: unique site identifier from the CSV file.
        name: site name
        description: short description of the monitoring site
        latitude: site's latidute
        longitude: site's longitude

    Returns:
        Site object from the database
    """
    existing_site = db.query(Site).filter(Site.site_code == site_code).first()

    if existing_site:
        return existing_site

    new_site = Site(
        site_code=site_code,
        name=name,
        description=description,
        latitude=latitude,
        longitude=longitude,
        is_active=True,
    )

    db.add(new_site)
    db.commit()
    db.refresh(new_site)

    return new_site


def main():
    # make sure the database tables exist before we try to insert data
    Base.metadata.create_all(bind=engine)

    # open a database sessoin
    db = SessionLocal()

    try:
        # read the CSV into a pandas dataframe
        df = pd.read_csv(CSV_PATH)

        # convert timestamps. invalid ones become NaT instead of crashing.
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        bad_timestamps = df["timestamp"].isna().sum()

        if bad_timestamps > 0:
            print(f"Skipped {bad_timestamps} rows with missing timestamps")

        df = df.dropna(subset=["timestamp"])  # if no timestamp, drop

        # remove exact duplicate readings for the same site and timestamp
        duplicates = df.duplicated(
            subset=["site_id", "timestamp"],
            keep="first",
        )
        duplicate_count = duplicates.sum()

        if duplicate_count > 0:
            print(f"Skipped {duplicate_count} duplicate rows")

        df = df.drop_duplicates(subset=["site_id", "timestamp"], keep="first")

        # create or update the the 3 real sites
        site_upstream = get_or_create_site(
            db,
            "site_upstream",
            "Upstream Site",
            "Reference point above agricultural land",
            -32.780,
            26.840,
        )

        site_downstream = get_or_create_site(
            db,
            "site_downstream",
            "Downstream Site",
            "Below farming activity",
            -32.785,
            26.845,
        )

        site_reservoir = get_or_create_site(
            db,
            "site_reservoir",
            "Reservoir Site",
            "Community dam",
            -32.790,
            26.850,
        )

        # after committing, the database gives these sites their IDs
        db.refresh(site_upstream)
        db.refresh(site_downstream)
        db.refresh(site_reservoir)

        # go through each row in the csv file

        for index, row in df.iterrows():

            # Work out which site this reading belongs to
            if row["site_id"] == "site_upstream":
                site_id_value = site_upstream.id
            elif row["site_id"] == "site_downstream":
                site_id_value = site_downstream.id
            elif row["site_id"] == "site_reservoir":
                site_id_value = site_reservoir.id
            else:
                continue

            # for refreshing database, dont add any duplicate times + sites
            existing_reading = (
                db.query(WaterReading)
                .filter(WaterReading.site_id == site_id_value)
                .filter(WaterReading.recorded_at == row["timestamp"])
                .first()
            )

            if existing_reading:
                continue

            # make sure no values are left blank
            ph_value = clean_number(row["ph"])
            turbidity_value = clean_number(row["turbidity_ntu"])
            conductivity_value = clean_number(row["conductivity_uS_cm"])
            water_temp_value = clean_number(row["water_temperature_c"])
            water_level_value = clean_number(row["water_level_cm"])
            light_value = clean_number(row["light_lux"])

            wx_temp_value = clean_number(row["wx_temp_c"])
            wx_rh_value = clean_number(row["wx_rh_pct"])
            wx_rain_value = clean_number(row["wx_rain_mm_hr"])

            # validate the measurements
            status_val, sensor_fault_val, fault_reason_val = validate_row(
                ph_value,
                turbidity_value,
                conductivity_value,
                water_temp_value,
                water_level_value,
                light_value,
                wx_temp_value,
                wx_rh_value,
                wx_rain_value,
                row["status"],
            )

            # validate the alerts
            alert_fault_reasons = []

            alert_triggered_value = check_alert_flag(
                row["alert_triggered"],
                "alert_triggered",
                alert_fault_reasons,
            )
            alert_ph_value = check_alert_flag(
                row["alert_ph"],
                "alert_ph",
                alert_fault_reasons,
            )
            alert_turbidity_value = check_alert_flag(
                row["alert_turbidity"],
                "alert_turbidity",
                alert_fault_reasons,
            )
            alert_turbidity_crit_value = check_alert_flag(
                row["alert_turbidity_crit"],
                "alert_turbidity_crit",
                alert_fault_reasons,
            )
            alert_conductivity_value = check_alert_flag(
                row["alert_conductivity"],
                "alert_conductivity",
                alert_fault_reasons,
            )

            # if there were any errors with the alerts update error
            # status and add reason
            if len(alert_fault_reasons) > 0:
                sensor_fault_val = True

                if fault_reason_val is None:
                    fault_reason_val = ", ".join(alert_fault_reasons)
                else:
                    new_reasons = ", ".join(alert_fault_reasons)
                    fault_reason_val += ", " + new_reasons

            # create one WaterReading object from this CSV row
            reading = WaterReading(
                site_id=site_id_value,
                recorded_at=row["timestamp"],
                ph=ph_value,
                turbidity_ntu=turbidity_value,
                conductivity_uS_cm=conductivity_value,
                water_temperature_c=water_temp_value,
                water_level_cm=water_level_value,
                light_lux=light_value,
                status=status_val,
                alert_triggered=alert_triggered_value,
                alert_ph=alert_ph_value,
                alert_turbidity=alert_turbidity_value,
                alert_turbidity_crit=alert_turbidity_crit_value,
                alert_conductivity=alert_conductivity_value,
                wx_temp_c=wx_temp_value,
                wx_rh_pct=wx_rh_value,
                wx_rain_mm_hr=wx_rain_value,
                sensor_fault=sensor_fault_val,
                fault_reason=fault_reason_val,
            )

            # Add this reading to the database session
            db.add(reading)

            # flush gives this reading an ID before the full commit which
            # is needed because alert_events.source_reading_id links to
            # reading.id
            db.flush()

            # create linked alert event rows if this reading triggered an alert
            # or failed validation.
            if reading.alert_triggered or reading.sensor_fault:
                create_alert_events_for_reading(db, reading)

            # commits every 1000 rows so memory does not grow too much
            if index % 1000 == 0:
                db.commit()
                print(f"Inserted {index} rows...")

        # Final commit for any remaining rows
        db.commit()

        print("Import finished successfully.")
        print(f"Total rows imported: {len(df)}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
