def get_trends(
    site_id, metric, freq="D", start_date=None, end_date=None
):  # gets trends for a specific time period
    data = filter_water_data(site_id, start_date, end_date)

    if data.empty:
        return pd.DataFrame()  # return empty result if no data found

    trend = (
        data.set_index("timestamp")  # make the timestamp the index
        .resample(freq)[metric]  # aggregates data into either 'h'(hour) or 'D'(day) time groups
        .agg(["mean", "min", "max"])  # calculates mean, minimum and maximum
        .reset_index()
    )
    trend = trend.rename(columns={"mean": "avg"})  # rename mean to avg
    return trend
