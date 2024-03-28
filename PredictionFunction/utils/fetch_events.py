import psycopg2
import logging
import pandas as pd
from datetime import timedelta,datetime
# Define your database parameters here
from PredictionFunction.utils.params import params


def fetch_events(restaurant,location_name):
    # Define the query
    raw_query = """ SELECT e.name,e.event_size,e.start_date,e.end_date
                    FROM public."Events" e
                    JOIN public."Events_restaurants" er ON e.id = er.events_id
                    JOIN public."accounts_restaurant" ar ON er.restaurant_id = ar.id
                    JOIN public."Predictions_location" pl ON e.location_id = pl.id
                    WHERE ar.name = %s
                        AND pl.name = %s
                        """
    try:
        with psycopg2.connect(**params) as conn:
            # Use Pandas to directly read the SQL query into a DataFrame
            df = pd.read_sql_query(raw_query, conn, params=[restaurant,location_name])
            formatted_events = []
            
            for index, row in df.iterrows():
                start_date = row['start_date']
                end_date = row['end_date']
                
                if pd.notna(end_date):
                    current_date = start_date
                    while current_date <= end_date:
                        event_copy = row.copy()
                        event_copy['date'] = current_date
                        formatted_events.append(event_copy)
                        current_date += timedelta(days=1)
                else:
                    row['date'] = start_date
                    formatted_events.append(row)
            
            return pd.DataFrame(formatted_events)
    except Exception as e:
        logging.error(f"Exception: {e}")
        return None
