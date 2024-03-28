import psycopg2
import logging
import pandas as pd
from datetime import timedelta,datetime
# Define your database parameters here
from PredictionFunction.utils.params import params

def fetch_weather(city,start_date,end_date):
    # Define the query
    raw_query = """    select
                    *
                    from public."Weather"
                    WHERE
                        "city"=%s
                        AND time>=%s
                        AND time<=%s
                    group by 1;
                        """
    try:
        with psycopg2.connect(**params) as conn:
            # Use Pandas to directly read the SQL query into a DataFrame
            df = pd.read_sql_query(raw_query, conn, params=[city,start_date,end_date])
            return df
    except Exception as e:
        logging.error(f"Exception: {e}")
        return None
