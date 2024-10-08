import pandas as pd
import numpy as np
import datetime
import logging


def predict(
    m, future, df, company, restaurant, start_date, end_date, prediction_category
):
    if future.empty:
        raise ValueError("The future DataFrame is empty.")

    ######### make forecast and plots

    # This must be changed to the correct opening hours, which varies for days and restaurants. Create dictionary for that and use here
    # future.to_csv('future.csv') 
    future['ds'] = pd.to_datetime(future['ds'])
    future= future.fillna(0)
    forecast = m.predict(future)
    # Set negative sales to 0 (this might happen sometimes for closed days)
    forecast["yhat"] = np.where(forecast["yhat"] < 0, 0, forecast["yhat"])

    # create a pandas dataframe of the forecasst
    forecast["ds"] = pd.to_datetime(forecast["ds"])
    logging.info(len(future))
    # Filter out predictions for dates before today
    today = pd.to_datetime(datetime.datetime.now().date())
    forecast_df = forecast[forecast["ds"] > today]
    # Optionally, adjust the forecast based on other factors (like tourist data, if applicable)

    # Return the DataFrame with future dates and corresponding predictions
    return forecast_df[["ds", "yhat"]]
