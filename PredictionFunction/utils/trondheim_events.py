import pandas as pd
import psycopg2
from PredictionFunction.utils.fetch_events import fetch_events

def trondheim_events():
    event_holidays=pd.DataFrame()
    locations = [
        "Bar Moskus","Lokal Bar","Tapperietpaadahls AS","Byscenen","Trondheim Spektrum",
        "Dokkhuset Scene","ISAK Kulturhus","EC Dahls Arena","Granåsen skisenter",
        "Granåsen","Granåsen Arena","Lerkendal stadion","Tapperiet Scene","Olavshallen, Store Sal",
        "Havet, Langhuset","Havet, Djupet","Havet, Heim, Trondheim"
    ]

    for venue in locations:
        venue_df = fetch_events("Trondheim", venue)
        event_holidays = pd.concat(objs=[event_holidays, venue_df], ignore_index=True)

    event_holidays['event_names'] = event_holidays['holiday'].fillna(event_holidays['name'])
    event_holidays['ds'] = pd.to_datetime(event_holidays['ds'])
    event_holidays['date'] = pd.to_datetime(event_holidays['date'])
    # event_holidays.to_csv("events_before.csv")
    event_holidays['event_date'] = event_holidays['date'].fillna(event_holidays['ds'].dt.date)
    event_holidays['event_date'] = event_holidays['event_date'].dt.strftime('%Y-%m-%d').astype(str)

    # event_holidays.to_csv("events_holidays.csv")
    return event_holidays