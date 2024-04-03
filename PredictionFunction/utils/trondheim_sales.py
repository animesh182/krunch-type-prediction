from datetime import date,timedelta
import pandas as pd
import decimal
import random
import numpy as np
from PredictionFunction.utils.constants import article_supergroup_values
import psycopg2
from PredictionFunction.utils.params import params
from PredictionFunction.utils.fetch_sales_data import fetch_salesdata
from io import BytesIO
import logging
from PredictionFunction.meta_tables import data

def sales_without_effect(company,start_date,end_date,alcohol_reference_restaurant,food_reference_restaurant):
    sales_forecast_stavanger = pd.read_csv("https://salespredictionstorage.blob.core.windows.net/csv/stavanger_forecast.csv")
    sales_forecast_karl_johan = pd.read_csv("https://salespredictionstorage.blob.core.windows.net/csv/karl_johan_forecast.csv")

    # actual_trondheim_start_date = SalesData.objects.filter(
    #     company=company, restaurant="Trondheim"
    # ).aggregate(min_day=Min("gastronomic_day"))["min_day"]

    actual_trondheim_start_date=date(2024,2,1)

    alcohol_query = '''
        SELECT *
        FROM public."SalesData" 
        WHERE company = %s 
            AND restaurant = %s 
            AND date >= %s 
            AND date <= %s 
            AND article_supergroup IN %s
    '''

    with psycopg2.connect(**params) as conn:
        alcohol_sales_data=pd.read_sql_query(alcohol_query,conn,params=[company,alcohol_reference_restaurant,start_date,actual_trondheim_start_date-timedelta(days=1),tuple(article_supergroup_values)])

    food_query = '''
        SELECT *
        FROM public."SalesData" 
        WHERE company = %s 
            AND restaurant = %s 
            AND date >= %s 
            AND date <= %s 
            AND article_supergroup not IN %s
    '''

    with psycopg2.connect(**params) as conn:
        food_sales_data= pd.read_sql_query(food_query,conn,params=[company,food_reference_restaurant,start_date,actual_trondheim_start_date-timedelta(days=1),tuple(article_supergroup_values)])


    trondheim_query = '''
        SELECT *
        FROM public."SalesData" 
        WHERE company = %s 
            AND restaurant = 'Trondheim' 
            AND date >= %s 
            AND date <= %s 
    '''

    with psycopg2.connect(**params) as conn:
        actual_trondheim_sales= pd.read_sql_query(trondheim_query,conn,params=[company,actual_trondheim_start_date,end_date])
    # alcohol_sales_data = SalesData.objects.filter(
    #     company=company,
    #     restaurant=alcohol_reference_restaurant,
    #     date__gte=start_date,
    #     date__lte=end_date,
    # ).filter(article_supergroup__in=article_supergroup_values)

    # food_sales_data = SalesData.objects.filter(
    #     company=company,
    #     restaurant=food_reference_restaurant,
    #     date__gte=start_date,
    #     date__lte=end_date,
    # ).exclude(article_supergroup__in=article_supergroup_values)

    # actual_trondheim = SalesData.objects.filter(
    #     company=company,
    #     restaurant="Trondheim",
    #     date__gte=actual_trondheim_start_date,
    #     date__lte=date(2024,2,29),
    # ).exclude(article_group="Catering")
    
    actual_trondheim_sales['gastronomic_day'] =pd.to_datetime(actual_trondheim_sales['gastronomic_day'])

    filtered_sales_reference = pd.concat([alcohol_sales_data,food_sales_data])

#get actual sales of food and alcohol in trondheim for a month---------------------------------------------------------------
    actual_sales_alcohol = actual_trondheim_sales[actual_trondheim_sales['article_supergroup'].isin(article_supergroup_values) & (actual_trondheim_sales['gastronomic_day'].dt.month == 2)]
    average_sales_new_alcohol = actual_sales_alcohol.groupby(['gastronomic_day','take_out'])['total_net'].sum().reset_index()
    actual_alcohol_sum = average_sales_new_alcohol['total_net'].sum()
    print(f'actual alcohol sales for trondheim in feb is {actual_alcohol_sum}')

    actual_sales_food = actual_trondheim_sales[~actual_trondheim_sales['article_supergroup'].isin(article_supergroup_values)& (actual_trondheim_sales['gastronomic_day'].dt.month == 2)]
    average_sales_new_food = actual_sales_food.groupby(['gastronomic_day','take_out'])['total_net'].sum().reset_index()
    actual_food_sum = average_sales_new_food['total_net'].sum()
    print(f'actual food sales for trondheim in feb is {actual_food_sum}')

#get sales of food and alcohol in reference restaurant for a month------------------------------------------------------
    reference_sales = filtered_sales_reference
    reference_alcohol_sales = reference_sales[reference_sales['article_supergroup'].isin(article_supergroup_values)]
    reference_alcohol_sales['gastronomic_day'] = pd.to_datetime(reference_alcohol_sales['gastronomic_day'])
    feb_alcohol_sales = reference_alcohol_sales[reference_alcohol_sales['gastronomic_day'].dt.month == 2]
    sums_per_feb_alcohol = feb_alcohol_sales.groupby(feb_alcohol_sales['gastronomic_day'].dt.year)['total_net'].sum()
    average_sum_feb_alcohol = sums_per_feb_alcohol.mean()
    print(f'actual alcohol sales for reference in feb is {average_sum_feb_alcohol}')


    reference_food_sales = reference_sales[~reference_sales['article_supergroup'].isin(article_supergroup_values)]
    reference_food_sales['gastronomic_day'] = pd.to_datetime(reference_food_sales['gastronomic_day'])
    feb_food_sales = reference_food_sales[reference_food_sales['gastronomic_day'].dt.month == 2]
    sums_per_feb_food = feb_food_sales.groupby(feb_food_sales['gastronomic_day'].dt.year)['total_net'].sum()
    average_sum_feb_food = sums_per_feb_food.mean()
    print(f'actual food sales for reference in feb is {average_sum_feb_food}')
#----------------------------------------------------------------------------------------------------------------------------
    scale_factor_for_food = float(actual_food_sum)/average_sum_feb_food
    scale_factor_for_alcohol = float(actual_alcohol_sum)/average_sum_feb_alcohol

    print(f'Scale factor for food is {scale_factor_for_food}')
    print(f'Scale factor for alcohol is {scale_factor_for_alcohol}')
    reference_alcohol_sales['total_net'] =reference_alcohol_sales['total_net'].astype(float) * float(scale_factor_for_alcohol)
    reference_food_sales['total_net'] = reference_food_sales['total_net'].astype(float) * float(scale_factor_for_food)

    final_scaled_scales = pd.concat([reference_alcohol_sales,reference_food_sales])
    final_sales_grouped = final_scaled_scales.groupby(['gastronomic_day','take_out'])['total_net'].sum().reset_index()


    daily_sales = actual_trondheim_sales.groupby(actual_trondheim_sales['gastronomic_day'].dt.date)['total_net'].sum().reset_index()
    daily_sales['gastronomic_day'] = pd.to_datetime(daily_sales['gastronomic_day'])

    # Calculate average sales for each day of the week
    average_sales_per_day = {}
    for day in range(7):
        day_sales = daily_sales[daily_sales['gastronomic_day'].dt.dayofweek == day]
        average_sales_per_day[day] = day_sales['total_net'].mean()

    # Calculate average sales for each month
    average_sales_per_month = {}
    for month in range(1, 13):
        month_sales = daily_sales[daily_sales['gastronomic_day'].dt.month == month]
        average_sales_per_month[month] = month_sales['total_net'].mean()

    # Calculate scales
    scales = {}
    for day in range(7):
        for month in range(1, 13):
            key = (day, month)
            scales[key] = average_sales_per_month[month] / average_sales_per_day[day] if average_sales_per_day[day] != 0 else 1

    # Apply scales to sales data
    final_sales_grouped['day_of_week'] = final_sales_grouped['gastronomic_day'].dt.dayofweek
    final_sales_grouped['month'] = final_sales_grouped['gastronomic_day'].dt.month
    final_sales_grouped['scaling_factor'] = final_sales_grouped.apply(lambda row: scales[(row['day_of_week'], row['month'])], axis=1)
    final_sales_grouped['scaled_total_net'] = final_sales_grouped['total_net'] * final_sales_grouped['scaling_factor']
#------------------------Get all the event Names for reference locations and their effects on the reference restaurant forecasts-------------------------------------------
    # events = Events.objects.filter(
    # location_id__cities_id__in=[
    #     '14bf2c63-7fbe-4480-8b22-4dc21d9f4195',
    #     '1b298f0c-4696-40ac-baa2-b1fa4784faff'
    # ],start_date__lt=date(2024,2,5)
    # ) 

    event_query =  '''SELECT e.*
                    FROM public."Events" e
                    JOIN public."Predictions_location" pl ON e.location_id = pl.id
                    JOIN public."accounts_city" ac ON pl.cities_id = ac.id
                    WHERE ac.id IN ('14bf2c63-7fbe-4480-8b22-4dc21d9f4195', '1b298f0c-4696-40ac-baa2-b1fa4784faff')
                    AND start_date < '2024-02-29';
                    '''
    with psycopg2.connect(**params) as conn:
        events_df=pd.read_sql_query(event_query,conn)
    events_df.columns = ['id', 'name', 'event_size', 'audience_type', 'is_sold_out', 'start_date', 'end_date', 'event_category_id', 'location_id']

    matching_events = []
    # Iterate over the event names in events_df
    for event_name in events_df['name']:
        # logging.info(event_name)
        if event_name in sales_forecast_stavanger.columns:
            event_column = sales_forecast_stavanger[event_name] 
            # Find the first non-zero effect value and its date
            non_zero_effect = event_column[event_column != 0].first_valid_index()
            # logging.info(f'{event_name}:{non_zero_effect}')
            if non_zero_effect is not None:
                effect_date = sales_forecast_stavanger.loc[non_zero_effect, 'ds']  # Assuming 'date' is a column in food_sales_forecast
                effect_value = event_column[non_zero_effect]
                # Append to our list
                matching_events.append({'event_name': event_name, 'gastronomic_day': effect_date, 'effect': effect_value})
        if event_name in sales_forecast_karl_johan.columns:
            event_column = sales_forecast_karl_johan[event_name] 
            # Find the first non-zero effect value and its date
            non_zero_effect = event_column[event_column != 0].first_valid_index()
            if non_zero_effect is not None:
                effect_date = sales_forecast_karl_johan.loc[non_zero_effect, 'ds']  # Assuming 'date' is a column in alcohol_sales_forecast
                effect_value = event_column[non_zero_effect]
                # Append to our list
                matching_events.append({'event_name': event_name, 'gastronomic_day': effect_date, 'effect': effect_value})
    matching_events_df = pd.DataFrame(matching_events)
    # matching_events_df.to_csv("matching_events.csv")
    matching_events_df.drop_duplicates(subset=['event_name','gastronomic_day','effect'])
    matching_events_grouped = matching_events_df.groupby('gastronomic_day')['effect'].sum().reset_index()
#---------------------Now decrease/increase the total_net depending on theeffect for the gastronomic_day to remove effect of reference restaurant's events---------------------
    final_sales_grouped['gastronomic_day']=pd.to_datetime(final_sales_grouped['gastronomic_day'])
    matching_events_grouped['gastronomic_day']=pd.to_datetime(matching_events_grouped['gastronomic_day'])
    merged_sales= pd.merge(final_sales_grouped, matching_events_grouped, on='gastronomic_day', how='outer')
    merged_sales['effect'].fillna(0,inplace=True)
    merged_sales['altered_effect']= merged_sales['total_net'].apply(decimal.Decimal)-merged_sales['effect'].apply(decimal.Decimal)
    merged_sales.rename(columns={"total_net":"old_total_net","altered_effect": "total_net"},inplace=True)
    actual_trondheim_sales_grouped = actual_trondheim_sales.groupby(['gastronomic_day','take_out'])['total_net'].sum().reset_index()
    final_merged = pd.concat([merged_sales,actual_trondheim_sales_grouped]).reset_index()
    final_merged.drop_duplicates('gastronomic_day',keep='last',inplace=True)
    final_merged.drop(columns=["day_of_week","month","scaling_factor","scaled_total_net","old_total_net","effect","index"], inplace=True)
    final_merged.fillna(0,inplace=True)
    filtered_sales = final_merged.copy()
    return filtered_sales,actual_trondheim_start_date