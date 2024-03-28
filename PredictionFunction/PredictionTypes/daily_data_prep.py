import pandas as pd
import datetime as dt
import numpy as np
from PredictionFunction.utils.fetch_sales_data import fetch_salesdata
from PredictionFunction.meta_tables import data
from PredictionFunction.utils.fetch_weather_data import fetch_weather


def prepare_data(company, restaurant, start_date, end_date):
    # Create a pandas DataFrame
    filtered_sales_data = fetch_salesdata(company, restaurant, start_date, end_date)
    restaurant_list = pd.DataFrame(data)
    # Convert the filtered SalesData to a DataFrame
    sales_data_df = filtered_sales_data
    end_date = pd.to_datetime(end_date)
    weather_end_date = end_date + dt.timedelta(days=45)

    city_data = restaurant_list.loc[restaurant_list["Restaurant"] == restaurant, "City"]
    city = city_data.iloc[0] if not city_data.empty else None

    if city is not None:
        filtered_weather_data = fetch_weather(city, start_date, end_date)
    else:
        filtered_weather_data = None
        print(f"No city found for the restaurant {restaurant}")

    # Create a dataframe with all dates from the start to the end
    all_dates_df = pd.DataFrame(
        {"date": pd.date_range(start=start_date, end=weather_end_date)}
    )

    # Add relevant new weather data columns
    # filtered_weather_data = []
    weather_data_df = filtered_weather_data

    weather_data_df = weather_data_df.drop_duplicates(
        subset=["time", "city"], keep="first"
    )

    weather_data_df = weather_data_df.rename(
        columns={"time": "date"}
    )  # Rename 'time' column to 'date'

    sales_data_df["date"] = pd.to_datetime(
        sales_data_df["date"], format="%Y-%m-%d %H"
    ).dt.date

    # Only use sunshine in the relevant hour intervals based on feedback from the restaurant's manager'
    def get_relevant_hours(row):
        # Get the day of the week (0 is Monday, 6 is Sunday)
        date = row["date"]
        day_of_week = date.dayofweek
        hour = row["date"].hour
        date = date.strftime("%Y-%m-%d")
        if ("2022-07-11" < date < "2022-07-28") or ("2023-07-10" < date < "2023-07-28"):
            ranges = {
                0: (11, 21),  # Monday
                1: (11, 21),  # Tuesday
                2: (11, 21),  # Wednesday
                3: (11, 21),  # Thursday
                4: (11, 23),  # Friday
                5: (11, 23),  # Saturday
                6: (11, 21),  # Sunday
            }
        # Define the hour ranges for each day
        else:
            ranges = {
                0: (15, 21),  # Monday
                1: (15, 21),  # Tuesday
                2: (15, 21),  # Wednesday
                3: (15, 21),  # Thursday
                4: (14, 23),  # Friday
                5: (12, 23),  # Saturday
                6: (14, 21),  # Sunday
            }

        start, end = ranges[day_of_week]

        # Return True if the current hour falls within the range for the current day
        return start <= hour < end

    # print date and sunshine_amount of weather_data_df

    # replace Nan with 0 for weather_data_df
    weather_data_df["sunshine_amount"].fillna(0, inplace=True)
    # weather_data_df['sunshine_amount'].fillna(0, inplace=True)

    # Apply the function to create a new column indicating whether each row falls within the desired hours
    weather_data_df["relevant_hours"] = weather_data_df.apply(
        get_relevant_hours, axis=1
    )

    # print(weather_data_df[['date', 'sunshine_amount']])
    # sum sunshine_amount in weather_data_df if relevant_hours is true
    weather_data_df["sunshine_amount"] = weather_data_df["sunshine_amount"].where(
        weather_data_df["relevant_hours"] == True, 0
    )
    weather_data_df["sunshine_amount"] = weather_data_df["sunshine_amount"].where(
        weather_data_df["relevant_hours"] == True, 0
    )

    # if rain_sum=0 for the hours 17-23 and sum sunshine_amount between 15-18 < 120, set sunshine_amount = 60 for the hours 18-23
    weather_data_df.loc[
        (weather_data_df["date"].dt.hour == 18)
        & (weather_data_df["rain_sum"] == 0)
        & (weather_data_df["sunshine_amount"].between(15, 18) > 120),
        "sunshine_amount",
    ] = 60
    weather_data_df.loc[
        (weather_data_df["date"].dt.hour == 19)
        & (weather_data_df["rain_sum"] == 0)
        & (weather_data_df["sunshine_amount"].between(15, 18) > 120),
        "sunshine_amount",
    ] = 60
    weather_data_df.loc[
        (weather_data_df["date"].dt.hour == 20)
        & (weather_data_df["rain_sum"] == 0)
        & (weather_data_df["sunshine_amount"].between(15, 18) > 120),
        "sunshine_amount",
    ] = 60
    weather_data_df.loc[
        (weather_data_df["date"].dt.hour == 21)
        & (weather_data_df["rain_sum"] == 0)
        & (weather_data_df["sunshine_amount"].between(15, 18) > 120),
        "sunshine_amount",
    ] = 60
    weather_data_df.loc[
        (weather_data_df["date"].dt.hour == 22)
        & (weather_data_df["rain_sum"] == 0)
        & (weather_data_df["sunshine_amount"].between(15, 18) > 120),
        "sunshine_amount",
    ] = 60
    weather_data_df.loc[
        (weather_data_df["date"].dt.hour == 23)
        & (weather_data_df["rain_sum"] == 0)
        & (weather_data_df["sunshine_amount"].between(15, 18) > 120),
        "sunshine_amount",
    ] = 60

    weather_data_df["sunshine_amount"] = np.where(
        weather_data_df["date"].dt.month.isin(range(3, 10)),
        weather_data_df["sunshine_amount"],
        0,
    )
    weather_data_df["sunshine_amount"].fillna(0, inplace=True)

    "set rain_sum between 02-10 to 0"
    weather_data_df.loc[
        (weather_data_df["date"].dt.hour.between(2, 10)), "rain_sum"
    ] = 0

    # make the date field in weather_data_df date only
    weather_data_df["date"] = weather_data_df["date"].dt.date

    # group weather_data_df by date and sum the total sunshine_amount
    # weather_data_df = weather_data_df.groupby('date')['sunshine_amount'].sum().reset_index()
    weather_data_df = (
        weather_data_df.groupby("date")
        .agg(
            {
                "air_temperature": "max",
                "rain_sum": "sum",
                "windspeed": "max",
                "sunshine_amount": "sum",
            }
        )
        .reset_index()
    )

    # Make sure 'date' column in all_dates_df is also of type 'date'
    all_dates_df["date"] = pd.to_datetime(all_dates_df["date"]).dt.date

    # Merge all_dates_df with weather_data_df, fill missing values with 0
    weather_data_df = pd.merge(all_dates_df, weather_data_df, on="date", how="left")
    weather_data_df.fillna(0, inplace=True)

    # print(weather_data_df[['date', 'sunshine_amount' ,'rain_sum']].head(1000))

    # replace NaN values with 0

    # group sales data by date and sum the total_gross
    sales_data_df = sales_data_df.groupby("date")["total_net"].sum().reset_index()

    # print all rows from salesdata from august 2023 with total_net and date/ds columns, take away the max rows
    pd.set_option("display.max_rows", None)

    # group weather data by date and sum the total rain_sum
    # weather_data_df = weather_data_df.groupby('date')['sunshine_amount'].sum().reset_index()

    # take away dataframe head rows limit
    pd.set_option("display.max_rows", None)
    # print(weather_data_df[['date', 'sunshine_amount']])
    merged_data = weather_data_df.merge(sales_data_df, on="date", how="left")
    merged_data["total_net"].fillna(0, inplace=True)
    # merged_data = sales_data_df
    # fill missing dates with 0, as these are closed days
    full_date_range = pd.date_range(
        start=min(merged_data["date"]), end=max(merged_data["date"])
    )
    df_full = pd.DataFrame(full_date_range, columns=["date"])
    df_full["date"] = df_full["date"].astype("object")
    merged_data = pd.merge(merged_data, df_full, on="date", how="left")
    merged_data.loc[merged_data["total_net"].isnull(), "total_net"] = 0
    merged_data["date"] = pd.to_datetime(merged_data["date"])
    # merged_data.loc[merged_data['total_gross'].isnull(), 'total_gross'] = 0

    pd.set_option("display.max_rows", None)

    # Split the data into two periods
    historical_data = merged_data[merged_data["date"] <= end_date]
    future_data = merged_data[merged_data["date"] > end_date]
    # delete the total_gross values from future_data
    # future_data = future_data['total_gross'] = 0

    return merged_data, historical_data, future_data
