from datetime import datetime
import pandas as pd
import psycopg2
from PredictionFunction.utils.params import params


def add_opening_hours(df, restaurant_name,normal_hour,special_hour):
    # restaurant_id = Restaurant.objects.get(name=restaurant_name).id
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cursor:
            cursor.execute(""" select id from public."accounts_restaurant" where name=%s """,[restaurant_name])
            restaurant_id= cursor.fetchone()[0]

    def get_opening_duration(date):
        day_type = int(date.strftime("%w"))
        with conn.cursor() as cursor:
            cursor.execute(""" select * from public."accounts_openinghours" where restaurant_id=%s and start_date <= %s and end_date >= %s and day_of_week=%s """,
                           [restaurant_id,date,date,day_type])
            rows= cursor.fetchall()
            opening_hours = []
            for row in rows:
                hour = {
                    "start_hour": row[1],
                    "end_hour": row[2],
                    "start_date": row[3],
                    "end_date": row[4],
                    "day_of_week": row[7],
                }
                opening_hours.append(hour)
        if opening_hours:
            start = opening_hours[0]["start_hour"]
            end = opening_hours[0]["end_hour"]
            if start > end:
                duration = (24 - start) + end
            elif start==end:
                duration=0
            else:
                duration = end - start

            return duration
        else:
            return 0  # Assuming 0 hours for closed

    def scale_duration(duration, day_type):
        if duration == 0:
            return -1  # Closedx
        elif duration >= 24:
            return 1  # Open 24 hours
        elif duration == special_hour:
            return (duration / special_hour) - 1
        elif duration ==normal_hour:
            return (duration / normal_hour) - 1
        else:
            return 0

    df["opening_duration"] = df["ds"].apply(get_opening_duration)
    df["opening_duration"] = df.apply(
        lambda row: scale_duration(
            row["opening_duration"], int(row["ds"].strftime("%w"))
        ),
        axis=1,
    )
    return df