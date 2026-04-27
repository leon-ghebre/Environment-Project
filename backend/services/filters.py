def filter_water_data(site_id, start_date=None, end_date=None): #function that filters water data by site and date range(if specified) and returns a filtered dataframe
    data = df[df["site_id"] == site_id].copy() #selects rows that pertain to the chosen site_id

    if start_date:
        data = data[data["timestamp"] >= pd.to_datetime(start_date)] #if start date is specified - filter rows after given start date

    if end_date:
        data = data[data["timestamp"] <= pd.to_datetime(end_date)] #if end date is specified - filter rows before given end date

    return data # return a filtered data frame