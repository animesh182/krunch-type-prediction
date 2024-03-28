import pandas as pd

FALL_START_DATES = {
        2022: {"start": "2022-08-08", "end": "2022-08-21"},
        2023: {"start": "2023-08-07", "end": "2023-08-20"},
        # Add more years and their respective dates as needed
    }
def is_fall_start(ds):
        date = pd.to_datetime(ds)
        year = date.year  # Extract the year from the input date

        if year not in FALL_START_DATES:
            return False  # or raise an error if you prefer

        start_date = pd.Timestamp(FALL_START_DATES[year]["start"])
        end_date = pd.Timestamp(FALL_START_DATES[year]["end"])

        return start_date <= date <= end_date
def is_first_two_weeks_january_21(ds):
        date = pd.to_datetime(ds)
        start_date = pd.Timestamp("2022-01-10")
        end_date = pd.Timestamp("2022-01-30")
        return start_date <= date <= end_date
def is_fellesferie(ds):
        date = pd.to_datetime(ds)
        start_date = pd.Timestamp("2022-07-04")
        end_date = pd.Timestamp("2022-08-07")
        return start_date <= date <= end_date
def is_specific_month(ds):
        date = pd.to_datetime(ds)
        start_date = pd.to_datetime(
            "2022-07-01"
        )  # replace with the start date of the interval
        end_date = pd.to_datetime(
            "2022-07-31"
        )  # replace with the end date of the interval
        return start_date <= date <= end_date
def is_covid_restriction_christmas(ds):
        date = pd.to_datetime(ds)
        start_date = pd.to_datetime(
            "2021-12-13"
        )  # replace with the start date of the restriction period
        end_date = pd.to_datetime(
            "2022-01-09"
        )  # replace with the end date of the restriction period
        return start_date <= date <= end_date
def is_christmas_shopping(ds):
        date = pd.to_datetime(ds)
        start_date = pd.Timestamp("2022-11-14")
        end_date = pd.Timestamp("2022-12-11")
        return start_date <= date <= end_date
def is_closed(ds):
        date = pd.to_datetime(ds)
        start_date = pd.Timestamp("2022-01-01")  # Replace with the closure start date
        end_date = pd.Timestamp("2022-02-28")  # Replace with the closure end date
        return start_date <= date <= end_date
def is_campaign_active(ds, campaign_row):
         date = pd.to_datetime(ds)
         return 1 if pd.to_datetime(campaign_row['startdate']) <= date <= pd.to_datetime(campaign_row['enddate']) else 0
def is_high_weekends(ds):
        date = pd.to_datetime(ds)
        return date.month > 8 or date.month < 2
def is_fellesferie_sandnes(ds):
        date = pd.to_datetime(ds)
        start_date = pd.Timestamp("2022-07-05")
        end_date = pd.Timestamp("2022-08-05")
        return start_date <= date <= end_date
def is_covid_loose_fall21(ds):
        date = pd.to_datetime(ds)
        start_date = pd.Timestamp("2021-09-20")
        end_date = pd.Timestamp("2021-10-31")
        return start_date <= date <= end_date
def is_fellesferie_stavanger(ds):
        date = pd.to_datetime(ds)
        start_date = pd.Timestamp("2022-07-05")
        end_date = pd.Timestamp("2022-08-05")
        return start_date <= date <= end_date
def is_may(ds):
        ds = pd.to_datetime(ds)
        return ds.month == 5
def is_saturday_rainy_windy(row):
        return 1 if(row['ds'].dayofweek == 5) and (row['rain_sum']>5) and (row['windspeed']>4.5) else 0