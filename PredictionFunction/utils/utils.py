import pandas as pd


def calculate_days_30(df, last_working_day):
    # Convert 'ds' column to datetime if it's not already
    df["ds"] = pd.to_datetime(df["ds"])

    # Convert last_working_day list to datetime
    last_working_day = pd.to_datetime(pd.Series(last_working_day))

    df["days_since_last_30"] = df["ds"].apply(
        lambda x: min([abs(x - y).days for y in last_working_day if x >= y],default =0)
    )
    df["days_until_next_30"] = df["ds"].apply(
        lambda x: min([abs(x - y).days for y in last_working_day if x <= y],default=0)
    )

    # Set 'days_since_last' and 'days_until_next' to 0 for days that are not within the -5 to +5 range
    df.loc[df["days_since_last_30"] > 5, "days_since_last_30"] = 0
    df.loc[df["days_until_next_30"] > 5, "days_until_next_30"] = 0

    return df


def early_semester(ds, params):
    max_value, start_date_early_semester, end_date_early_semester = params
    date = pd.to_datetime(ds)
    if start_date_early_semester <= date <= end_date_early_semester:
        duration = (end_date_early_semester - start_date_early_semester).days
        elapsed_days = (date - start_date_early_semester).days
        return max_value * (1 - (elapsed_days / duration))
    else:
        return 0


def calculate_days_15(df, fifteenth_working_days):
    # Convert 'ds' column to datetime if it's not already
    df["ds"] = pd.to_datetime(df["ds"])

    # Convert last_working_day list to datetime
    fifteenth_working_days = pd.to_datetime(pd.Series(fifteenth_working_days))

    df["days_since_last_15"] = df["ds"].apply(
              lambda x: min([abs(x - pd.to_datetime(y)).days for y in fifteenth_working_days if x >= pd.to_datetime(y)],default=0))
    df["days_until_next_15"] = df["ds"].apply(             
              lambda x: min([abs(x -pd.to_datetime(y)).days for y in fifteenth_working_days if x <= pd.to_datetime(y)],default=0)
        )

    # Set 'days_since_last' and 'days_until_next' to 0 for days that are not within the -5 to +5 range
    df.loc[df["days_since_last_15"] > 5, "days_since_last_15"] = 0
    df.loc[df["days_until_next_15"] > 5, "days_until_next_15"] = 0

    return df


def is_closed(ds):
    date = pd.to_datetime(ds)
    start_date = pd.Timestamp("2022-01-01")  # Replace with the closure start date
    end_date = pd.Timestamp("2022-02-28")  # Replace with the closure end date
    return start_date <= date <= end_date


def custom_regressor(week_number, abrupt_increase_week=1, decay_rate=0.3):
    if week_number == abrupt_increase_week:
        return 1
    elif week_number > abrupt_increase_week:
        return decay_rate ** (week_number - abrupt_increase_week)
    else:
        return 0


def is_within_hours(date_obj, opening_hour, closing_hour):
    hour_of_day = date_obj.time().hour
    # Adjust for closing times past midnight
    if closing_hour < opening_hour:
        if hour_of_day >= opening_hour or hour_of_day < closing_hour:
            return True
    else:
        if opening_hour <= hour_of_day < closing_hour:
            return True
    return False


tourist_data={
    "Oslo Storo":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Oslo City":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Oslo Torggata":{
        "July":"1",
        "June":"1",
        "August":"1",
    },    
    "Karl Johan":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Fredrikstad":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Pedersgata":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Oslo Lokka":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Stavanger":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Bergen":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Oslo Steen_Strom":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Sandnes":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
    "Oslo Smestad":{
        "July":"1",
        "June":"1",
        "August":"1",
    },
}