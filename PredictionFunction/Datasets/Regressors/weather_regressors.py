import pandas as pd

#### In this file we add generic weather regressions. We import company-restaurant specific parameters from other files to be used in these regressions
#### and then import the regressions in this file to each location specific restaurant file


#### Add weather parameters to the df

def add_weather_parameters(prediction_category, sales_data_df):
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

    return df



##### GOOD WEATHER REGRESSORS

## Warm and dry weather
def warm_dry_weather_spring(df):
     # Add a column for the day of the week
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month
    
    # Calculate the rolling mean of the last 10 days for air_temperature
    df['rolling_avg_temp'] = df['air_temperature'].rolling(window=10, min_periods=1).mean()

    # Now, define the warm and cold thresholds based on the rolling averages
    warm_threshold = df['rolling_avg_temp'].quantile(0.75)  # Warm days based on rolling temperature

    # You may also want to define what constitutes 'dry' and 'wet'
    dry_threshold = 0

    #Apply the conditions for warm and dry weather
    df['warm_and_dry'] = (
        (df['air_temperature'] >= warm_threshold) & 
        (df['rain_sum'] <= dry_threshold) & 
        (df['day_of_week'].isin([4, 5, 6])) &
        (df['month'].isin([3, 4, 5, 6]))
    ).astype(int)
    
    return df

def warm_and_dry_future(future):
    # Convert 'date' column to datetime if it's not already
    future['ds'] = pd.to_datetime(future['ds'])


    # Add day of the week and month to the future DataFrame
    future['day_of_week'] = future['ds'].dt.dayofweek
    future['month'] = future['ds'].dt.month

    # Calculate the rolling mean of the last 10 days for air_temperature
    future['rolling_avg_temp'] = future['air_temperature'].rolling(window=10, min_periods=1).mean()

    # Now, define the warm and cold thresholds based on the rolling averages
    # Use the .quantile() method on the rolling average temperatures
    warm_threshold = future['rolling_avg_temp'].quantile(0.75)  # Warm days
    cold_threshold = future['rolling_avg_temp'].quantile(0.25)  # Cold days

    # Set a fixed threshold for rain to define 'wet' days
    fixed_heavy_rain_threshold = 10

    # Apply the conditions to determine 'warm_and_dry' and 'cold_and_wet' for the future DataFrame
    # Here, we don't filter by day of the week because we want to apply this to the full future forecast
    future['warm_and_dry'] = (
        (future['rolling_avg_temp'] >= warm_threshold) & 
        (future['rain_sum'] <= 0) & 
        (future['day_of_week'].isin([4, 5, 6])) &
        (future['month'].isin([3, 4, 5, 6]))  # Only spring season
    ).astype(int)

    return future




###### RAIN REGRESSORS

## Heavy rain fall
def heavy_rain_fall_weekday(df):
     # Add a column for the day of the week
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month

    #Define what constitutes 'dry' and 'wet'
    fixed_heavy_rain_threshold = 10

    #Apply the conditions for heavy rain weekday
    df['heavy_rain_fall_weekday'] = (
        (df['rain_sum'] > fixed_heavy_rain_threshold) & 
        (df['day_of_week'].isin([0, 1, 2, 3])) &
        (df['month'].isin([9, 10, 11]))  # Assuming fall is September, October, November
    ).astype(int)
  
    return df

def heavy_rain_fall_weekday_future(future):
    # Convert 'date' column to datetime if it's not already
    future['ds'] = pd.to_datetime(future['ds'])
    # Set a fixed threshold for rain to define 'wet' days
    fixed_heavy_rain_threshold = 10

    # Add day of the week and month to the future DataFrame
    future['day_of_week'] = future['ds'].dt.dayofweek
    future['month'] = future['ds'].dt.month

    #Fall rain
    future['heavy_rain_fall_weekday'] = (
        (future['rain_sum'] > fixed_heavy_rain_threshold) &
        (future['day_of_week'].isin([0, 1, 2, 3])) &  # Presumably only for fall season, but not specified
        (future['month'].isin([9, 10, 11]))  # Only fall season

    ).astype(int)

  
    return future


def heavy_rain_fall_weekend(df):
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month

    #Define what constitutes 'dry' and 'wet'
    fixed_heavy_rain_threshold = 10

    # Apply the conditions for heavy rain weekend
    df['heavy_rain_fall_weekend'] = (
        (df['rain_sum'] > fixed_heavy_rain_threshold) & 
        (df['day_of_week'].isin([4, 5])) &
        (df['month'].isin([9, 10, 11, 12]))  # Assuming fall is September, October, November
    ).astype(int)

    #df['non_heavy_rain_fall_weekend'] = (
    #    (df['rain_sum'] <= 0) & 
    #    (df['day_of_week'].isin([4, 5])) &
    #    (df['month'].isin([9, 10, 11, 12]))  # Assuming fall is September, October, November
    #).astype(int)
    
    return df

def heavy_rain_fall_weekend_future(future):
    # Convert 'date' column to datetime if it's not already
    future['ds'] = pd.to_datetime(future['ds'])
    # Set a fixed threshold for rain to define 'wet' days
    fixed_heavy_rain_threshold = 10

    # Add day of the week and month to the future DataFrame
    future['day_of_week'] = future['ds'].dt.dayofweek
    future['month'] = future['ds'].dt.month

    future['heavy_rain_fall_weekend'] = (
        (future['rain_sum'] > fixed_heavy_rain_threshold) &
        (future['day_of_week'].isin([4, 5])) &  # Presumably only for fall season, but not specified
        (future['month'].isin([9, 10, 11, 12]))  # Only fall season

    ).astype(int)

    #future['non_heavy_rain_fall_weekend'] = (
    #    (future['rain_sum'] <= 0) &
    #    (future['day_of_week'].isin([4, 5])) &  # Presumably only for fall season, but not specified
    #    (future['month'].isin([9, 10, 11, 12]))  # Only fall season

    #).astype(int)

    return future


def non_heavy_rain_fall_weekend(df):
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month

    #Define what constitutes 'dry' and 'wet'
    fixed_heavy_rain_threshold = 10


    df['non_heavy_rain_fall_weekend'] = (
        (df['rain_sum'] <= 0) & 
        (df['day_of_week'].isin([4, 5])) &
        (df['month'].isin([9, 10, 11, 12]))  # Assuming fall is September, October, November
    ).astype(int)
    
    return df

def non_heavy_rain_fall_weekend_future(future):
    # Convert 'date' column to datetime if it's not already
    future['ds'] = pd.to_datetime(future['ds'])
    # Set a fixed threshold for rain to define 'wet' days
    fixed_heavy_rain_threshold = 10

    # Add day of the week and month to the future DataFrame
    future['day_of_week'] = future['ds'].dt.dayofweek
    future['month'] = future['ds'].dt.month


    future['non_heavy_rain_fall_weekend'] = (
        (future['rain_sum'] <= 0) &
        (future['day_of_week'].isin([4, 5])) &  # Presumably only for fall season, but not specified
        (future['month'].isin([9, 10, 11, 12]))  # Only fall season

    ).astype(int)

    return future




## Heavy rain winter
def heavy_rain_winter_weekday(df):
     # Add a column for the day of the week
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month

    #Define what constitutes 'dry' and 'wet'
    fixed_heavy_rain_threshold = 10

    #Apply the conditions for heavy rain weekday
    df['heavy_rain_winter_weekday'] = (
        (df['rain_sum'] > fixed_heavy_rain_threshold) & 
        (df['day_of_week'].isin([0, 1, 2, 3])) &
        (df['month'].isin([1, 2]))  # Assuming fall is September, October, November
    ).astype(int)
  
    return df

def heavy_rain_winter_weekday_future(future):
    # Convert 'date' column to datetime if it's not already
    future['ds'] = pd.to_datetime(future['ds'])
    # Set a fixed threshold for rain to define 'wet' days
    fixed_heavy_rain_threshold = 10

    # Add day of the week and month to the future DataFrame
    future['day_of_week'] = future['ds'].dt.dayofweek
    future['month'] = future['ds'].dt.month

    #Fall rain
    future['heavy_rain_winter_weekday'] = (
        (future['rain_sum'] > fixed_heavy_rain_threshold) &
        (future['day_of_week'].isin([0, 1, 2, 3])) &  # Presumably only for fall season, but not specified
        (future['month'].isin([1, 2]))  # Only fall season

    ).astype(int)

  
    return future

def heavy_rain_winter_weekend(df):
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month

    #Define what constitutes 'dry' and 'wet'
    fixed_heavy_rain_threshold = 10

    # Apply the conditions for heavy rain weekend
    df['heavy_rain_winter_weekend'] = (
        (df['rain_sum'] > fixed_heavy_rain_threshold) & 
        (df['day_of_week'].isin([4, 5])) &
        (df['month'].isin([1, 2]))  # winter
    ).astype(int)
    
    return df

def heavy_rain_winter_weekend_future(future):
    # Convert 'date' column to datetime if it's not already
    future['ds'] = pd.to_datetime(future['ds'])
    # Set a fixed threshold for rain to define 'wet' days
    fixed_heavy_rain_threshold = 10

    # Add day of the week and month to the future DataFrame
    future['day_of_week'] = future['ds'].dt.dayofweek
    future['month'] = future['ds'].dt.month

    future['heavy_rain_winter_weekend'] = (
        (future['rain_sum'] > fixed_heavy_rain_threshold) &
        (future['day_of_week'].isin([4, 5])) &  # Presumably only for fall season, but not specified
        (future['month'].isin([1, 2]))  # Only fall season

    ).astype(int)

    return future





## Heavy rain spring
def heavy_rain_spring_weekday(df):
     # Add a column for the day of the week
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month

    #Define what constitutes 'dry' and 'wet'
    fixed_heavy_rain_threshold = 10

    df['heavy_rain_spring_weekday'] = (
        (df['rain_sum'] > fixed_heavy_rain_threshold) & 
        (df['day_of_week'].isin([0, 1, 2, 3])) &
        (df['month'].isin([3, 4, 5]))  # Assuming fall is September, October, November
    ).astype(int)

    return df

def heavy_rain_spring_weekday_future(future):
    # Convert 'date' column to datetime if it's not already
    future['ds'] = pd.to_datetime(future['ds'])
    # Set a fixed threshold for rain to define 'wet' days
    fixed_heavy_rain_threshold = 10

    # Add day of the week and month to the future DataFrame
    future['day_of_week'] = future['ds'].dt.dayofweek
    future['month'] = future['ds'].dt.month

    #Spring rain
    future['heavy_rain_spring_weekday'] = (
        (future['rain_sum'] > fixed_heavy_rain_threshold) &
        (future['day_of_week'].isin([0, 1, 2, 3])) &  # Presumably only for fall season, but not specified
        (future['month'].isin([3, 4, 5]))  # Only fall season

    ).astype(int)

    return future


def heavy_rain_spring_weekend(df):
     # Add a column for the day of the week
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month

    #Define what constitutes 'dry' and 'wet'
    dry_threshold = 0
    fixed_heavy_rain_threshold = 10

    df['heavy_rain_spring_weekend'] = (
        (df['rain_sum'] > fixed_heavy_rain_threshold) & 
        (df['day_of_week'].isin([4, 5])) &
        (df['month'].isin([3, 4, 5]))  # Assuming fall is September, October, November
    ).astype(int)
    
    return df

def heavy_rain_spring_weekend_future(future):
    # Convert 'date' column to datetime if it's not already
    future['ds'] = pd.to_datetime(future['ds'])
    # Set a fixed threshold for rain to define 'wet' days
    fixed_heavy_rain_threshold = 10

    # Add day of the week and month to the future DataFrame
    future['day_of_week'] = future['ds'].dt.dayofweek
    future['month'] = future['ds'].dt.month

    future['heavy_rain_spring_weekend'] = (
        (future['rain_sum'] > fixed_heavy_rain_threshold) &
        (future['day_of_week'].isin([4, 5])) &  # Presumably only for fall season, but not specified
        (future['month'].isin([3, 4, 5]))  # Only fall season

    ).astype(int)

    return future

