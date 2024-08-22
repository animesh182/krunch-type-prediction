import pandas as pd
import logging
from prophet import Prophet
import numpy as np
from PredictionFunction.utils.fetch_events import fetch_events
from PredictionFunction.Datasets.Regressors.weather_regressors import (
    warm_dry_weather_spring,
    # warm_and_dry_future,
    # heavy_rain_fall_weekday,
    heavy_rain_fall_weekend,
    # heavy_rain_spring_weekday,
    # heavy_rain_spring_weekend,
    # heavy_rain_winter_weekday,
    ## there hasnt been any instances of heavy rain winter weekend for torggata yet. Test later
    # heavy_rain_winter_weekend,
    # heavy_rain_fall_weekday_future,
    # heavy_rain_fall_weekend_future,
    # heavy_rain_spring_weekday_future,
    # heavy_rain_spring_weekend_future,
    # heavy_rain_winter_weekday_future,
    # heavy_rain_winter_weekend_future,
    # warm_dry_weekday_spring,
    # warm_dry_weekend_spring,
    # warm_dry_weekend_fall,
    # warm_dry_weather_spring,
    # warm_dry_weekday_spring_future,
    # warm_dry_weekend_spring_future,
    # warm_dry_weekend_fall_future,
)
from PredictionFunction.Datasets.Regressors.general_regressors import( 
    is_fall_start,
    is_fellesferie,
    # is_may
    )
from PredictionFunction.Datasets.Holidays.LosTacos.common_oslo_holidays import (
    firstweek_jan,
    oslo_pride,
    musikkfestival,
)

from PredictionFunction.Datasets.Holidays.LosTacos.common_holidays import (
    hostferie_sor_ostlandet_weekdend,
    first_weekend_christmas_school_vacation,
    seventeenth_may,
    easter,
    new_years_day,
    first_may,
    pinse,
    himmelfart,
    christmas_day,
    new_year_romjul
)
from PredictionFunction.utils.openinghours import add_opening_hours


def restaurantdrift(
    prediction_category, restaurant, merged_data, historical_data, future_data
):
    sales_data_df = historical_data
    sales_data_df = sales_data_df.rename(columns={"date": "ds"})

    future_data = future_data.rename(columns={"date": "ds"})

    merged_data = merged_data.rename(columns={"date": "ds"})

    sales_data_df["ds"] = pd.to_datetime(sales_data_df["ds"])
    sales_data_df["ds"] = pd.to_datetime(sales_data_df["ds"])

    if prediction_category == "day":
        df = (
            sales_data_df.groupby(["ds"])
            .agg(
                {
                    "total_net": "sum",
                    "sunshine_amount": "sum",
                    "rain_sum": "sum",
                    "windspeed": "mean",
                    "air_temperature": "mean",
                }
            )
            .reset_index()
        )
        df.fillna(
            {"sunshine_amount": 0, "rain_sum": 0, "windspeed": 0, "air_temperature": 0},
            inplace=True,
        )
        df.columns = [
            "ds",
            "y",
            "sunshine_amount",
            "rain_sum",
            "windspeed",
            "air_temperature",
        ]

    elif prediction_category == "hour":
        df = (
            sales_data_df.groupby(["ds", "hour"])
            .agg(
                {
                    "total_net": "sum",
                    "sunshine_amount": "sum",
                    "rain_sum": "sum",
                    "windspeed": "mean",
                    "air_temperature": "mean",
                }
            )
            .reset_index()
        )
        df.fillna(
            {"sunshine_amount": 0, "rain_sum": 0, "windspeed": 0, "air_temperature": 0},
            inplace=True,
        )
        df.columns = [
            "ds",
            "hour",
            "y",
            "sunshine_amount",
            "rain_sum",
            "windspeed",
            "air_temperature",
        ]

    elif prediction_category in ["type", "product"]:
        df = (
            sales_data_df.groupby(["ds"])
            .agg(
                {
                    "percentage": "max",
                    "sunshine_amount": "sum",
                    "rain_sum": "sum",
                    "windspeed": "mean",
                    "air_temperature": "mean",
                }
            )
            .reset_index()
        )
        df.fillna(
            {"sunshine_amount": 0, "rain_sum": 0, "windspeed": 0, "air_temperature": 0},
            inplace=True,
        )
        df.columns = [
            "ds",
            "y",
            "sunshine_amount",
            "rain_sum",
            "windspeed",
            "air_temperature",
        ]
    df = add_opening_hours(df, "Restaurantdrift AS", [12], [13,15,14,7])
    m = Prophet()

    ### Holidays and other repeating outliers
    m.add_country_holidays(country_name="NO")
    holidays = pd.concat(
        (
            christmas_day,
            firstweek_jan,
            easter,
            first_may,
            new_years_day,
            seventeenth_may,
            pinse,
            himmelfart,
            hostferie_sor_ostlandet_weekdend,
            first_weekend_christmas_school_vacation,
            oslo_pride,
            musikkfestival,
            christmas_day,
            new_year_romjul,
        )
    )
    df["ds"] = pd.to_datetime(df["ds"])
    df["week_number"] = df["ds"].dt.isocalendar().week
    df["is_fellesferie"] = df["ds"].apply(is_fellesferie)
    # df["high_weekend"] = df["ds"].apply(is_high_weekend_spring)
    df["fall_start"] = df["ds"].apply(is_fall_start)
    df = heavy_rain_fall_weekend(df)
    df = warm_dry_weather_spring(df)

    prediction_venues = {
        "Rockefeller",
        "Cosmopolite, Oslo",
        "Parkteatret Scene",
        "Nordic Black Theatre",
        "Oslo Concert Hall",
        # "Salt Langhuset",
        "Sofienbergparken",
        "Tons of Rock"
    }

    data = {"name": [], "effect": []}
    city='Oslo'
    venue_list = prediction_venues
    regressors_to_add = []
    for venue in prediction_venues:
        # for venue in karl_johan_venues:
        venue_df = fetch_events("Oslo Torggata", venue,city)
        if "name" in venue_df.columns:
            venue_df = venue_df.drop_duplicates("date")
            venue_df["date"] = pd.to_datetime(venue_df["date"])
            venue_df = venue_df.rename(columns={"date": "ds"})
            venue_df["ds"] = pd.to_datetime(venue_df["ds"])
            venue_df = venue_df[["ds", "name"]]
            venue_df.columns = ["ds", "event"]
            dataframe_name = venue.lower().replace(" ", "_").replace(",", "")
            venue_df[dataframe_name] = 1
            df = pd.merge(df, venue_df, how="left", on="ds", suffixes=("", "_venue"))
            df[dataframe_name].fillna(0, inplace=True)
            regressors_to_add.append(
                (venue_df, dataframe_name)
            )  # Append venue_df along with venue name for regressor addition
        else:
            holidays = pd.concat(objs=[holidays, venue_df], ignore_index=True)
    # holidays.to_csv('holidays.csv')
    m = Prophet(
        holidays=holidays,
        # yearly_seasonality=True,
        # weekly_seasonality=False,
        # daily_seasonality=False,
        changepoint_prior_scale=0.01,
        seasonality_mode="additive"
    )


    for event_df, regressor_name in regressors_to_add:
        if "event" in event_df.columns:
            m.add_regressor(regressor_name)

    # Weather regressors
    # m.add_regressor("sunshine_amount",standardize=False)
    m.add_regressor("rain_sum",standardize=False)
    m.add_regressor('heavy_rain_fall_weekend')
    m.add_regressor('warm_and_dry')
    # m.add_regressor('sunday_low_sales')
    # m.add_regressor("opening_duration")
    # m.add_regressor("fall_start")

    # m.add_seasonality(name="monthly", period=30.5, fourier_order=5)
    # m.add_seasonality(name="weekly", period=7, fourier_order=3)

    # m.add_seasonality(
    #     name="is_fellesferie",
    #     period=30.5,
    #     fourier_order=5,
    #     condition_name="is_fellesferie",
    # )

    m.fit(df)

    future = m.make_future_dataframe(periods=60, freq="D")

    # Add relevant columns to the future df
    future["rain_sum"] = merged_data["rain_sum"]
    future["sunshine_amount"] = merged_data["sunshine_amount"]
    future["windspeed"] = merged_data["windspeed"]
    future["air_temperature"] = merged_data["air_temperature"]

    future.fillna(
        {"sunshine_amount": 0, "rain_sum": 0, "windspeed": 0, "air_temperature": 0},
        inplace=True,
    )

    for event_df, event_column in regressors_to_add:
        if "event" in event_df.columns:
            event_df = event_df.drop_duplicates("ds")
            future = pd.merge(
                future,
                event_df[["ds", event_column]],
                how="left",
                on="ds",
            )
            future[event_column].fillna(0, inplace=True)

    # Apply the future functions for weather regressions here
    # future = heavy_rain_spring_weekend_future(future)
    future["is_fellesferie"] = future["ds"].apply(is_fellesferie)
    future["fall_start"] = future["ds"].apply(is_fall_start)
    future = heavy_rain_fall_weekend(future)
    future = warm_dry_weather_spring(future)

    merged_data["ds"] = pd.to_datetime(merged_data["ds"], format="%Y", errors="coerce")
    # Calculate the custom regressor values for the future dates
    future["ds"] = pd.to_datetime(future["ds"])

    future.fillna(0, inplace=True)
    future = add_opening_hours(future, "Restaurantdrift AS", [12], [13,15,14,7])
    # future.to_csv("future.csv")

    return m, future, df


def location_function(
    prediction_category, restaurant, merged_data, historical_data, future_data
):
    return restaurantdrift(
        prediction_category, restaurant, merged_data, historical_data, future_data
    )
