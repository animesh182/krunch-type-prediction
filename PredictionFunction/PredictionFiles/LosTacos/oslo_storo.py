import pandas as pd
from prophet import Prophet
from PredictionFunction.Datasets.Holidays.LosTacos.dataset_holidays import (
    last_working_day,
    fifteenth_working_days,
    fornebu_large_concerts,
    ullevaal_big_football_games,
)
from PredictionFunction.Datasets.Regressors.general_regressors import (
    is_specific_month,
    is_covid_restriction_christmas,
    is_fall_start,
    is_christmas_shopping,
)
from PredictionFunction.Datasets.Regressors.weather_regressors import (
    warm_dry_weather_spring,
    warm_and_dry_future,
    heavy_rain_fall_weekday,
    heavy_rain_fall_weekday_future,
    heavy_rain_fall_weekend,
    heavy_rain_fall_weekend_future,
    heavy_rain_winter_weekday,
    heavy_rain_winter_weekday_future,
    # heavy_rain_winter_weekend,
    # heavy_rain_winter_weekend_future,
    heavy_rain_spring_weekday,
    heavy_rain_spring_weekday_future,
    heavy_rain_spring_weekend,
    heavy_rain_spring_weekend_future,
    # non_heavy_rain_fall_weekend,
    # non_heavy_rain_fall_weekend_future,
)
from PredictionFunction.utils.utils import (
    calculate_days_30,
    custom_regressor,
    calculate_days_15,
)
from PredictionFunction.Datasets.Holidays.LosTacos.Restaurants.oslo_storo_holidays import (
    christmas_day,
    # firstweek_jan,
    # new_years_day,
    # first_may,
    seventeenth_may,
    easter,
    easter_lowsaturday,
    easter_mondaydayoff,
    # pinse,
    # himmelfart,
    fadderuke,
    day_before_red_day,
    closed_days,
    karriere_dag,
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

from PredictionFunction.utils.fetch_sales_data import fetch_salesdata
from PredictionFunction.utils.fetch_events import fetch_events
from PredictionFunction.utils.openinghours import add_opening_hours


def oslo_storo(
    prediction_category, restaurant, merged_data, historical_data, future_data
):

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

    # df['y'] = np.log(df['y'])
    df = warm_dry_weather_spring(df)
    df = heavy_rain_fall_weekday(df)
    df = heavy_rain_fall_weekend(df)
    df = heavy_rain_winter_weekday(df)
    # df = heavy_rain_winter_weekend(df)
    df = heavy_rain_spring_weekday(df)
    df = heavy_rain_spring_weekend(df)
    # df = non_heavy_rain_fall_weekend(df)
    m = Prophet()

    ### Holidays and other repeating outliers
    m.add_country_holidays(country_name="NO")

    holidays = pd.concat(
        (
            christmas_day,
            firstweek_jan,
            first_may,
            easter,
            easter_mondaydayoff,
            seventeenth_may,
            pinse,
            himmelfart,
            day_before_red_day,
            lockdown,
            closed_days,
            fadderuke,
            oslo_pride,
            karriere_dag,
            halloween_day,
            halloween_weekend,
            hostferie_sor_ostlandet_weekdend,
            first_weekend_christmas_school_vacation,
        )
    )

    # Add custom monthly seasonalities for a specific month

    df["specific_month"] = df["ds"].apply(is_specific_month)

    # Define a function to check if the date is within the period of heavy COVID restrictions

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
    start_date = "2022-08-22"
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
    df = add_opening_hours(df, "Oslo Storo", 11, 11)

    oslo_storo_venues = {
        "Ulleval",
        "Cosmopolite, Oslo",
        "Oslo City",
        "Nordic Black Theatre",
        "Salt Langhuset",
        "Parkteatret Scene",
    }

    data = {"name": [], "effect": []}
    regressors_to_add = []
    for venue in oslo_storo_venues:
        # for venue in karl_johan_venues:
        venue_df = fetch_events("Oslo Torggata", venue)
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

    # The training DataFrame (df) should also include 'days_since_last' and 'days_until_next' columns.
    # df = calculate_days_30(df, fifteenth_working_days)

    # # Ullevål big concerts regressor (Oslo)
    # ullevaal_big_football_games_df = pd.DataFrame(ullevaal_big_football_games)
    # ullevaal_big_football_games_df["date"] = pd.to_datetime(
    #     ullevaal_big_football_games_df["date"]
    # )
    # # Rename the columns to match the existing DataFrame
    # ullevaal_big_football_games_df.columns = ["ds", "event"]
    # # Create a new column for the event
    # ullevaal_big_football_games_df["ullevaal_big_football_games"] = 1
    # # Merge the new dataframe with the existing data
    # df = pd.merge(df, ullevaal_big_football_games_df, how="left", on="ds")
    # # Fill missing values with 0
    # df["ullevaal_big_football_games"].fillna(0, inplace=True)

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
    # m.add_regressor("days_since_last_30")
    # m.add_regressor("days_until_next_30")

    m.add_regressor("warm_and_dry")
    m.add_regressor("heavy_rain_fall_weekday")
    m.add_regressor("heavy_rain_fall_weekend")
    m.add_regressor("heavy_rain_winter_weekday")
    # m.add_regressor("heavy_rain_winter_weekend")
    m.add_regressor("heavy_rain_spring_weekday")
    m.add_regressor("heavy_rain_spring_weekend")
    # m.add_regressor("non_heavy_rain_fall_weekend")
    m.add_regressor("sunshine_amount", standardize=False)
    m.add_regressor("opening_duration")

    # Add the Ullevåål big football games  regressor
    # m.add_regressor("ullevaal_big_football_games")

    m.add_regressor("custom_regressor")

    for event_df, regressor_name in regressors_to_add:
        if "event" in event_df.columns:
            m.add_regressor(regressor_name)

    m.add_seasonality(
        name="monthly", period=30.5, fourier_order=5, condition_name="specific_month"
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
    m.add_regressor("sunshine_amount", standardize=False)
    if prediction_category == "hour":
        df["ds"] = pd.to_datetime(
            df["ds"].astype(str) + " " + df["hour"].astype(str) + ":00:00"
        )
        weekday_mask = df["ds"].dt.weekday < 4  # Monday to Friday
        weekend_mask = df["ds"].dt.weekday == 4  # Saturday

        df_weekday = df[weekday_mask]
        df_weekend = df[weekend_mask]
        # print(df_weekday)
        # print(df_weekend)
        # Set the hours dynamically based on the day of the week
        df_weekday = df_weekday[
            (
                df_weekday["ds"].dt.hour
                >= int(restaurant_hours["Oslo Storo"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Oslo Storo"]["weekday"]["ending"])
            )
        ]

        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Oslo Storo"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Oslo Storo"]["weekend"]["ending"])
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
        weekday_mask = future["ds"].dt.weekday < 4  # Monday to Friday
        weekend_mask = future["ds"].dt.weekday == 4  # Saturday
        df_weekday = future[weekday_mask]
        df_weekend = future[weekend_mask]
        df_weekday = df_weekday[
            (
                df_weekday["ds"].dt.hour
                >= int(restaurant_hours["Oslo Storo"]["weekday"]["starting"])
            )
            & (
                df_weekday["ds"].dt.hour
                <= int(restaurant_hours["Oslo Storo"]["weekday"]["ending"])
            )
        ]
        df_weekend = df_weekend[
            (
                df_weekend["ds"].dt.hour
                >= int(restaurant_hours["Oslo Storo"]["weekend"]["starting"])
            )
            | (
                df_weekend["ds"].dt.hour
                <= int(restaurant_hours["Oslo Storo"]["weekend"]["ending"])
            )
        ]
        future = pd.concat([df_weekday, df_weekend])

    # add the last working day and the +/- 5 days
    # future = calculate_days_30(future, last_working_day)

    future["sunshine_amount"] = merged_data["sunshine_amount"]

    future["covid_restriction_christmas"] = future["ds"].apply(
        is_covid_restriction_christmas
    )

    future["fall_start"] = future["ds"].apply(is_fall_start)

    future["christmas_shopping"] = future["ds"].apply(is_christmas_shopping)

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

    # Add Future df for Oslo Spektrum large concerts
    # Merge with the events data
    # future = pd.merge(
    #     future,
    #     ullevaal_big_football_games_df[["ds", "ullevaal_big_football_games"]],
    #     how="left",
    #     on="ds",
    # )
    # # Fill missing values with 0
    # future["ullevaal_big_football_games"].fillna(0, inplace=True)

    future["specific_month"] = future["ds"].apply(is_specific_month)
    # Calculate the custom regressor values for the future dates
    future["ds"] = pd.to_datetime(future["ds"])
    future_date_mask = (future["ds"] >= start_date) & (future["ds"] <= end_date)
    future["week_number"] = future["ds"].dt.isocalendar().week
    future.loc[future_date_mask, "custom_regressor"] = future.loc[
        future_date_mask, "week_number"
    ].apply(custom_regressor)
    future.loc[~future_date_mask, "custom_regressor"] = 0

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
    future = heavy_rain_winter_weekday_future(future)
    # future = heavy_rain_winter_weekend_future(future)
    future = heavy_rain_spring_weekday_future(future)
    future = heavy_rain_spring_weekend_future(future)
    future = add_opening_hours(future, "Oslo Storo", 11, 11)
    # future = non_heavy_rain_fall_weekend_future(future)
    future.fillna(0, inplace=True)

    return m, future, df


def location_function(
    prediction_category, restaurant, merged_data, historical_data, future_data
):
    return oslo_storo(
        prediction_category, restaurant, merged_data, historical_data, future_data
    )
