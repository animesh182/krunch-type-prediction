import pandas as pd
import datetime as dt
from PredictionFunction.Datasets.OpeningHours.lostacos_opening_hours import restaurant_opening_hours

def hourly_sales(company, restaurant, start_date, end_date):
    #This function processes the data for the given restaurant and date range.

    # Create a pandas DataFrame
    restaurant_city_df = pd.DataFrame(data)

    if restaurant=='Oslo Torggata':
        filtered_sales_data = SalesData.objects.filter(
            company=company,
            restaurant=restaurant,
            date__gte=start_date,
            date__lte=end_date,
        ).exclude(Q(qty__gt=30))   
    else:
        filtered_sales_data = SalesData.objects.filter(
        company=company,
        restaurant=restaurant,
        date__gte=start_date,
        date__lte=end_date,
    ).exclude(article_group='Catering')

    # Convert the filtered SalesData to a DataFrame
    sales_data_hourly = filtered_sales_data.annotate(
        hour=TruncHour('date')
    ).annotate(
        hour=Extract('hour', 'hour')
    ).values('hour').annotate(total_net_sum=Sum('total_net')).order_by('date')

    sales_data_hourly = pd.DataFrame(list(sales_data_hourly.values()))
    sales_data_hourly['date'] = sales_data_hourly['date'].dt.date


    weather_end_date = end_date + dt.timedelta(days=45)
    city_data = restaurant_city_df.loc[restaurant_city_df['Restaurant'] == restaurant, 'City']
    city = city_data.iloc[0] if not city_data.empty else None

    if city is not None:
        filtered_weather_data = Weather.objects.filter(
            city=city,
            time__gte=start_date,
            time__lte=weather_end_date
        )
    else:
        print(f"No city found for the restaurant {restaurant}")

    #Add relevant new weather data columns
    start_datetime = pd.to_datetime(start_date)
    start_datetime = start_datetime.replace(minute=15)

    end_datetime = pd.to_datetime(weather_end_date)
    end_datetime = end_datetime.replace(minute=15)

    all_dates_df = pd.DataFrame({
        'date': pd.date_range(start=start_datetime, end=end_datetime, freq='1H')
    })
    all_dates_df['date'] = pd.to_datetime(all_dates_df['date'])

    #filtered_weather_data = []
    weather_data_df = filtered_weather_data.annotate(
        hour=TruncHour('time')
    ).annotate(
        hour=Extract('hour', 'hour')
    ).values('hour').order_by('time')
    weather_data_df = pd.DataFrame(list(weather_data_df.values()))
    weather_data_df = weather_data_df.rename(columns={'time': 'date'})
    #replace Nan with 0 for weather_data_df
    weather_data_df['sunshine_amount'].fillna(0.0, inplace=True)


    def get_relevant_hours(row):
        # Get the day of the week (0 is Monday, 6 is Sunday)
        date=row['date']
        day_of_week = date.dayofweek
        hour = row['date'].hour
        date = date.strftime('%Y-%m-%d')
        if ('2022-07-11'< date < '2022-07-28') or ('2023-07-10'<date<'2023-07-28'):
            ranges = {
                0: (11, 23),  # Monday
                1: (11, 23),  # Tuesday
                2: (11, 23),  # Wednesday
                3: (11, 23),  # Thursday
                4: (11, 23),  # Friday
                5: (11, 23),  # Saturday
                6: (11, 23)  # Sunday
            }
        # Define the hour ranges for each day
        else:
            ranges = {
                0: (15, 23),  # Monday
                1: (15, 23),  # Tuesday
                2: (15, 23),  # Wednesday
                3: (15, 23),  # Thursday
                4: (14, 23),  # Friday
                5: (12, 23),  # Saturday
                6: (14, 23)  # Sunday
            }

        start, end = ranges[day_of_week]

        # Return True if the current hour falls within the range for the current day
        return start <= hour < end
    weather_data_df['relevant_hours'] = weather_data_df.apply(get_relevant_hours, axis=1)
    weather_data_df['sunshine_amount'] = weather_data_df['sunshine_amount'].where(weather_data_df['relevant_hours'] == True, 0)

    weather_data_df = weather_data_df.groupby('date').agg({
        'air_temperature': 'max',
        'rain_sum': 'sum',
        'windspeed': 'max',  
        'sunshine_amount': 'sum'
    }).reset_index()

    weather_data_df = pd.merge(all_dates_df, weather_data_df, on='date', how='left')
    weather_data_df.fillna(0, inplace=True)

    weather_data_df['hour'] = pd.to_datetime(weather_data_df['date']).dt.hour
    weather_data_df['date'] = weather_data_df['date'].dt.date
 
    #group sales data by date and sum the total_gross
    sales_data_hourly = sales_data_hourly.groupby(['date', 'hour'])['total_net'].sum().reset_index()
    #take away dataframe head rows limit
    pd.set_option('display.max_rows', None)
    merged_data = weather_data_df.merge(sales_data_hourly, on=['hour', 'date'], how='left')
    merged_data['total_net'].fillna(0, inplace=True)
    #merged_data = sales_data_df

    #fill missing dates with 0, as these are closed days
    full_date_range = pd.date_range(start=min(merged_data['date']), end=max(merged_data['date']))
    df_full = pd.DataFrame(full_date_range, columns=['date'])
    df_full['date'] = df_full['date'].astype('object')
    merged_data = pd.merge(merged_data, df_full, on=['date'], how='left')
    merged_data.loc[merged_data['total_net'].isnull(), 'total_net'] = 0


    #Delete rows in the df outside of each restaurants opening hours
    # Get the opening hours for the specific restaurant
    restaurant_data = restaurant_opening_hours[restaurant]

    from datetime import datetime
    # Add a new column to keep track of rows to keep
    merged_data['keep'] = False

    # Iterate through the rows of the DataFrame
    for index, row in merged_data.iterrows():
        # Convert the date to a datetime object and get the day of the week (0 is Monday, 6 is Sunday)
        weekday = datetime(row['date'].year, row['date'].month, row['date'].day).weekday()
        
        # Get the starting and ending hours for the current weekday from the restaurant_data
        hours = restaurant_opening_hours[restaurant][weekday]
        starting_hour = int(hours['starting'].split(':')[0])
        ending_hour = int(hours['ending'].split(':')[0])
        
        # Check if the current hour falls within the opening hours
        if ending_hour == 0:  # Special case for midnight
            if starting_hour <= row['hour'] <= 23:  # Include the hour 23
                merged_data.loc[index, 'keep'] = True
        elif ending_hour < starting_hour:  # Closing time is on the next day
            if starting_hour <= row['hour'] or row['hour'] <= ending_hour:
                merged_data.loc[index, 'keep'] = True
        else:  # Closing time is on the same day
            if starting_hour <= row['hour'] <= ending_hour:
                merged_data.loc[index, 'keep'] = True


    # Split the data into two periods
    historical_data = merged_data[merged_data['date'] <= end_date]
    future_data = merged_data[merged_data['date'] > end_date]

    return merged_data, historical_data, future_data






