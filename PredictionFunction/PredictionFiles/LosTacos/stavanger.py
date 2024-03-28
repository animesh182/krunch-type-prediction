import pandas as pd
import numpy as np
from prophet import Prophet
from PredictionFunction.Datasets.Holidays.LosTacos.dataset_holidays import (
    cruise_ship_arrivals,
    twelfth_working_days,
    last_working_day,
)
import logging
from PredictionFunction.utils.utils import calculate_days_30, calculate_days_15,custom_regressor
from PredictionFunction.Datasets.OpeningHours.lostacos_opening_hours import restaurant_opening_hours
from PredictionFunction.Datasets.Seasonalities.LosTacos.weekly_seasonality import weekly_seasonalities
from PredictionFunction.Datasets.Regressors.general_regressors import (
    is_fellesferie_stavanger,
    is_may,
    is_covid_restriction_christmas,
    is_fall_start,
    is_covid_loose_fall21,
    is_christmas_shopping,
)
from PredictionFunction.Datasets.Holidays.LosTacos.Restaurants.stavanger_holidays import (
    christmas_day,
    new_year_eve,
    # firstweek_jan,
    # new_years_day,
    fadder_week,
    # first_may,
    eight_may,
    seventeenth_may,
    easter,
    easter_mondaydayoff,
    landstreff_russ,
    # pinse,
    # himmelfart,
    fjoge,
    stor_konsert_ukedag,
    maijazz_lørdag,
    military_excercise,
    outliers,
    closed_days,
    cruise_ship_arrivals_holiday,
    pay_day,
    utopia_friday,
    utopia_saturday,
    skeiva_natta,
)

from PredictionFunction.Datasets.Holidays.LosTacos.common_holidays import (
    first_may,
    firstweek_jan,
    new_years_day,
    pinse,
    himmelfart,
    halloween_weekend,
    halloween_day,
    hostferie_sor_ostlandet_weekdend,
    vinterferie_vestlandet_weekend,
    vinterferie_vestlandet_weekend_before,
    first_weekend_christmas_school_vacation,
)

from PredictionFunction.Datasets.Regressors.weather_regressors import(
    # warm_dry_weather_spring,
    # warm_and_dry_future,
    # heavy_rain_fall_weekday,
    # heavy_rain_fall_weekday_future,
    heavy_rain_fall_weekend,
    heavy_rain_fall_weekend_future,
    heavy_rain_winter_weekday,
    heavy_rain_winter_weekday_future,
    heavy_rain_winter_weekend,
    heavy_rain_winter_weekend_future,
    # heavy_rain_spring_weekday,
    # heavy_rain_spring_weekday_future,
    # heavy_rain_spring_weekend,
    # heavy_rain_spring_weekend_future,
    non_heavy_rain_fall_weekend,
    non_heavy_rain_fall_weekend_future,

)
def stavanger(prediction_category,restaurant,merged_data,historical_data,future_data):
    print("starting loc spec stavanger")
    sales_data_df = historical_data
    sales_data_df = sales_data_df.rename(columns={"date": "ds"})
    sales_data_df["ds"] = pd.to_datetime(sales_data_df["ds"])

    future_data = future_data.rename(columns={"date": "ds"})
    future_data["ds"] = pd.to_datetime(future_data["ds"])

    merged_data = merged_data.rename(columns={"date": "ds"})
    merged_data["ds"] = pd.to_datetime(merged_data["ds"])
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

    # df = warm_dry_weather_spring(df)
    # df = heavy_rain_fall_weekday(df)
    df = heavy_rain_fall_weekend(df)
    df = heavy_rain_winter_weekday(df)
    df = heavy_rain_winter_weekend(df)
    # df = heavy_rain_spring_weekday(df)
    # df = heavy_rain_spring_weekend(df)
    df = non_heavy_rain_fall_weekend(df)
    m = Prophet()

    ### Holidays and other repeating outliers
    m.add_country_holidays(country_name="NO")

    ONS = pd.DataFrame(
        {
            "holiday": "ONS",
            "ds": pd.to_datetime(["2022-08-31"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

    musikkfestrogaland = pd.DataFrame(
        {
            "holiday": "Musikkfest Rogaland",
            "ds": pd.to_datetime([""]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

    holidays = pd.concat(
        (
            christmas_day,
            firstweek_jan,
            new_year_eve,
            fadder_week,
            landstreff_russ,
            first_may,
            eight_may,
            easter,
            easter_mondaydayoff,
            seventeenth_may,
            pinse,
            fjoge,
            stor_konsert_ukedag,
            himmelfart,
            ONS,
            outliers,
            closed_days,
            cruise_ship_arrivals_holiday,
            maijazz_lørdag,
            utopia_friday,
            utopia_saturday,
            skeiva_natta,
            military_excercise,
            hostferie_sor_ostlandet_weekdend,
            halloween_day,
            halloween_weekend,
            vinterferie_vestlandet_weekend_before,
            vinterferie_vestlandet_weekend,
            first_weekend_christmas_school_vacation,
        )
    )

    print("done with holidays")

    ### Conditional seasonality - weekly

    df["fellesferie"] = df["ds"].apply(is_fellesferie_stavanger)

    df["is_may"] = df["ds"].apply(is_may)

    # Define a function to check if the date is within the period of heavy COVID restrictions

    # Add new columns in your dataframe to indicate if a date is within or outside the restrictions period
    df["covid_restriction_christmas"] = df["ds"].apply(is_covid_restriction_christmas)

    # Some weeks have the same weekly seasonality but more extreme and just higher. Add that here
    # Convert 'ds' column to datetime if it is not already
    df["ds"] = pd.to_datetime(df["ds"])
    # Calculate the week number for each date
    df["week_number"] = df["ds"].dt.isocalendar().week

    # Convert 'ds' column to datetime if it is not already
    df["ds"] = pd.to_datetime(df["ds"])

    # Define the start and end dates for the specific date interval
    start_date = "2022-08-22"
    end_date = "2022-09-11"
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

    df["covid_loose_fall21"] = df["ds"].apply(is_covid_loose_fall21)

    df["christmas_shopping"] = df["ds"].apply(is_christmas_shopping)

    # function for calculating the days before and after the last workday
    def calculate_days(df, last_working_day):
        # Convert 'ds' column to datetime if it's not already
        df["ds"] = pd.to_datetime(df["ds"])

        # Convert last_working_day list to datetime
        last_working_day = pd.to_datetime(pd.Series(last_working_day))

        df["days_since_last"] = df["ds"].apply(
            lambda x: min([abs(x - y).days for y in last_working_day if x >= y],default=0)
        )
        df["days_until_next"] = df["ds"].apply(
            lambda x: min([abs(x - y).days for y in last_working_day if x <= y],default=0)
        )

        # Set 'days_since_last' and 'days_until_next' to 0 for days that are not within the -5 to +5 range
        df.loc[df["days_since_last"] > 5, "days_since_last"] = 0

        return df

    # The training DataFrame (df) should also include 'days_since_last' and 'days_until_next' columns.
    df = calculate_days(df, last_working_day)

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
            changepoint_range=0.95,
            changepoint_prior_scale=0.15,
            seasonality_mode="multiplicative",
        )

    # m.add_regressor('days_since_last')

    m.add_regressor("custom_regressor")
    # m.add_regressor('covid_restriction')
    # m.add_seasonality(name='monthly', period=30.5, fourier_order=5, condition_name='specific_month')
    m.add_seasonality(
        name="covid_restriction_christmas",
        period=7,
        fourier_order=1000,
        condition_name="covid_restriction_christmas",
    )

    # m.add_seasonality(name='weekly_fall_start', period=7, fourier_order=3,
    #                  condition_name='fall_start')

    m.add_seasonality(
        name="covid_loose_fall21",
        period=7,
        fourier_order=3,
        condition_name="covid_loose_fall21",
    )

    m.add_seasonality(
        name="christmas_shopping",
        period=7,
        fourier_order=3,
        condition_name="christmas_shopping",
    )

    # m.add_seasonality(name='weekly_fellesferie', period=7, fourier_order=3, condition_name='fellesferie')

    # m.add_seasonality(name='weekly_in_may', period=7, fourier_order=3, condition_name='is_may')

    m.add_seasonality(name="monthly", period=30.5, fourier_order=5)

    # Add the conditional regressor to the model
    m.add_regressor("sunshine_amount", standardize=False)
    # m.add_regressor("warm_and_dry")
    # m.add_regressor("heavy_rain_fall_weekday")
    m.add_regressor("heavy_rain_fall_weekend")
    m.add_regressor("heavy_rain_winter_weekday")
    m.add_regressor("heavy_rain_winter_weekend")
    # m.add_regressor("heavy_rain_spring_weekday")
    # m.add_regressor("heavy_rain_spring_weekend")
    m.add_regressor("non_heavy_rain_fall_weekend")

    print("done with seasonalities")
    if prediction_category == "hour":
        df["ds"] = pd.to_datetime(
            df["ds"].astype(str) + " " + df["hour"].astype(str) + ":00:00"
        )

    print("før get adjusted")
    """ def get_adjusted_total_net(prediction_category):
        m, future, _ = location_function(prediction_category)
        # Predict the total net
        forecast = m.predict(future)
        # Extract the predicted total net
        adjusted_total_net = forecast['yhat']
        return adjusted_total_net

    m.fit(df)
    print("etter adjusted")

    # Call the function with the appropriate prediction category
    adjusted_total_net = get_adjusted_total_net(prediction_category="day")

    #add adjusted total_net to the df
    df['adjusted_total_net'] = adjusted_total_net """

    # get the weekly_seasonalities
    print("kommet til cluster")
    clusters = weekly_seasonalities(df)

    for cluster_label, weeks in clusters.items():
        # Here, you would define the custom seasonality parameters for each cluster
        # You might want to define a custom seasonality function, or apply different parameters based on the cluster label
        seasonality_params = {
            "name": f"weekly_{cluster_label}",
            "period": 7,
            "fourier_order": 3,  # Adjust as needed
            # Other parameters may go here as needed
        }

        # Add the custom seasonality to the model
        m.add_seasonality(**seasonality_params)

    # Fit the model to your data
    m.fit(df)
    print("klar for future")

    if prediction_category == "hour":
        future = m.make_future_dataframe(periods=700, freq="H")
        for weekday in range(7):
            future[f"weekday_{weekday}"] = future["ds"].dt.weekday == weekday
    else:
        future = m.make_future_dataframe(periods=60, freq="D")

    # Apply the mapping function to the dates in the future DataFrame
    def get_cluster_label(date):
        week_number = date.isocalendar().week
        for cluster_label, weeks in clusters.items():
            if week_number in weeks:
                return cluster_label
        return None  # Default if week number not found in clusters

    future["cluster_label"] = future["ds"].apply(get_cluster_label)


    future["sunshine_amount"] = merged_data["sunshine_amount"]

    # add the last working day and the +/- 5 days
    # future = calculate_days(future, last_working_day)

    ## Add conditional seasonality
    future["fellesferie"] = future["ds"].apply(is_fellesferie_stavanger)

    # Add 'is_may' column to future DataFrame
    future["is_may"] = future["ds"].apply(is_may)

    future["covid_restriction_christmas"] = future["ds"].apply(
        is_covid_restriction_christmas
    )

    future["fall_start"] = future["ds"].apply(is_fall_start)

    future["covid_loose_fall21"] = future["ds"].apply(is_covid_loose_fall21)

    future["christmas_shopping"] = future["ds"].apply(is_christmas_shopping)

    future["rain_sum"] = merged_data["rain_sum"]
    future["sunshine_amount"] = merged_data["sunshine_amount"]
    future["windspeed"] = merged_data["windspeed"]
    future["air_temperature"] = merged_data["air_temperature"]
    # future = warm_and_dry_future(future)
    # future = heavy_rain_fall_weekday_future(future)
    future = heavy_rain_fall_weekend_future(future)
    future = heavy_rain_winter_weekday_future(future)
    future = heavy_rain_winter_weekend_future(future)
    # future = heavy_rain_spring_weekday_future(future)
    # future = heavy_rain_spring_weekend_future(future)
    future = non_heavy_rain_fall_weekend_future(future)
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
    future.fillna(0, inplace=True)
    return m, future, df


def location_function(prediction_category,restaurant,merged_data,historical_data,future_data):
    return stavanger(prediction_category,restaurant,merged_data,historical_data,future_data)