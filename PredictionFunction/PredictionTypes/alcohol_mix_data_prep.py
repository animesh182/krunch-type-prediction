import pandas as pd
import datetime as dt
import numpy as np

def product_mix_predictions(company, restaurant, start_date, end_date):
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
    sales_data_df = pd.DataFrame(list(filtered_sales_data.values()))
    sales_data_df['date'] = pd.to_datetime(sales_data_df['date'], format='%Y-%m-%d %H').dt.date

    # Convert alcohol related columns to boolean values and map to 1 for True, 0 for False
    # List of article_group values that should be set to 1 in article_supergroup
    
    if company == 'Los Tacos' or company == 'Krunch':
        article_group_values_for_one = [
            'Ã˜l',
            'Alcohol',
            'Beer',
            'Beer after 21',
            'Brennevin',
            'Cocktails',
            'Rusbrus/Cider',
            'Spirits',
            'Tequila',
            'Vin',
            'Wine',
            'Wine, Taco Tuesday',
            'Øl',
        ]
    else:
        article_group_values_for_one = [
            'Cocktails',
            'Hetvin',
            'Hvitvin',
            'Musserende Vin',
            'Øl',
            'Rødvin',
            'Whiskey',
        ]



    # Use the isin function to check if article_group is in the list
    # sales_data_df['article_supergroup'] = sales_data_df['article_group'].isin(article_group_values_for_one).astype(int)
    sales_data_df['article_supergroup'] = sales_data_df.apply(lambda row: row['total_net'] if row['article_supergroup'] in article_group_values_for_one else 0, axis=1)
    
    sales_data_df['article_supergroup']=sales_data_df['article_supergroup'].astype(float)
    # Group the DataFrame by date and calculate total sales and count of transactions per day
    sales_data_df = sales_data_df.groupby('date').agg({'total_net': 'sum', 'article_supergroup': 'sum'}).reset_index()
    sales_data_df = sales_data_df.rename(columns={'total_net': 'total_sales'})
    sales_data_df = sales_data_df.dropna(subset=['total_sales'])
    sales_data_df['total_sales']=sales_data_df['total_sales'].astype(float)
    sales_data_df['percentage'] = 0
    sales_data_df.loc[sales_data_df['total_sales'] != 0, 'percentage'] = (sales_data_df['article_supergroup'] / sales_data_df['total_sales']) * 100 

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

    #print(city)
    # Create a dataframe with all dates from the start to the end
    all_dates_df = pd.DataFrame({
        'date': pd.date_range(start=start_date, end=weather_end_date)
    })



    #Add relevant new weather data columns
    #filtered_weather_data = []
    weather_data_df = pd.DataFrame(list(filtered_weather_data.values()))
    weather_data_df = weather_data_df.rename(columns={'time': 'date'})  # Rename 'time' column to 'date'

    sales_data_df['date'] = pd.to_datetime(sales_data_df['date'], format='%Y-%m-%d %H').dt.date

    #Only use sunshine in the relevant hour intervals based on feedback from the restaurant's manager'
    def get_relevant_hours(row):
        # Get the day of the week (0 is Monday, 6 is Sunday)
        day_of_week = row['date'].dayofweek
        hour = row['date'].hour

        # Define the hour ranges for each day
        ranges = {
            0: (15, 21),  # Monday
            1: (15, 21),  # Tuesday
            2: (15, 21),  # Wednesday
            3: (15, 21),  # Thursday
            4: (14, 23),  # Friday
            5: (12, 23),  # Saturday
            6: (14, 21)  # Sunday
        }

        start, end = ranges[day_of_week]

        # Return True if the current hour falls within the range for the current day
        return start <= hour < end

    #replace Nan with 0 for weather_data_df
    
    weather_data_df['sunshine_amount'].fillna(0, inplace=True)
    # Apply the function to create a new column indicating whether each row falls within the desired hours
    weather_data_df['relevant_hours'] = weather_data_df.apply(get_relevant_hours, axis=1)

    #print(weather_data_df[['date', 'sunshine_amount']])
    #sum sunshine_amount in weather_data_df if relevant_hours is true
    weather_data_df['sunshine_amount'] = weather_data_df['sunshine_amount'].where(weather_data_df['relevant_hours'] == True, 0)


    #if rain_sum=0 for the hours 17-23 and sum sunshine_amount between 15-18 < 120, set sunshine_amount = 60 for the hours 18-23
    weather_data_df.loc[(weather_data_df['date'].dt.hour == 18) & (weather_data_df['rain_sum'] == 0) & (weather_data_df['sunshine_amount'].between(15, 18) < 120), 'sunshine_amount'] = 60
    weather_data_df.loc[(weather_data_df['date'].dt.hour == 19) & (weather_data_df['rain_sum'] == 0) & (weather_data_df['sunshine_amount'].between(15, 18) < 120), 'sunshine_amount'] = 60
    weather_data_df.loc[(weather_data_df['date'].dt.hour == 20) & (weather_data_df['rain_sum'] == 0) & (weather_data_df['sunshine_amount'].between(15, 18) < 120), 'sunshine_amount'] = 60
    weather_data_df.loc[(weather_data_df['date'].dt.hour == 21) & (weather_data_df['rain_sum'] == 0) & (weather_data_df['sunshine_amount'].between(15, 18) < 120), 'sunshine_amount'] = 60
    weather_data_df.loc[(weather_data_df['date'].dt.hour == 22) & (weather_data_df['rain_sum'] == 0) & (weather_data_df['sunshine_amount'].between(15, 18) < 120), 'sunshine_amount'] = 60
    weather_data_df.loc[(weather_data_df['date'].dt.hour == 23) & (weather_data_df['rain_sum'] == 0) & (weather_data_df['sunshine_amount'].between(15, 18) < 120), 'sunshine_amount'] = 60

    weather_data_df['sunshine_amount'] = np.where(weather_data_df['date'].dt.month.isin(range(3, 10)),
                                                  weather_data_df['sunshine_amount'], 0)
    weather_data_df['sunshine_amount'].fillna(0, inplace=True)


    #make the date field in weather_data_df date only
    weather_data_df['date'] = weather_data_df['date'].dt.date
    # group weather_data_df by date and sum the total sunshine_amount
    # weather_data_df = weather_data_df.groupby('date')['sunshine_amount'].sum().reset_index()

    # Make sure 'date' column in all_dates_df is also of type 'date'
    all_dates_df['date'] = pd.to_datetime(all_dates_df['date']).dt.date

    # Merge all_dates_df with weather_data_df, fill missing values with 0
    weather_data_df = pd.merge(all_dates_df, weather_data_df, on='date', how='left')
    weather_data_df.fillna(0, inplace=True)


    #group sales data by date and sum the total_gross
    sales_data_df = sales_data_df.groupby('date')['percentage'].sum().reset_index()

    #take away dataframe head rows limit
    pd.set_option('display.max_rows', None)
    #print(weather_data_df[['date', 'sunshine_amount']])
    merged_data = weather_data_df.merge(sales_data_df, on='date', how='left')
    merged_data['percentage'].fillna(0, inplace=True)
    #merged_data = sales_data_df

    #fill missing dates with 0, as these are closed days
    full_date_range = pd.date_range(start=min(merged_data['date']), end=max(merged_data['date']))
    df_full = pd.DataFrame(full_date_range, columns=['date'])
    df_full['date'] = df_full['date'].astype('object')
    merged_data = pd.merge(merged_data, df_full, on='date', how='left')
    merged_data.loc[merged_data['percentage'].isnull(), 'percentage'] = 0
    #merged_data.loc[merged_data['total_gross'].isnull(), 'total_gross'] = 0

    pd.set_option('display.max_rows', None)

    # Split the data into two periods
    historical_data = merged_data[merged_data['date'] <= end_date]
    future_data = merged_data[merged_data['date'] > end_date]


    return merged_data, historical_data, future_data






