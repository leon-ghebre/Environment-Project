"""
simulate_stream.py

Simulates a streaming sensor feed by importing water quality data
in small batches with a delay between each batch.

Persona coverage:
    - Lebo Xhosa: simulates continuous monitoring where new readings
      arrive every few minutes rather than a static dataset

    - George Weah: simulates live contamination data arriving during
      an active monitoring period
"""

import time
import pandas as pd

from config import CSV_PATH
from database.database import Base, SessionLocal, engine
from scripts.import_water import get_or_create_site, import_rows

BATCH_SIZE = 12
DELAY_SECONDS = 2


def main():
    """Simulates a streaming sensor feed from the water quality CSV."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # create  or retrieve the monitoring sites.
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
        db.commit()

        # build a lookup disctionary so that import_rows()
        # can map site_code strings to their integer database IDs

        site_ids = {
            "site_upstream": site_upstream.id,
            "site_downstream": site_downstream.id,
            "site_reservoir": site_reservoir.id,
        }

        # load the full CSV into memory
        # dropna removes the rows with missing timestamps
        # drop_duplicates prevents importing the same reading twice
        df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
        df = df.dropna(subset=["timestamp"])
        df = df.drop_duplicates(subset=["site_id", "timestamp"], keep="first")
        df = df.sort_values("timestamp").reset_index(drop=True)

        total = len(df)

        # process the DataFrame in batches,
        #  each iteration simulates one burst of sensor data arriving
        for start in range(0, total, BATCH_SIZE):
            batch = df.iloc[start : start + BATCH_SIZE]
            import_rows(db, batch, site_ids)
            end = min(start + BATCH_SIZE, total)
            print(f"Imported rows {start} to {end} of {total}")
            # wait before the next batch to simulate real sensor timing
            #  then skip the delay after the final batch
            if end < total:
                time.sleep(DELAY_SECONDS)

        print("Stream simulation complete.")

    finally:
        # close db session
        db.close()


if __name__ == "__main__":
    main()
