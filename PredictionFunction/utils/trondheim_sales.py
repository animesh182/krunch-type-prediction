from datetime import date, timedelta
import pandas as pd
import decimal
import random
import numpy as np
from PredictionFunction.utils.constants import article_supergroup_values
import psycopg2
from PredictionFunction.utils.params import params
from PredictionFunction.utils.fetch_sales_data import fetch_salesdata
from io import BytesIO
import logging
from PredictionFunction.meta_tables import data


def sales_without_effect(
    company,
    start_date,
    end_date,
    alcohol_reference_restaurant,
    food_reference_restaurant,
):

    reference_sales = pd.read_csv('https://salespredictionstorage.blob.core.windows.net/csv/reference_type_sales.csv')

    # actual_trondheim_start_date = SalesData.objects.filter(
    #     company=company, restaurant="Trondheim"
    # ).aggregate(min_day=Min("gastronomic_day"))["min_day"]

    actual_trondheim_start_date = date(2024, 2, 1)

    trondheim_query = """
        SELECT *
        FROM public."SalesData" 
        WHERE company = %s 
            AND restaurant = 'Trondheim' 
            AND date >= %s 
            AND date <= %s 
    """

    with psycopg2.connect(**params) as conn:
        actual_trondheim_sales = pd.read_sql_query(
            trondheim_query,
            conn,
            params=[company, actual_trondheim_start_date, end_date],
        )

    actual_trondheim_sales["gastronomic_day"] = pd.to_datetime(
        actual_trondheim_sales["gastronomic_day"]
    )

    # get actual sales of food and alcohol in trondheim for a month---------------------------------------------------------------
    actual_sales_alcohol = actual_trondheim_sales[
        actual_trondheim_sales["article_supergroup"].isin(article_supergroup_values)
        & (actual_trondheim_sales["gastronomic_day"].dt.month == 3)
    ]
    average_sales_new_alcohol = (
        actual_sales_alcohol.groupby(["gastronomic_day", "take_out"])["total_net"]
        .sum()
        .reset_index()
    )
    actual_alcohol_sum = average_sales_new_alcohol["total_net"].sum()
    logging.info(f"actual alcohol sales for trondheim in feb is {actual_alcohol_sum}")

    actual_sales_food = actual_trondheim_sales[
        ~actual_trondheim_sales["article_supergroup"].isin(article_supergroup_values)
        & (actual_trondheim_sales["gastronomic_day"].dt.month == 3)
    ]
    average_sales_new_food = (
        actual_sales_food.groupby(["gastronomic_day", "take_out"])["total_net"]
        .sum()
        .reset_index()
    )
    actual_food_sum = average_sales_new_food["total_net"].sum()
    logging.info(f"actual food sales for trondheim in feb is {actual_food_sum}")
    # ----------------------------------------------------------------------------------------------------------------------------

    daily_sales = (
        actual_trondheim_sales.groupby(
            actual_trondheim_sales["gastronomic_day"].dt.date
        )["total_net"]
        .sum()
        .reset_index()
    )
    daily_sales["gastronomic_day"] = pd.to_datetime(daily_sales["gastronomic_day"])

    actual_trondheim_sales_grouped = (
        actual_trondheim_sales.groupby(["gastronomic_day", "take_out"])["total_net"]
        .sum()
        .reset_index()
    )
    final_merged = pd.concat(
        [reference_sales, actual_trondheim_sales_grouped]
    ).reset_index()
    # final_merged.drop_duplicates('gastronomic_day',keep='last',inplace=True)
    final_merged.drop(
        columns=[
            "day_of_week",
            "month",
            "scaling_factor",
            "scaled_total_net",
            "old_total_net",
            "effect",
            "index",
        ],
        inplace=True,
    )
    final_merged.fillna(0, inplace=True)
    filtered_sales = final_merged.copy()
    return filtered_sales, actual_trondheim_start_date
