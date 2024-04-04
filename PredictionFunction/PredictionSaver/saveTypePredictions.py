import psycopg2
import logging
import pandas as pd
import uuid
from datetime import timedelta, datetime

# Define your database parameters here
from PredictionFunction.utils.params import params
import psycopg2.extras


def save_type_predictions(data, restaurant):
    raw_query = """ INSERT INTO public."Predictions_typeprediction"(
	date, take_out,company , restaurant, id, created_at)
	VALUES %s"""
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                # Transform your DataFrame to a list of tuples, including the id column
                tuples = [tuple(x) for x in data.to_records(index=False)]
                # Use execute_values to insert the data
                psycopg2.extras.execute_values(
                    cur, raw_query, tuples, template=None, page_size=100
                )
                conn.commit()
        logging.info(f"Successfully uploaded predictions for {restaurant}")
        return
    except Exception as e:
        logging.error(f"Exception: {e}")
        return None
