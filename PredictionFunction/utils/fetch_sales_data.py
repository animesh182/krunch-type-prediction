import psycopg2
import logging
import pandas as pd
from datetime import timedelta, datetime

# Define your database parameters here
from PredictionFunction.utils.params import params


def fetch_salesdata(company, restaurant, start_date, end_date):
    # Define the query
    raw_query = """    select
                    gastronomic_day as date,
                    take_out,
                    sum("total_net") as total_net
                    from public."SalesData"
                    WHERE
                        "company"=%s
                        AND "restaurant" = %s
                        AND gastronomic_day>=%s
                        AND gastronomic_day<=%s
                    group by 1,2;
                        """
    try:
        with psycopg2.connect(**params) as conn:
            # Use Pandas to directly read the SQL query into a DataFrame
            df = pd.read_sql_query(
                raw_query, conn, params=[company, restaurant, start_date, end_date]
            )
            return df
    except Exception as e:
        logging.error(f"Exception: {e}")
        return None
