from datetime import datetime, timezone
import logging
import azure.functions as func
import pandas as pd
from PredictionFunction.meta_tables import (
    data,
    location_specific_dictionary,
    weather_locations,
)
from PredictionFunction.PredictionTypes.take_out_data_prep import (
    type_predictor as prepare_takeout_data,
)
from PredictionFunction.predict import predict
from PredictionFunction.save_to_db import save_to_db
import psycopg2
from PredictionFunction.utils.params import params
from datetime import timedelta

from PredictionFunction.utils.create_temp_json import (
    select_minimum_restaurant,
    fetch_or_initialize_json,
    update_execution_count,
    save_json_file,
    group_run_count
)

async def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    start_date = "2021-09-01"
    # end_date = datetime.now().strftime("%Y-%m-%d")
    prediction_category = "type"
    # prediction category is either hour, type, alcohol or day
    execution_count_json = fetch_or_initialize_json()
    group_selected, candidates = select_minimum_restaurant(execution_count_json)
    logging.info(f"Selected group: {group_selected}")
    logging.info(f"Restaurants with minimum count:{candidates}")
    filtered_restaurants = [restaurant_info for restaurant_info in data if restaurant_info["Restaurant"] in candidates]
    if mytimer.past_due:
        logging.info("The timer is past due!")


    for restaurant_info in filtered_restaurants:
        restaurant = restaurant_info["Restaurant"]
        company = restaurant_info["Company"]
        try:
            with psycopg2.connect(**params) as conn:
                with conn.cursor() as cursor:
                    end_date_query = '''
                    SELECT MAX(gastronomic_day)
                    FROM public."SalesData"
                    WHERE restaurant = %s
                '''
                    cursor.execute(end_date_query,(restaurant,))
                    latest_gastronomic_day = cursor.fetchone()[0]
                    logging.info(latest_gastronomic_day)
                    if latest_gastronomic_day:
                        latest_date = latest_gastronomic_day - timedelta(days=1)
                        end_date= latest_date.strftime("%Y-%m-%d")
            conn.close()
            if restaurant == 'Oslo Torggata':
                start_date= "2022-05-12"
            elif restaurant == 'Oslo Steen_Strom':
                start_date= "2022-02-01"
            elif restaurant == 'Oslo Smestad':
                start_date= "2021-12-31"
            elif restaurant == 'Alexander Kielland':
                start_date= "2024-04-10"
            elif restaurant == 'Bjørvika':
                start_date= "2024-04-20"
            elif restaurant == "Trondheim":
                start_date = "2024-02-01"
            else:
                start_date = "2021-09-01"
            logging.info(f'start date for {restaurant} is {start_date}')
            logging.info(f'end date for {restaurant} is {end_date}')
            restaurant_func = location_specific_dictionary[restaurant]

            merged_data, historical_data, future_data = prepare_takeout_data(
                    company, restaurant, start_date, end_date
                )

            logging.info(f"Running predictions for {restaurant}")
            model, future_df, current_df = restaurant_func(
                prediction_category, restaurant, merged_data, historical_data, future_data
            )
            forecast = predict(
                model,
                future_df,
                current_df,
                company,
                restaurant,
                start_date,
                end_date,
                prediction_category,
            )
            # forecast.to_csv('befire.csv')
            save_to_db(forecast, company, restaurant, prediction_category)
            logging.info(f'predictions uploaded for {restaurant}  successfully')
            initial_json = update_execution_count(group_selected, restaurant, execution_count_json)
            save_json_file(initial_json)
        except Exception as e:
            logging.error(f"Error running predictions for {restaurant} of {company}: {e}")
    run_count_group = 'first_run_count' if group_selected == 'first' else 'second_run_count'
    initial_json = group_run_count(execution_count_json,run_count_group)
    save_json_file(initial_json)
    logging.info(f"All predictions and database updates completed for group {group_selected}")
