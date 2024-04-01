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


async def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    start_date = "2021-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    prediction_category = "type"
    # prediction category is either hour, type, alcohol or day
    company = "Los Tacos"
    if mytimer.past_due:
        logging.info("The timer is past due!")

    for instance in data:
        restaurant = instance["Restaurant"]
        city = instance["City"]
        company = instance["Company"]
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
        save_to_db(forecast, company, restaurant, prediction_category)
