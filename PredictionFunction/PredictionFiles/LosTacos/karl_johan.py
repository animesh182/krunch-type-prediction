import pandas as pd
import logging
from prophet import Prophet
from PredictionFunction.Datasets.OpeningHours.lostacos_opening_hours import restaurant_opening_hours
import numpy as np
from PredictionFunction.Datasets.Regressors.general_regressors import (
    is_specific_month,
    is_covid_restriction_christmas,
    is_closed,
    is_fall_start,
    is_christmas_shopping,
    is_campaign_active,
    is_high_weekends,
)
from PredictionFunction.Datasets.Holidays.LosTacos.dataset_holidays import (
    last_working_day,
    fifteenth_working_days,
    fornebu_large_concerts,
    ullevaal_big_football_games,
)
from PredictionFunction.Datasets.Concerts.concerts import oslo_spektrum,sentrum_scene_oslo
from PredictionFunction.utils.fetch_events import fetch_events
from PredictionFunction.Datasets.Regressors.weather_regressors import (
    # warm_dry_weather_spring,
    # warm_and_dry_future,
    heavy_rain_fall_weekday,
    heavy_rain_fall_weekend,
    heavy_rain_spring_weekday,
    heavy_rain_spring_weekend,
    # heavy_rain_winter_weekday,
    ## there hasnt been any instances of heavy rain winter weekend for torggata yet. Test later
    # heavy_rain_winter_weekend,
    heavy_rain_fall_weekday_future,
    heavy_rain_fall_weekend_future,
    heavy_rain_spring_weekday_future,
    heavy_rain_spring_weekend_future,
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
from PredictionFunction.Datasets.Holidays.LosTacos.dataset_holidays import (
    last_working_day,
    fifteenth_working_days,
)
from PredictionFunction.Datasets.Holidays.LosTacos.Restaurants.karl_johan_holidays import (
    by_larm,
    oya,
    tons_of_rock,
    findings,
    # firstweek_jan,
    # new_years_day,
    # first_may,
    seventeenth_may,
    easter,
    easter_lowsaturday,
    easter_mondaydayoff,
    # pinse,
    # himmelfart,
    norway_cup,
    closed_days,
    black_friday,
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
    hostferie_sor_ostlandet_weekdend,
    first_weekend_christmas_school_vacation,
)

from PredictionFunction.utils.utils import calculate_days_30, calculate_days_15, custom_regressor

# from Predictions.models import MarketingCampaigns
import xgboost as xgb
# from Predictions.models import MarketingCampaignTypes

# from Predictions.models import MarketingCampaignTypes, MarketingCampaigns
from datetime import date

# campaign_data = pd.DataFrame(
#     list(
#         MarketingCampaigns.objects.values("campaign_type__name", "startdate", "enddate")
#     )
# )


def karl_johan(prediction_category,restaurant,merged_data,historical_data,future_data):
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
    # df['y'] = np.log(df['y'])
    else:
        raise ValueError(f"Unexpected prediction_category value: {prediction_category}")
    # fig = px.histogram(df, x="y")
    # fig.show()
    df = heavy_rain_spring_weekend(df)
    df = heavy_rain_spring_weekday(df)
    df = heavy_rain_fall_weekend(df)
    df = heavy_rain_fall_weekday(df)
    # df = heavy_rain_winter_weekend(df)
    # df = heavy_rain_winter_weekday(df)
    # df = warm_dry_weather_spring(df)
    df = calculate_days_15(df, fifteenth_working_days)
    # df = non_heavy_rain_fall_weekend(df)

    m = Prophet()

    ### Holidays and other repeating outliers
    m.add_country_holidays(country_name="NO")

    christmas_day = pd.DataFrame(
        {
            "holiday": "christmas eve",
            "ds": pd.to_datetime(["2022-12-24"]),
            "lower_window": -5,
            "upper_window": 0,
        }
    )

    holidays = pd.concat(
        (
            christmas_day,
            firstweek_jan,
            easter,
            first_may,
            easter_lowsaturday,
            easter_mondaydayoff,
            seventeenth_may,
            pinse,
            himmelfart,
            lockdown,
            closed_days,
            tons_of_rock,
            oya,
            by_larm,
            findings,
            norway_cup,
            black_friday,
            halloween_weekend,
            halloween_day,
            hostferie_sor_ostlandet_weekdend,
            first_weekend_christmas_school_vacation,
        )
    )
    # Didnt use, because the effect was too small or looked incorrect: piknik_i_parken,inferno

    df["specific_month"] = df["ds"].apply(is_specific_month)

    # Add new columns in your dataframe to indicate if a date is within or outside the restrictions period
    df["covid_restriction_christmas"] = df["ds"].apply(is_covid_restriction_christmas)

    df["closed_jan"] = df["ds"].apply(is_closed)

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

    df["fall_start"] = df["ds"].apply(is_fall_start)

    df["christmas_shopping"] = df["ds"].apply(is_christmas_shopping)
    # Fornebu concerts as regressor (Oslo)
    fornebu_large_concerts_df = fetch_events("Karl Johan","Fornebu")
    fornebu_large_concerts_df = pd.DataFrame(fornebu_large_concerts_df) 
    fornebu_large_concerts_df = fornebu_large_concerts_df[["date","name"]]
    fornebu_large_concerts_df = fornebu_large_concerts_df.drop_duplicates(subset='date')
 
    fornebu_large_concerts_df["date"] = pd.to_datetime(
        fornebu_large_concerts_df["date"]
    )
    # Rename the columns to match the existing DataFrame
    fornebu_large_concerts_df.columns = ["ds", "event"]
    # Create a new column for the event
    fornebu_large_concerts_df["fornebu_large_concerts"] = 1
    # Merge the new dataframe with the existing data
    df = pd.merge(df, fornebu_large_concerts_df, how="left", on="ds")
    # Fill missing values with 0
    df["fornebu_large_concerts"].fillna(0, inplace=True)

    # Ullevål big concerts regressor (Oslo)
    ullevaal_big_football_games_df = fetch_events("Karl Johan","Ulleval")
    ullevaal_big_football_games_df = pd.DataFrame(ullevaal_big_football_games_df)  
    ullevaal_big_football_games_df["date"] = pd.to_datetime(
        ullevaal_big_football_games_df["date"]
    )
    ullevaal_big_football_games_df = ullevaal_big_football_games_df.drop_duplicates(subset='date')

    # Rename the columns to match the existing DataFrame\
    ullevaal_big_football_games_df = ullevaal_big_football_games_df[["date","name"]]

    ullevaal_big_football_games_df.columns = ["ds", "event"]
    # Create a new column for the event
    ullevaal_big_football_games_df["ullevaal_big_football_games"] = 1
    # Merge the new dataframe with the existing data
    df = pd.merge(df, ullevaal_big_football_games_df, how="left", on="ds")
    # Fill missing values with 0
    df["ullevaal_big_football_games"].fillna(0, inplace=True)

    # Oslo Spektrum large concerts
    oslo_spektrum = fetch_events("Karl Johan","Oslo Spektrum")
    oslo_spectrum_large_df = pd.DataFrame(oslo_spektrum) 
    oslo_spectrum_large_df = oslo_spectrum_large_df.rename(columns={"date": "ds"})
    oslo_spectrum_large_df["ds"] = pd.to_datetime(oslo_spectrum_large_df["ds"])
    oslo_spectrum_large_df = oslo_spectrum_large_df.drop_duplicates(subset='ds')

    oslo_spectrum_large_df["oslo_spektrum_large_concert"] = 1
    oslo_spectrum_large_df = oslo_spectrum_large_df[
        ["ds", "name", "oslo_spektrum_large_concert"]
    ]

    # Merge the new dataframe with the existing data
    df = pd.merge(df, oslo_spectrum_large_df, how="left", on=["ds"])

    # Fill missing values with 0
    df["oslo_spektrum_large_concert"].fillna(0, inplace=True)

    # Sentrum scene concerts regressor
    # Convert date strings to datetime format and create separate columns for each weekday
    # after testing, it seems there is only an effect on sun, monn and tue
    sentrum_scene_oslo_df = fetch_events("Karl Johan","Sentrum Scene")
    sentrum_scene_oslo_df["date"] = pd.to_datetime(sentrum_scene_oslo_df["date"])
    sentrum_scene_oslo_df = sentrum_scene_oslo_df.drop_duplicates(subset='date')

    # def is_campaign_active(ds, campaign_row):
    #      date = pd.to_datetime(ds)
    #      return 1 if pd.to_datetime(campaign_row['startdate']) <= date <= pd.to_datetime(campaign_row['enddate']) else 0

    # Apply the function to the historical data
    # for _, row in campaign_data.iterrows():
    #     campaign_type = row["campaign_type__name"]
    #     # if 'Red Bull Campaign Foodora/Wolt' in campaign_type:

    #     df[f"campaign_{campaign_type}"] = df["ds"].apply(
    #         lambda ds: is_campaign_active(ds, row)
    #     )

    # Create separate columns for each weekday
    weekdays = ["Monday", "Tuesday", "Sunday"]
    for day in weekdays:
        sentrum_scene_oslo_df[f"sentrum_scene_concert_{day}"] = 0

    for index, row in sentrum_scene_oslo_df.iterrows():
        day_of_week = row["date"].day_name()
        sentrum_scene_oslo_df.at[index, f"sentrum_scene_concert_{day_of_week}"] = 1

    df = pd.merge(df, sentrum_scene_oslo_df, how="left", left_on="ds", right_on="date")

    df["high_weekend"] = df["ds"].apply(is_high_weekends)
    df["low_weekend"] = ~df["ds"].apply(is_high_weekends)

    # The training DataFrame (df) should also include 'days_since_last' and 'days_until_next' columns.
    df = calculate_days_30(df, last_working_day)

    # The training DataFrame (df) should also include 'days_since_last' and 'days_until_next' columns.
    # df = calculate_days_15(df, fifteenth_working_days)

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

    # Weather regressors
    # Add the 'warm_and_dry' and 'cold_and_wet' as additional regressors
    m.add_regressor("heavy_rain_fall_weekday")
    m.add_regressor("heavy_rain_fall_weekend")
    m.add_regressor("heavy_rain_spring_weekday")
    m.add_regressor("heavy_rain_spring_weekend")
    # m.add_regressor('heavy_rain_winter_weekday')
    # m.add_regressor('heavy_rain_winter_weekend')
    # m.add_regressor('warm_dry_weekday_spring')
    # m.add_regressor('warm_dry_weekend_spring')
    # m.add_regressor('warm_dry_weekend_fall')

    # Add the payday columns as regressors
    m.add_regressor("days_since_last_30")
    m.add_regressor("days_until_next_30")
    # m.add_regressor("days_since_last_15")
    # for _, row in campaign_data.iterrows():
    #     campaign_type = row["campaign_type__name"]
    #     # if 'Red Bull Campaign Foodora/Wolt' in campaign_type:

    #     m.add_regressor(f"campaign_{campaign_type}")
    # print(f"the extra regressor are : {m.extra_regressors}")
    # Add the Fornebu concerts regressor
    m.add_regressor("fornebu_large_concerts")
    # Add the Ullevåål big football games  regressor
    m.add_regressor("ullevaal_big_football_games")
    # Add the Osloe Spektrum regressor
    m.add_regressor("oslo_spektrum_large_concert")

    # Sentrum scene
    # Add each weekday as a separate regressor
    weekdays = ["Monday", "Tuesday", "Sunday"]
    for day in weekdays:
        df[f"sentrum_scene_concert_{day}"].fillna(0, inplace=True)
        m.add_regressor(f"sentrum_scene_concert_{day}")

    # m.add_regressor('sunshine_amount', standardize=False)

    m.add_regressor("custom_regressor")
    # m.add_regressor('covid_restriction')
    m.add_regressor("closed_jan")
    m.add_seasonality(
        name="monthly", period=30.5, fourier_order=2, condition_name="specific_month"
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

    m.add_seasonality(
        name="high_weekend", period=7, fourier_order=5, condition_name="high_weekend"
    )

    if prediction_category == "hour":
        df["ds"] = pd.to_datetime(
            df["ds"].astype(str) + " " + df["hour"].astype(str) + ":00:00"
        )
        weekday_mask = df["ds"].dt.weekday < 5  # Monday to Friday
        weekend_mask = df["ds"].dt.weekday >= 5  # Saturday and Sunday

        df_weekday = df[weekday_mask]
        df_weekend = df[weekend_mask]
        # print(df_weekday)
        # print(df_weekend)
        # Set the hours dynamically based on the day of the week
        df_weekday = df_weekday[
            (
                df_weekday["ds"].dt.hour
                >= int(restaurant_hours["Karl Johan"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Karl Johan"]["weekday"]["ending"])
            )
        ]

        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Karl Johan"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Karl Johan"]["weekend"]["ending"])
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
        weekday_mask = future["ds"].dt.weekday < 5  # Monday to Friday
        weekend_mask = future["ds"].dt.weekday >= 5  # Saturday and Sunday

        df_weekday = future[weekday_mask]
        df_weekend = future[weekend_mask]
        df_weekday = df_weekday[
            (
                df_weekday["ds"].dt.hour
                >= int(restaurant_hours["Karl Johan"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Karl Johan"]["weekday"]["ending"])
            )
        ]
        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Karl Johan"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Karl Johan"]["weekend"]["ending"])
            )
        ]
        # Concatenate the weekday and weekend DataFrames
        future = pd.concat([df_weekday, df_weekend])

    # Add weather future df

    # Add relevant columns to the future df
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
    # future = heavy_rain_winter_weekday_future(future)
    # future = warm_dry_weather_spring(future)

    # add the last working day and the +/- 5 days
    future = calculate_days_30(future, last_working_day)
    # future = calculate_days_15(future, fifteenth_working_days)
    future["high_weekend"] = future["ds"].apply(is_high_weekends)
    future = pd.merge(
        future,
        fornebu_large_concerts_df[["ds", "fornebu_large_concerts"]],
        how="left",
        on="ds",
    )
    # Fill missing values with 0
    future["fornebu_large_concerts"].fillna(0, inplace=True)

    # Add Future df for Oslo Spektrum large concerts
    # Merge with the events data
    future = pd.merge(
        future,
        ullevaal_big_football_games_df[["ds", "ullevaal_big_football_games"]],
        how="left",
        on="ds",
    )
    # Fill missing values with 0
    future["ullevaal_big_football_games"].fillna(0, inplace=True)

    # Add Future df for Osloe Spektrum Large Concerts
    # Merge with the events data
    future = pd.merge(
        future,
        oslo_spectrum_large_df[["ds", "oslo_spektrum_large_concert"]],
        how="left",
        on="ds",
    )
    # Fill missing values with 0
    future["oslo_spektrum_large_concert"].fillna(0, inplace=True)

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

    future["covid_restriction_christmas"] = future["ds"].apply(
        is_covid_restriction_christmas
    )

    # for _, row in campaign_data.iterrows():
    #     campaign_type = row["campaign_type__name"]
    #     # if 'Red Bull Campaign Foodora/Wolt' in campaign_type:
    #     future[f"campaign_{campaign_type}"] = future["ds"].apply(
    #         lambda ds: is_campaign_active(ds, row)
    #     )

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
    future["closed_jan"] = future["ds"].apply(is_closed)

    # Add the 'sunshine_amount' column to the future dataframe
    if prediction_category != "hour":
        future["ds"] = future["ds"].dt.date
    future.fillna(0, inplace=True)

    return m, future, df


def location_function(prediction_category,restaurant,merged_data,historical_data,future_data):
    return karl_johan(prediction_category,restaurant,merged_data,historical_data,future_data)