import pandas as pd
import numpy as np
from prophet import Prophet
from PredictionFunction.Datasets.Holidays.LosTacos.dataset_holidays import (
    last_working_day,
    fifteenth_working_days,
)
from PredictionFunction.utils.utils import calculate_days_30,calculate_days_15, custom_regressor, is_closed
from PredictionFunction.Datasets.Regressors.general_regressors import (is_specific_month,
is_covid_restriction_christmas,
is_fall_start,
is_christmas_shopping,
)

from PredictionFunction.Datasets.OpeningHours.lostacos_opening_hours import restaurant_opening_hours
from PredictionFunction.Datasets.Regressors.weather_regressors import(
    #warm_dry_weather_spring,
    warm_and_dry_future,
    heavy_rain_fall_weekday,
    heavy_rain_fall_weekday_future,
    heavy_rain_fall_weekend,
    heavy_rain_fall_weekend_future,
    #heavy_rain_winter_weekday, 
    #heavy_rain_winter_weekday_future,
    #heavy_rain_winter_weekend,
    #heavy_rain_winter_weekend_future,
    heavy_rain_spring_weekday,
    heavy_rain_spring_weekday_future,
    heavy_rain_spring_weekend,
    heavy_rain_spring_weekend_future,
    # non_heavy_rain_fall_weekend,
    # non_heavy_rain_fall_weekend_future,

)
from PredictionFunction.Datasets.Holidays.LosTacos.Restaurants.fredrikstad_holidays import (
    christmas_day,
    new_year_eve,
    # firstweek_jan,
    # new_years_day,
    fadder_week,
    seventeenth_may,
    easter,
    # pinse,
    # himmelfart,
    stor_konsert_ukedag,
    idyll,
    closed_days,
    black_friday,
    )

from PredictionFunction.Datasets.Holidays.LosTacos.common_holidays import (
    first_may,
    firstweek_jan,
    new_years_day,
    pinse,
    himmelfart,
    halloween_day,
    halloween_weekend,
    hostferie_sor_ostlandet_weekdays,
    hostferie_sor_ostlandet_weekdend,
)

def fredrikstad(prediction_category,restaurant,merged_data,historical_data,future_data):
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
        # df['y'] = np.log(df['y'])
    #df = warm_dry_weather_spring(df)
    df = heavy_rain_fall_weekday(df)
    df = heavy_rain_fall_weekend(df)
    #df = heavy_rain_winter_weekday(df)
    #df = heavy_rain_winter_weekend(df)
    df = heavy_rain_spring_weekday(df)
    df = heavy_rain_spring_weekend(df)
    #df = non_heavy_rain_fall_weekend(df)

    m = Prophet()

    ### Holidays and other repeating outliers
    m.add_country_holidays(country_name="NO")

    # christmas_day = pd.DataFrame(
    #     {
    #         "holiday": "christmas eve",
    #         "ds": pd.to_datetime(["2021-12-24", "2022-12-24"]),
    #         "lower_window": -5,
    #         "upper_window": 0,
    #     }
    # )

    # new_year_eve = pd.DataFrame(
    #     {
    #         "holiday": "new_year_eve",
    #         "ds": pd.to_datetime(["2021-12-31", "2022-12-31"]),
    #         "lower_window": -6,
    #         "upper_window": 0,
    #     }
    # )

    # firstweek_jan = pd.DataFrame(
    #     {
    #         "holiday": "firstweek_jan",
    #         "ds": pd.to_datetime(
    #             [
    #                 "2021-01-02",
    #                 "2021-01-02",
    #                 "2021-01-03",
    #                 "2021-01-04",
    #                 "2021-01-05",
    #                 "2021-01-06",
    #                 "2021-01-07",
    #                 "2021-01-08",
    #                 "2021-01-09",
    #                 "2021-01-10",
    #                 "2021-01-11",
    #                 "2022-01-02",
    #                 "2022-01-02",
    #                 "2022-01-03",
    #                 "2022-01-04",
    #                 "2022-01-05",
    #                 "2022-01-06",
    #                 "2022-01-07",
    #                 "2022-01-08",
    #                 "2022-01-09",
    #                 "2022-01-10",
    #                 "2022-01-11",
    #                 "2023-01-02",
    #                 "2023-01-02",
    #                 "2023-01-03",
    #                 "2023-01-04",
    #                 "2023-01-05",
    #                 "2023-01-06",
    #                 "2023-01-07",
    #                 "2023-01-08",
    #                 "2023-01-09",
    #                 "2023-01-10",
    #                 "2023-01-11",
    #             ]
    #         ),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )

    # new_years_day = pd.DataFrame(
    #     {
    #         "holiday": "new_years_day",
    #         "ds": pd.to_datetime(["2022-01-01", "2022-01-01", "2023-01-01"]),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )

    # fadder_week = pd.DataFrame(
    #     {
    #         "holiday": "fadder_week",
    #         "ds": pd.to_datetime(
    #             ["2022-08-15", "2022-08-16", "2022-08-17", "2022-08-18"]
    #         ),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )

    # only when the holiday is on a weekday. If it is in the weekend there is no effect
    # first_may = pd.DataFrame(
    #     {
    #         "holiday": "first_may",
    #         "ds": pd.to_datetime(["2021-05-01", "2023-05-01"]),
    #         "lower_window": -1,
    #         "upper_window": 0,
    #     }
    # )
    # seventeenth_may = pd.DataFrame(
    #     {
    #         "holiday": "seventeenth_may",
    #         "ds": pd.to_datetime(
    #             ["2021-05-17", "2022-05-17", "2023-05-17", "2024-05-17"]
    #         ),
    #         "lower_window": -1,
    #         "upper_window": 0,
    #     }
    # )

    # easter = pd.DataFrame(
    #     {
    #         "holiday": "easter",
    #         "ds": pd.to_datetime(
    #             ["2022-04-14", "2022-04-15", "2022-04-16", "2022-04-17"]
    #         ),
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

    # 2023: falls the day after the national independence day, so no effect the day before this year
    # himmelfart = pd.DataFrame(
    #     {
    #         "holiday": "himmelfart",
    #         "ds": pd.to_datetime(["2022-05-26"]),
    #         "lower_window": -1,
    #         "upper_window": 0,
    #     }
    # )

    # stor_konsert_ukedag = pd.DataFrame(
    #     {
    #         "holiday": "stor_konsert_ukedag",
    #         "ds": pd.to_datetime([]),
    #         "lower_window": 0,
    #         "upper_window": 0,
    #     }
    # )

    # idyll = pd.DataFrame(
    #     {
    #         "holiday": "idyll",
    #         "ds": pd.to_datetime(["2022-06-19", "2023-06-18"]),
    #         "lower_window": -3,
    #         "upper_window": 0,
    #     }
    # )

    # closed_days = pd.DataFrame(
    #     {
    #         "holiday": "closed_days",
    #         "ds": pd.to_datetime(
    #             [
    #                 "2021-12-22",
    #                 "2021-12-23",
    #                 "2021-12-24",
    #                 "2021-12-25",
    #                 "2022-12-24",
    #                 "2022-12-31",
    #             ]
    #         ),
    #         "lower_window": 0,
    #         "upper_window": 0,
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

    holidays = pd.concat(
        (
            christmas_day,
            new_year_eve,
            new_years_day,
            firstweek_jan,
            fadder_week,
            first_may,
            easter,
            seventeenth_may,
            pinse,
            stor_konsert_ukedag,
            himmelfart,
            closed_days,
            idyll,
            black_friday,
            halloween_weekend,
            halloween_day,
            hostferie_sor_ostlandet_weekdend,
            hostferie_sor_ostlandet_weekdays,
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

    ### Add weather parameters

    # m.add_regressor('precipitation_hours', mode='additive')
    # m.add_regressor('apparent_temperature_mean')
    # m.add_regressor('rain_sum')
    # m.add_regressor('snowfall_sum')
    # m.add_regressor('windspeed_10m_max')

    # Add custom monthly seasonalities for a specific month

    df["specific_month"] = df["ds"].apply(is_specific_month)

    # Define a function to check if the date is within the period of heavy COVID restrictions

    # Add new columns in your dataframe to indicate if a date is within or outside the restrictions period
    df["covid_restriction_christmas"] = df["ds"].apply(is_covid_restriction_christmas)
    df["no_covid_restriction_christmas"] = ~df["ds"].apply(
        is_covid_restriction_christmas
    )

    # was closed for the following date interval


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

    # Different weekly seasonality for 2 weeks in august related to starting fall semester/work
    FALL_START_DATES = {
        2022: {"start": "2022-08-08", "end": "2022-08-21"},
        2023: {"start": "2023-08-07", "end": "2023-08-20"},
        # Add more years and their respective dates as needed
    }

    df["fall_start"] = df["ds"].apply(is_fall_start)
    # df['not_fall_start'] = ~df['ds'].apply(is_fall_start)



    df["christmas_shopping"] = df["ds"].apply(is_christmas_shopping)
    # df['not_christmas_shopping'] = ~df['ds'].apply(is_christmas_shopping)

    ## calculating the paydays and the days before and after. Used in regressions



    # The training DataFrame (df) should also include 'days_since_last' and 'days_until_next' columns.
    #df = calculate_days_30(df, fifteenth_working_days)


    # The training DataFrame (df) should also include 'days_since_last' and 'days_until_next' columns.
    #df = calculate_days_15(df, fifteenth_working_days)

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
    #m.add_regressor("days_since_last_30")

    #m.add_regressor("days_since_last_15")
    #m.add_regressor("days_until_next_15")

    #m.add_regressor("warm_and_dry")
    m.add_regressor("heavy_rain_fall_weekday")
    m.add_regressor("heavy_rain_fall_weekend")
    #m.add_regressor("heavy_rain_winter_weekday")
    #m.add_regressor("heavy_rain_winter_weekend")
    m.add_regressor("heavy_rain_spring_weekday")
    m.add_regressor("heavy_rain_spring_weekend")
    #m.add_regressor("non_heavy_rain_fall_weekend")

    m.add_regressor("custom_regressor")
    # m.add_regressor('covid_restriction')
    m.add_regressor("closed_jan")
    m.add_seasonality(
        name="monthly", period=30.5, fourier_order=5, condition_name="specific_month"
    )
    m.add_seasonality(
        name="covid_restriction_christmas",
        period=7,
        fourier_order=1000,
        condition_name="covid_restriction_christmas",
    )
    # m.add_seasonality(name='no_covid_restriction_christmas', period=7, fourier_order=3,
    #                  condition_name='no_covid_restriction_christmas')

    m.add_seasonality(
        name="weekly_fall_start", period=7, fourier_order=3, condition_name="fall_start"
    )
    # m.add_seasonality(name='weekly_not_fall_start', period=7, fourier_order=3,
    #                  condition_name='not_fall_start')

    m.add_seasonality(
        name="christmas_shopping",
        period=7,
        fourier_order=3,
        condition_name="christmas_shopping",
    )
    # m.add_seasonality(name='not_christmas_shopping', period=7, fourier_order=3,
    #                  condition_name='not_christmas_shopping')

    # Add the conditional regressor to the model
    m.add_regressor("sunshine_amount", standardize=False)
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
                >= int(restaurant_hours["Fredrikstad"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Fredrikstad"]["weekday"]["ending"])
            )
        ]

        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Fredrikstad"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Fredrikstad"]["weekend"]["ending"])
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
                >= int(restaurant_hours["Fredrikstad"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Fredrikstad"]["weekday"]["ending"])
            )
        ]

        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Fredrikstad"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Fredrikstad"]["weekend"]["ending"])
            )
        ]

        # Concatenate the weekday and weekend DataFrames
        future = pd.concat([df_weekday, df_weekend])

    # add the last working day and the +/- 5 days
    #future = calculate_days_30(future, last_working_day)
    #future = calculate_days_15(future, fifteenth_working_days)

    future["sunshine_amount"] = merged_data["sunshine_amount"]

    future["covid_restriction_christmas"] = future["ds"].apply(
        is_covid_restriction_christmas
    )
    # future['no_covid_restriction_christmas'] = ~future['ds'].apply(is_covid_restriction_christmas)

    future["fall_start"] = future["ds"].apply(is_fall_start)
    # future['not_fall_start'] = ~future['ds'].apply(is_fall_start)

    future["christmas_shopping"] = future["ds"].apply(is_christmas_shopping)
    # future['not_christmas_shopping'] = ~future['ds'].apply(is_christmas_shopping)

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
    if prediction_category != "hour":
        future["ds"] = future["ds"].dt.date

     # Add relevant weather columns to the future df
    future["rain_sum"] = merged_data["rain_sum"]
    future["sunshine_amount"] = merged_data["sunshine_amount"]
    future["windspeed"] = merged_data["windspeed"]
    future["air_temperature"] = merged_data["air_temperature"]
    future = warm_and_dry_future(future)
    future = heavy_rain_fall_weekday_future(future)
    future = heavy_rain_fall_weekend_future(future)
    #future = heavy_rain_winter_weekday_future(future)
   # future = heavy_rain_winter_weekend_future(future)
    future = heavy_rain_spring_weekday_future(future)
    future = heavy_rain_spring_weekend_future(future)
    #future = non_heavy_rain_fall_weekend_future(future)

    future.fillna(0, inplace=True)

    return m, future, df


def location_function(prediction_category,restaurant,merged_data,historical_data,future_data):
    return fredrikstad(prediction_category,restaurant,merged_data,historical_data,future_data)