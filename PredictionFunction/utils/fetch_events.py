import psycopg2
import logging
import pandas as pd
from datetime import timedelta,datetime
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
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cursor:
            cursor.execute(raw_query,[restaurant,location_name])
            rows = cursor.fetchall()
            events_dict = []
            for row in rows:
                event_dict = {
                    "name": row[0],
                    "event_size": row[1],
                    "start_date": row[2],
                    "end_date": row[3]
                }
                events_dict.append(event_dict)

    formatted_events = []
    formatted_holidays =[]
    threshold=20
    for events in events_dict:
        # If 'end_date' is present, calculate the number of days between 'start_date' and 'end_date' and repeat the event for all the days
        start_date = events.get("start_date")
        end_date = events.get("end_date")
        if len(events_dict) >= threshold:
            if end_date:
                current_date = start_date
                while current_date <= end_date:
                    event_copy = events.copy()
                    event_copy["date"] = current_date
                    formatted_events.append(event_copy)
                    current_date += timedelta(days=1)
            else:
                events["date"] = start_date
                formatted_events.append(events)
        else:
            if end_date and start_date and end_date>start_date and end_date-start_date > timedelta(days=threshold):
                current_date = start_date
                while current_date <= end_date:
                    event_copy = events.copy()
                    event_copy["date"] = current_date
                    formatted_events.append(event_copy)
                    current_date += timedelta(days=1)

            elif end_date and start_date and end_date>start_date and end_date-start_date< timedelta(days=threshold):
                formatted_holidays.append(
                    {
                        "holiday": events.get("name"),
                        "ds": pd.to_datetime(end_date),
                        "lower_window": -(end_date - start_date).days,
                        "upper_window": 0,
                    }
                )
            else:
                formatted_holidays.append(
                    {
                        "holiday": events.get("name"),
                        "ds": end_date if end_date else start_date,
                        "upper_window": 0,
                        "lower_window": 0,
                    }
                )
    # pd.DataFrame(formatted_events).to_csv("Events.csv")
    return pd.DataFrame(formatted_events) if len(events_dict) >= threshold or any(((event["end_date"] - event["start_date"]).days if event.get("end_date") and event.get("start_date") else 0) >= threshold for event in events_dict) else pd.DataFrame(formatted_holidays)
