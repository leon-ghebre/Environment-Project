import pandas as pd
from config import CSV_PATH
df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])# Convert timestamp from a text format to a datetime format
df = df.sort_values("timestamp").reset_index(drop=True) #sort dataframe by time, then reset index