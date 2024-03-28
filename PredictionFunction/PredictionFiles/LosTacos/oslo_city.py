import pandas as pd
import numpy as np

from PredictionFunction.Datasets.Holidays.LosTacos.dataset_holidays import (
    last_working_day,
    fifteenth_working_days
)
from prophet import Prophet
import plotly.express as px
from PredictionFunction.Datasets.OpeningHours.lostacos_opening_hours import restaurant_opening_hours
from PredictionFunction.Datasets.Regressors.general_regressors import (
    is_specific_month,
    is_covid_restriction_christmas,
    is_fall_start,
    is_christmas_shopping,
    is_saturday_rainy_windy,
)
from PredictionFunction.utils.utils import custom_regressor, calculate_days_30, calculate_days_15
from PredictionFunction.Datasets.Holidays.LosTacos.Restaurants.oslo_city_holidays import (
    christmas_day,
    # firstweek_jan,
    # new_years_day,
    easter,
    easter_lowsaturday,
    easter_mondaydayoff,
    # pinse,
    day_before_red_day,
    # himmelfart,
    closed_days,
    norway_cup,
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
    first_weekend_christmas_school_vacation,
)
from PredictionFunction.Datasets.Regressors.weather_regressors import(
    warm_dry_weather_spring,
    warm_and_dry_future,
    # heavy_rain_fall_weekday,
    # heavy_rain_fall_weekday_future,
    heavy_rain_fall_weekend,
    heavy_rain_fall_weekend_future,
    heavy_rain_winter_weekday, 
    heavy_rain_winter_weekday_future,
    # heavy_rain_winter_weekend,
    # heavy_rain_winter_weekend_future,
    heavy_rain_spring_weekday,
    heavy_rain_spring_weekday_future,
    # heavy_rain_spring_weekend,
    # heavy_rain_spring_weekend_future,
    # non_heavy_rain_fall_weekend,
    # non_heavy_rain_fall_weekend_future,
)
from PredictionFunction.utils.fetch_events import fetch_events

def oslo_city(prediction_category,restaurant,merged_data,historical_data,future_data):
    sales_data_df = historical_data
    sales_data_df = sales_data_df.rename(columns={"date": "ds"})

    future_data = future_data.rename(columns={"date": "ds"})

    merged_data = merged_data.rename(columns={"date": "ds"})

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
    df["ds"] = pd.to_datetime(df["ds"])
    df = warm_dry_weather_spring(df)
    df = heavy_rain_fall_weekend(df)
    df = heavy_rain_winter_weekday(df)
    df = heavy_rain_spring_weekday(df)
    m = Prophet()

    ### Holidays and other repeating outliers
    m.add_country_holidays(country_name="NO")

    # christmas_day = pd.DataFrame(
    #     {
    #         "holiday": "christmas eve",
    #         "ds": pd.to_datetime(["2022-12-24"]),
    #         "lower_window": -5,
    #         "upper_window": 0,
    #     }
    # )

    # firstweek_jan = pd.DataFrame(
    #     {
    #         "holiday": "firstweek_jan",
    #         "ds": pd.to_datetime(["2022-01-10", "2023-01-08", "2024-01-07"]),
    #         "lower_window": -7,
    #         "upper_window": 0,
    #     }
    # )

    # new_years_day = pd.DataFrame(
    #     {
    #         "holiday": "new_years_day",
    #         "ds": pd.to_datetime(["2022-01-01", "2023-01-01"]),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )

    # first_may = pd.DataFrame(
    #     {
    #         "holiday": "first_may",
    #         "ds": pd.to_datetime(["2021-05-01", "2022-05-01", "2023-05-01"]),
    #         "lower_window": -1,
    #         "upper_window": 0,
    #     }
    # )

    # easter = pd.DataFrame(
    #     {
    #         "holiday": "easter",
    #         "ds": pd.to_datetime(
    #             [
    #                 "2022-04-14",
    #                 "2022-04-15",
    #                 "2022-04-16",
    #                 "2022-04-17",
    #                 "2023-04-06",
    #                 "2023-04-07",
    #                 "2023-04-08",
    #                 "2023-04-09",
    #             ]
    #         ),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )

    # easter_lowsaturday = pd.DataFrame(
    #     {
    #         "holiday": "easter_lowsaturday",
    #         "ds": pd.to_datetime(["2022-04-16"]),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )

    # easter_mondaydayoff = pd.DataFrame(
    #     {
    #         "holiday": "easter_mondaydayoff",
    #         "ds": pd.to_datetime(["2022-04-18", "2023-04-10"]),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )

    # pinse = pd.DataFrame(
    #     {
    #         "holiday": "pinse",
    #         "ds": pd.to_datetime(["2022-06-06", "2023-05-29"]),
    #         "lower_window": -4,
    #         "upper_window": 0,
    #     }
    # )

    # day_before_red_day = pd.DataFrame(
    #     {
    #         "holiday": "day_before_red_day",
    #         "ds": pd.to_datetime(
    #             [
    #                 "2022-04-14",
    #                 "2022-05-16",
    #                 "2022-05-25",
    #                 "2022-12-24",
    #                 "2023-04-05",
    #                 "2023-05-16",
    #             ]
    #         ),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )

    # 2023: falls the day after the national independence day, so no effect the day before this year
    # himmelfart = pd.DataFrame(
    #     {
    #         "holiday": "himmelfart",
    #         "ds": pd.to_datetime(["2022-05-26"]),
    #         "lower_window": -1,
    #         "upper_window": 0,
    #     }
    # )

    # closed_days = pd.DataFrame(
    #     {
    #         "holiday": "closed_days",
    #         "ds": pd.to_datetime(
    #             [
    #                 "2022-04-14",
    #                 "2022-04-15",
    #                 "2022-04-17",
    #                 "2022-04-18",
    #                 "2022-12-25",
    #                 "2022-12-26",
    #                 "2022-06-05",
    #                 "2022-06-06",
    #                 "2022-06-11",
    #                 "2022-06-12",
    #                 "2023-01-01",
    #                 "2023-04-06",
    #                 "2023-04-07",
    #                 "2023-04-08",
    #                 "2023-04-09",
    #                 "2023-04-10",
    #                 "2023-05-01",
    #                 "2023-05-17",
    #                 "2023-05-18",
    #                 "2023-05-29",
    #             ]
    #         ),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )
    # oslo_pride = pd.DataFrame(
    #     {
    #         "holiday": "oslo_pride",
    #         "ds": pd.to_datetime(["2023-07-01"]),
    #         "lower_window": -7,
    #         "upper_window": 3,
    #     }
    # )
    # norway_cup = pd.DataFrame(
    #     {
    #         "holiday": "Norway Cup",
    #         "ds": pd.to_datetime(["2022-08-03", "2023-08-05"]),
    #         "lower_window": -8,
    #         "upper_window": 1,
    #     }
    # )
    # black_friday = pd.DataFrame(
    #     {
    #         "holiday": "Black Friday",
    #         "ds": pd.to_datetime(["2022-11-25", "2023-11-24"]),
    #         "lower_window": -1,
    #         "upper_window": 0,
    #     }
    # )

    # lockdown = pd.DataFrame(
    #     [
    #         {
    #             "holiday": "lockdown_1",
    #             "ds": "2019-12-31",
    #             "lower_window": 0,
    #             "ds_upper": "2020-04-14",
    #         },
    #     ]
    # )
    # for t_col in ['ds', 'ds_upper']:
    #    lockdowns[t_col] = pd.to_datetime(lockdowns[t_col])
    # lockdowns['upper_window'] = (lockdowns['ds_upper'] - lockdowns['ds']).dt.days
    # lockdowns

    holidays = pd.concat(
        (
            christmas_day,
            firstweek_jan,
            first_may,
            easter_lowsaturday,
            easter_mondaydayoff,
            pinse,
            day_before_red_day,
            himmelfart,
            closed_days,
            lockdown,
            black_friday,
            norway_cup,
            halloween_weekend,
            halloween_day,
            first_weekend_christmas_school_vacation,
        )
    )

    ### Add weather parameters

    # m.add_regressor('precipitation_hours', mode='additive')
    # m.add_regressor('apparent_temperature_mean')
    # m.add_regressor('rain_sum')
    # m.add_regressor('snowfall_sum')
    # m.add_regressor('windspeed_10m_max')

    # Add custom monthly seasonalities for a specific month
    # def is_specific_month(ds):
    #     date = pd.to_datetime(ds)
    #     start_date = pd.to_datetime(
    #         "2022-07-01"
    #     )  # replace with the start date of the interval
    #     end_date = pd.to_datetime(
    #         "2022-07-31"
    #     )  # replace with the end date of the interval
    #     return start_date <= date <= end_date

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
    # df['no_covid_restriction_christmas'] = ~df['ds'].apply(is_covid_restriction_christmas)

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
    # df['not_christmas_shopping'] = ~df['ds'].apply(is_christmas_shopping)


    # The training DataFrame (df) should also include 'days_since_last' and 'days_until_next' columns.
    df = calculate_days_30(df, fifteenth_working_days)

    # Oslo Spektrum large concerts
    oslo_spektrum = fetch_events("Oslo City","Oslo Spektrum")
    oslo_spectrum_large_df = pd.DataFrame(oslo_spektrum)
    oslo_spectrum_large_df = oslo_spectrum_large_df.rename(columns={"date": "ds"})

    # filtering by Young audience groups gives a negative expected effect.
    # oslo_spectrum_large_df = oslo_spectrum_large_df.loc[(oslo_spectrum_large_df['Audience Group'] == 'Young')]
    oslo_spectrum_large_df["ds"] = pd.to_datetime(oslo_spectrum_large_df["ds"])
    #oslo_spectrum_large_df should be 1 if there is a concert on that date that has concert size = Large and if the day is within sunday-thursday window and 0 if not using np
    oslo_spectrum_large_df["oslo_spektrum_large_concert"] = np.where(
        (oslo_spectrum_large_df["event_size"] == "Large")
        & (oslo_spectrum_large_df["ds"].dt.weekday < 4),
        1,
        0,
    )


   
    #oslo_spectrum_large_df["oslo_spektrum_large_concert"] = 1
    oslo_spectrum_large_df = oslo_spectrum_large_df[
        ["ds", "name", "oslo_spektrum_large_concert"]
    ]

    # Merge the new dataframe with the existing data
    df = pd.merge(df, oslo_spectrum_large_df, how="left", on=["ds"])

    # Fill missing values with 0
    df["oslo_spektrum_large_concert"].fillna(0, inplace=True)

    # closed days
    closed_dates = pd.to_datetime(
        [
            "2021-12-23",
            "2021-12-24",
            "2021-12-25",
            "2022-12-31",
            "2023-05-17",
            "2023-05-18",
        ]
    )

    df["closed"] = df["ds"].apply(
        lambda x: 1 if x in closed_dates or x.dayofweek == 6 else 0
    )

    # create daily seasonality column setting a number for each day of the week, to be used later
    # Create a Boolean column for each weekday
    for weekday in range(7):
        df[f"weekday_{weekday}"] = df["ds"].dt.weekday == weekday
    
   
    df['ds'] = pd.to_datetime(df['ds'])  
    df['rain_weekend'] = df.apply(is_saturday_rainy_windy, axis=1)
    df['rain_windy_weekend'] = df.apply(is_saturday_rainy_windy,axis = 1)
    #df['rain_weekend'] =df['rain_weekend'].fillna(0)
    df['rain_windy_weekend'] = df['rain_windy_weekend'].fillna(0)
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

    #add weather regressors
    #m.add_regressor("saturday_rain")
    m.add_regressor("warm_and_dry")
    #m.add_regressor("heavy_rain_fall_weekday")
    m.add_regressor("heavy_rain_fall_weekend")
    m.add_regressor("heavy_rain_winter_weekday")
    #m.add_regressor("heavy_rain_winter_weekend")
    m.add_regressor("heavy_rain_spring_weekday")
    #m.add_regressor("heavy_rain_spring_weekend")
    #m.add_regressor("non_heavy_rain_fall_weekend")
    m.add_regressor("closed")
    m.add_regressor("custom_regressor")
    

    # m.add_regressor("temp_deviation")
    # m.add_regressor("rain_deviation")
    # m.add_regressor("wind_deviation")
    #m1.add_regressor("rain_weekend")
    #m.add_regressor("rain_weekend")
    m.add_regressor("rain_windy_weekend")
    # m.add_regressor("rain_wind")
    m.add_seasonality(
        name="monthly", period=30.5, fourier_order=5, condition_name="specific_month"
    )
    m.add_seasonality(
        name="covid_restriction_christmas",
        period=7,
        fourier_order=1000,
        condition_name="covid_restriction_christmas",
    )

    # Add the payday columns as regressors
    m.add_regressor("days_since_last_30")
    # Add the Osloe Spektrum regressor
    m.add_regressor("oslo_spektrum_large_concert")

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
    m.add_regressor("sunshine_amount", standardize=False)
    if prediction_category == "hour":
        df["ds"] = pd.to_datetime(
            df["ds"].astype(str) + " " + df["hour"].astype(str) + ":00:00"
        )
        weekday_mask = df["ds"].dt.weekday < 4  # Monday to Friday
        weekend_mask = df["ds"].dt.weekday >= 4  # Saturday and Sunday

        df_weekday = df[weekday_mask]
        df_weekend = df[weekend_mask]
        # print(df_weekday)
        # print(df_weekend)
        # Set the hours dynamically based on the day of the week
        df_weekday = df_weekday[
            (
                df_weekday["ds"].dt.hour
                >= int(restaurant_hours["Oslo City"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Oslo City"]["weekday"]["ending"])
            )
        ]

        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Oslo City"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Oslo City"]["weekend"]["ending"])
            )
        ]

        # Concatenate the weekday and weekend DataFrames
        df = pd.concat([df_weekday, df_weekend])
    df = df.drop_duplicates(subset='ds')
    m.fit(df)
    #m1.fit(df)
    # m1.fit(prophet_df)

    


    # df = df[(df['hour'] < 20)]
    # df = df[(df['hour'] > 4 )]

    if prediction_category == "hour":
        future = m.make_future_dataframe(periods=700, freq="H")
        #future_residual = m1.make_future_dataframe(periods = 700,freq ='H')
        # Add the Boolean columns for each weekday to the future DataFrame
        for weekday in range(7):
            future[f"weekday_{weekday}"] = future["ds"].dt.weekday == weekday

    else:
        future = m.make_future_dataframe(periods=60, freq="D")
        #future_residual = m1.make_future_dataframe(periods = 60,freq ='D')
    if prediction_category == "hour":
        weekday_mask = future["ds"].dt.weekday < 4  # Monday to Friday
        weekend_mask = future["ds"].dt.weekday >= 4  # Saturday and Sunday

        df_weekday = future[weekday_mask]
        df_weekend = future[weekend_mask]
        df_weekday = df_weekday[
            (
                df_weekday["ds"].dt.hour
                >= int(restaurant_hours["Oslo City"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Oslo City"]["weekday"]["ending"])
            )
        ]

        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Oslo City"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Oslo City"]["weekend"]["ending"])
            )
        ]
        # Concatenate the weekday and weekend DataFrames
        future = pd.concat([df_weekday, df_weekend])


    

    # add the last working day and the +/- 5 days
    future = calculate_days_30(future, last_working_day)

    future["sunshine_amount"] = merged_data["sunshine_amount"]
    future["rain_sum"] = merged_data["rain_sum"]

    #Add weather regressors to the future df
    'Add a new column to the df called saturday_rain, with a 1 if it is a saturday and the rain_sum sum between 14-23 o clock is more than 5'
    #future["ds"] = pd.to_datetime(future["ds"])
    #future["saturday_rain"] = np.where(
    #    (future["ds"].dt.weekday == 5) & (future["rain_sum"] > 5), 1, 0
    #)

    future["covid_restriction_christmas"] = future["ds"].apply(
        is_covid_restriction_christmas
    )

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

    future["fall_start"] = future["ds"].apply(is_fall_start)

    future["christmas_shopping"] = future["ds"].apply(is_christmas_shopping)

    future["closed"] = future["ds"].apply(
        lambda x: 1 if x in closed_dates or x.dayofweek == 6 else 0
    )

    future["specific_month"] = future["ds"].apply(is_specific_month)
    # Calculate the custom regressor values for the future dates
    future["ds"] = pd.to_datetime(future["ds"])
    future_date_mask = (future["ds"] >= start_date) & (future["ds"] <= end_date)
    future["week_number"] = future["ds"].dt.isocalendar().week
    future.loc[future_date_mask, "custom_regressor"] = future.loc[
        future_date_mask, "week_number"
    ].apply(custom_regressor)
    future.loc[~future_date_mask, "custom_regressor"] = 0

    #future = pd.merge(future,df[['ds','rain_weekend']],on='ds',how='left')
    #future["rain_weekend"].fillna(0, inplace=True)
    future = pd.merge(future,df[['ds','rain_windy_weekend']],on='ds',how='left')
    future["rain_windy_weekend"].fillna(0,inplace=True)
 
    if prediction_category != "hour":
        future["ds"] = future["ds"].dt.date  

     # Add relevant weather columns to the future df
    future["rain_sum"] = merged_data["rain_sum"]
    future["sunshine_amount"] = merged_data["sunshine_amount"]
    future["windspeed"] = merged_data["windspeed"]
    future["air_temperature"] = merged_data["air_temperature"]
    future = warm_and_dry_future(future)
    #future = heavy_rain_fall_weekday_future(future)
    future = heavy_rain_fall_weekend_future(future)
    future = heavy_rain_winter_weekday_future(future)
    #future = heavy_rain_winter_weekend_future(future)
    future = heavy_rain_spring_weekday_future(future)
    #future = heavy_rain_spring_weekend_future(future)
    #future = non_heavy_rain_fall_weekend_future(future)
    future.fillna(0, inplace=True)
    future = future.drop_duplicates(subset='ds')

    return m, future, df



def location_function(prediction_category,restaurant,merged_data,historical_data,future_data):
    return oslo_city(prediction_category,restaurant,merged_data,historical_data,future_data)