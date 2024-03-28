import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.express as px
from PredictionFunction.Datasets.Concerts.concerts import sentrum_scene_oslo
from PredictionFunction.utils.utils import calculate_days_30, custom_regressor, calculate_days_15
from PredictionFunction.Datasets.Regressors.weather_regressors import (
    heavy_rain_fall_weekday, 
    heavy_rain_fall_weekend, 
    heavy_rain_spring_weekday,
    heavy_rain_spring_weekend,
    heavy_rain_winter_weekday,
    ## there hasnt been any instances of heavy rain winter weekend for torggata yet. Test later
    # heavy_rain_winter_weekend,
    heavy_rain_fall_weekday_future,
    heavy_rain_fall_weekend_future,
    heavy_rain_spring_weekday_future,
    heavy_rain_spring_weekend_future,
    heavy_rain_winter_weekday_future,
    # heavy_rain_winter_weekend_future,
    # warm_dry_weekday_spring,
    # warm_dry_weekday_spring_future,
    # warm_dry_weekend_spring,
    # warm_dry_weekend_spring_future,
    # warm_dry_weekend_fall,
    # warm_dry_weekend_fall_future,
    # warm_dry_weekday_fall,
    # warm_dry_weekday_fall_future,
    )

from PredictionFunction.Datasets.OpeningHours.lostacos_opening_hours import restaurant_opening_hours
from PredictionFunction.Datasets.Regressors.general_regressors import (
    is_specific_month,
    is_covid_restriction_christmas,
    is_fall_start,
    is_christmas_shopping,
    )
from PredictionFunction.Datasets.Holidays.LosTacos.dataset_holidays import (
    last_working_day,
    fifteenth_working_days,
    ullevaal_big_football_games,
    fornebu_large_concerts,
)

from PredictionFunction.Datasets.Holidays.LosTacos.Restaurants.oslo_torggata_holidays import (
    christmas_day,
    # firstweek_jan,
    # new_years_day,
    # first_may,
    seventeenth_may,
    easter_weekend,
    easter_mondaydayoff,
    # pinse,
    # himmelfart,
    bondens_matfest_youngstorget,
    twentysecond_july_youngstorget,
    oktoberfest_youngstorget,
    closed_days,
)

from PredictionFunction.Datasets.Holidays.LosTacos.common_oslo_holidays import (
    firstweek_jan,
    new_years_day,
    first_may,
    easter_mondaydayoff,
    pinse,
    himmelfart,
    lockdown,
    oslo_pride,
)

from PredictionFunction.Datasets.Holidays.LosTacos.common_holidays import (
    halloween_day,
    halloween_weekend,
)
from PredictionFunction.utils.fetch_events import fetch_events

def oslo_torggata(prediction_category,restaurant,merged_data,historical_data,future_data):
    # Import sales data
    sales_data_df = historical_data
    sales_data_df = sales_data_df.rename(columns={"date": "ds"})

    future_data = future_data.rename(columns={"date": "ds"})

    merged_data = merged_data.rename(columns={"date": "ds"})
    sales_data_df["ds"] = pd.to_datetime(sales_data_df["ds"])

    # Add weather parameters to df
    # df = add_weather_parameters(sales_data_df, prediction_category)

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

    # Apply weather regressions
    df = heavy_rain_spring_weekend(df)
    df = heavy_rain_spring_weekday(df)
    df = heavy_rain_fall_weekend(df)
    df = heavy_rain_fall_weekday(df)
    # df = heavy_rain_winter_weekend(df)
    df = heavy_rain_winter_weekday(df)
    # df = warm_dry_weekend_spring(df)
    # df = warm_dry_weekday_spring(df)
    # df = warm_dry_weekend_fall(df)




    # Initialize Prophet
    m = Prophet()

    ### Add holidays and other repeating outliers
    m.add_country_holidays(country_name="NO")

    holidays = pd.concat(
        (
            christmas_day,
            firstweek_jan,
            first_may,
            easter_weekend,
            easter_mondaydayoff,
            seventeenth_may,
            pinse,
            himmelfart,
            lockdown,
            closed_days,
            bondens_matfest_youngstorget,
            twentysecond_july_youngstorget,
            oktoberfest_youngstorget,
            halloween_weekend,
            halloween_day,
        )
    )

    # Add regressor that captures payday effect before and after the payday
    # Let's create additional regressors for the days before, on and after payday
    df["before_payday"] = 0
    df["on_payday"] = 0
    df["after_payday"] = 0

    # Define number of days before payday to start linear decrease and after payday to end exponential decrease
    n_days_before = 4
    n_days_after = 4

    df["ds"] = pd.to_datetime(df["ds"])  # Convert 'ds' column to Timestamp
    # Update regressor columns
    for i in range(len(df)):
        for pay_day in last_working_day:
            pay_day = pd.to_datetime(pay_day)  # Convert pay_day to datetime
            # Check if date is in the window before payday
            if (
                df.loc[i, "ds"] > (pay_day - pd.Timedelta(days=n_days_before))
                and df.loc[i, "ds"] < pay_day
            ):
                df.loc[i, "before_payday"] = (
                    pay_day - df.loc[i, "ds"]
                ).days / n_days_before
            # Check if date is on payday
            elif df.loc[i, "ds"] == pay_day:
                df.loc[i, "on_payday"] = 1
            # Check if date is in the window after payday
            elif df.loc[i, "ds"] > pay_day and df.loc[i, "ds"] < (
                pay_day + pd.Timedelta(days=n_days_after)
            ):
                df.loc[i, "after_payday"] = np.exp(
                    -(df.loc[i, "ds"] - pay_day).days
                )  # exponential decay

    # Add custom monthly seasonalities for a specific month


    df["specific_month"] = df["ds"].apply(is_specific_month)

    # Define a function to check if the date is within the period of heavy COVID restrictions
    # def is_covid_restriction_christmas(ds):
    #     date = pd.to_datetime(ds)
    #     start_date = pd.to_datetime(
    #         "2021-12-13"
    #     )  # replace with the start date of the restriction period
    #     end_date = pd.to_datetime(
    #         "2022-01-09"
    #     )  # replace with the end date of the restriction period
    #     return start_date <= date <= end_date

    # Add new columns in your dataframe to indicate if a date is within or outside the restrictions period
    df["covid_restriction_christmas"] = df["ds"].apply(is_covid_restriction_christmas)

    # Some weeks have the same weekly seasonality but more extreme and just higher. Add that here
    # Convert 'ds' column to datetime if it is not already
    df["ds"] = pd.to_datetime(df["ds"])
    # Calculate the week number for each date
    df["week_number"] = df["ds"].dt.isocalendar().week

    # pattern august-sept
    # Convert 'ds' column to datetime if it is not already
    df["ds"] = pd.to_datetime(df["ds"])

    # Define the start and end dates for the specific date interval
    start_date = "2022-08-15"
    end_date = "2022-09-18"
    # make start_date and end:date datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Create a mask for the specific date interval
    date_mask = (df["ds"] >= start_date) & (df["ds"] <= end_date)

    # Calculate the week number for the start and end dates
    start_week = pd.to_datetime(start_date).week
    end_week = pd.to_datetime(end_date).week

    # Calculate the week number for each date
    df["week_number"] = df["ds"].dt.isocalendar().week

    # Define a function to calculate the custom regressor value based on the week number

    # Calculate the custom regressor values for the specific date interval
    df.loc[date_mask, "custom_regressor"] = df.loc[date_mask, "week_number"].apply(
        custom_regressor
    )

    # Fill the custom regressor with zeros for the rows outside the specific date interval
    df.loc[~date_mask, "custom_regressor"] = 0

    # Different weekly seasonality for 2 weeks in august related to starting fall semester/work


    df["fall_start"] = df["ds"].apply(is_fall_start)

    df["christmas_shopping"] = df["ds"].apply(is_christmas_shopping)

    # Event regressors here

    # Sentrum scene concerts regressor
    # Convert date strings to datetime format and create separate columns for each weekday
    # after testing, it seems there is only an effect on sun, monn and tue
    sentrum_scene_oslo_df = fetch_events("Oslo Torggata","Sentrum Scene")
    sentrum_scene_oslo_df["date"] = pd.to_datetime(sentrum_scene_oslo_df["date"])
    sentrum_scene_oslo_df = sentrum_scene_oslo_df.drop_duplicates(subset='date')
    
    # Create separate columns for each weekday
    weekdays = ["Monday", "Tuesday", "Sunday"]
    for day in weekdays:
        sentrum_scene_oslo_df[f"sentrum_scene_concert_{day}"] = 0

    for index, row in sentrum_scene_oslo_df.iterrows():
        day_of_week = row["date"].day_name()
        sentrum_scene_oslo_df.at[index, f"sentrum_scene_concert_{day_of_week}"] = 1

    df = pd.merge(df, sentrum_scene_oslo_df, how="left", left_on="ds", right_on="date")

    # I commented out this until we actually add for hours. This needs to be rewritten since we now to separate regressor for each weekday

    # if prediction_category == "hour":
    #   # print("Before assignment:", len(df[df['sentrum_scene_concerts'] == 1]))
    #   df.loc[~((df['hour'] == 20)), 'sentrum_scene_concerts'] = 0
    #   #df.loc[~((df['hour'] == 20) | (df['hour'] == 22)), 'sentrum_scene_concerts'] = 0
    # # Fill missing values with 0
    # df['sentrum_scene_concerts'].fillna(0, inplace=True)
    # print(df[df['sentrum_scene_concerts'] != 0]['sentrum_scene_concerts'])

    ## calculating the paydays and the days before and after. Used in regressions

    # The training DataFrame (df) should also include 'days_since_last' and 'days_until_next' columns.
    df = calculate_days_30(df, fifteenth_working_days)

    def is_high_weekends(ds):
        date = pd.to_datetime(ds)
        return date.month > 8 or date.month < 2

    df["high_weekend"] = df["ds"].apply(is_high_weekends)
    df["low_weekend"] = ~df["ds"].apply(is_high_weekends)

    # create daily seasonality column setting a number for each day of the week, to be used later
    # Create a Boolean column for each weekday
    for weekday in range(7):
        df[f"weekday_{weekday}"] = df["ds"].dt.weekday == weekday

    # Add the custom regressor and seasonalities before fitting the model
    if prediction_category == "hour":
        m = Prophet(
            holidays=holidays,
            weekly_seasonality=False,
            yearly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.1,
        )

        # Add a conditional seasonality for each weekday
        for weekday in range(7):
            m.add_seasonality(
                name=f"hourly_weekday_{weekday}",
                period=1,
                fourier_order=10,
                condition_name=f"weekday_{weekday}",
            )

    else:
        m = Prophet(
            holidays=holidays,
            yearly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.1,
        )

    # Add the payday columns as regressors
    m.add_regressor("days_since_last_30")
    m.add_regressor("days_until_next_30")

    ### Add events and concert regressors here

    # Sentrum scene
    # Add each weekday as a separate regressor
    weekdays = ["Monday", "Tuesday", "Sunday"]
    for day in weekdays:
        df[f"sentrum_scene_concert_{day}"].fillna(0, inplace=True)
        m.add_regressor(f"sentrum_scene_concert_{day}")

    m.add_regressor("custom_regressor")
    # m.add_regressor('covid_restriction')

    # Weather regressors
    # Add the 'warm_and_dry' and 'cold_and_wet' as additional regressors
    m.add_regressor('heavy_rain_fall_weekday')
    m.add_regressor('heavy_rain_fall_weekend')
    m.add_regressor('heavy_rain_spring_weekday')
    m.add_regressor('heavy_rain_spring_weekend')
    m.add_regressor('heavy_rain_winter_weekday')
    # m.add_regressor('warm_dry_weekend_spring')
    # m.add_regressor('warm_dry_weekday_spring')
    # m.add_regressor('warm_dry_weekend_fall')

    # m.add_regressor('heavy_rain_winter_weekend')

    m.add_seasonality(
        name="monthly", period=30.5, fourier_order=5, condition_name="specific_month"
    )
    # add daily seasonality when prediction type is hour

    m.add_seasonality(
        name="high_weekend", period=7, fourier_order=5, condition_name="high_weekend"
    )

    m.add_seasonality(
        name="covid_restriction_christmas",
        period=7,
        fourier_order=1000,
        condition_name="covid_restriction_christmas",
    )

    m.add_seasonality(
        name="weekly_fall_start", period=7, fourier_order=3, condition_name="fall_start"
    )

    m.add_seasonality(
        name="christmas_shopping",
        period=7,
        fourier_order=3,
        condition_name="christmas_shopping",
    )

    # Add the conditional regressor to the model
    # m.add_regressor('sunshine_amount', standardize=False)
    if prediction_category == "hour":
        df["ds"] = pd.to_datetime(
            df["ds"].astype(str) + " " + df["hour"].astype(str) + ":00:00"
        )
        weekday_mask = df["ds"].dt.weekday < 5  # Monday to Thursday
        weekend_mask = df["ds"].dt.weekday >= 5  # Saturday and Sunday

        df_weekday = df[weekday_mask]
        df_weekend = df[weekend_mask]
        # print(df_weekday)
        # print(df_weekend)
        # Set the hours dynamically based on the day of the week
        df_weekday = df_weekday[
            (
                df_weekday["ds"].dt.hour
                >= int(restaurant_hours["Oslo Torggata"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Oslo Torggata"]["weekday"]["ending"])
            )
        ]

        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Oslo Torggata"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Oslo Torggata"]["weekend"]["ending"])
            )
        ]

        # Concatenate the weekday and weekend DataFrames
        df = pd.concat([df_weekday, df_weekend])
    m.fit(df)

    if prediction_category == "hour":
        future = m.make_future_dataframe(periods=700, freq="H")
        # Add the Boolean columns for each weekday to the future DataFrame
        for weekday in range(7):
            future[f"weekday_{weekday}"] = future["ds"].dt.weekday == weekday

    else:
        future = m.make_future_dataframe(periods=60, freq="D")

    if prediction_category == "hour":
        weekday_mask = future["ds"].dt.weekday < 5  # Monday to Thursday
        weekend_mask = future["ds"].dt.weekday >= 5  # Saturday and Sunday

        df_weekday = future[weekday_mask]
        df_weekend = future[weekend_mask]
        # print(df_weekday)
        # print(df_weekend)
        # Set the hours dynamically based on the day of the week
        df_weekday = df_weekday[
            (
                df_weekday["ds"].dt.hour
                >= int(restaurant_hours["Oslo Torggata"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Oslo Torggata"]["weekday"]["ending"])
            )
        ]

        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Oslo Torggata"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Oslo Torggata"]["weekend"]["ending"])
            )
        ]

        # Concatenate the weekday and weekend DataFrames
        future = pd.concat([df_weekday, df_weekend])

    # Add weather future df
    future.dropna(inplace=True)

    # Add relevant weather columns to the future df
    future["rain_sum"] = merged_data["rain_sum"]
    future["sunshine_amount"] = merged_data["sunshine_amount"]
    future["windspeed"] = merged_data["windspeed"]
    future["air_temperature"] = merged_data["air_temperature"]

    # Apply the future functions for weather regressions here
    future = heavy_rain_spring_weekend_future(future)
    future = heavy_rain_spring_weekday_future(future)
    future = heavy_rain_fall_weekend_future(future)
    future = heavy_rain_fall_weekday_future(future)
    # future = heavy_rain_winter_weekend_future(future)
    future = heavy_rain_winter_weekday_future(future)
    # future = warm_dry_weekday_spring_future(future)
    # future = warm_dry_weekend_spring_future(future)
    # future = warm_dry_weekend_fall_future(future)





    # add the last working day and the +/- 5 days
    future = calculate_days_30(future, last_working_day)

    # Adding events

    for day in weekdays:
        # Merge the future dataframe with the sentrum_scene_oslo_df for the specific day
        future = pd.merge(
            future,
            sentrum_scene_oslo_df[["date", f"sentrum_scene_concert_{day}"]],
            how="left",
            left_on="ds",
            right_on="date",
        )
        # Fill missing values with 0
        future[f"sentrum_scene_concert_{day}"].fillna(0, inplace=True)
        # Drop the date column
        future.drop("date", axis=1, inplace=True)

    merged_data["ds"] = pd.to_datetime(merged_data["ds"], format="%Y", errors="coerce")

    future["high_weekend"] = future["ds"].apply(is_high_weekends)
    future["covid_restriction_christmas"] = future["ds"].apply(
        is_covid_restriction_christmas
    )
    future["fall_start"] = future["ds"].apply(is_fall_start)
    future["christmas_shopping"] = future["ds"].apply(is_christmas_shopping)
    future["specific_month"] = future["ds"].apply(is_specific_month)
    # Calculate the custom regressor values for the future dates
    future["ds"] = pd.to_datetime(future["ds"])
    future_date_mask = (future["ds"] >= start_date) & (future["ds"] <= end_date)
    future["week_number"] = future["ds"].dt.isocalendar().week
    future.loc[future_date_mask, "custom_regressor"] = future.loc[
        future_date_mask, "week_number"
    ].apply(custom_regressor)
    future.loc[~future_date_mask, "custom_regressor"] = 0

    # Add the 'sunshine_amount' column to the future dataframe
    if prediction_category != "hour":
        future["ds"] = future["ds"].dt.date
    future = future.drop_duplicates(subset='ds')
    future.fillna(0, inplace=True)
    
    return m, future, df


def location_function(prediction_category,restaurant,merged_data,historical_data,future_data):
    return oslo_torggata(prediction_category,restaurant,merged_data,historical_data,future_data)