import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.express as px
import re
import pandas as pd
import pytz
from datetime import datetime as dt
from datetime import datetime, timedelta
import xlrd
import glob


def weekly_seasonalities(df):
    print("running weekly seasonalities function")
    merged_data = df.copy()

    # Make sure 'date' is in datetime format
    merged_data["ds"] = pd.to_datetime(merged_data["ds"])
    # Set 'date' as the index
    merged_data.set_index("ds", inplace=True)

    # Extract ISO week and year numbers
    merged_data["week_number"] = merged_data.index.isocalendar().week
    merged_data["year_number"] = merged_data.index.isocalendar().year

    # Create a DataFrame to store the average pattern for each week
    average_weekly_patterns = []

    for week_number in range(1, 54):  # ISO week numbers go from 1 to 53
        weekly_data = merged_data[merged_data["week_number"] == week_number]

        # Get the average for each day of the week across all years
        daily_averages = (
            weekly_data.groupby(weekly_data.index.weekday)["y"].mean().values
        )

        # If there are 7 days, add to the list
        if len(daily_averages) == 7:
            average_weekly_patterns.append(daily_averages)

    # Convert the weekly patterns into a numpy array
    weekly_patterns_array = np.array(average_weekly_patterns)

    from sklearn.cluster import KMeans

    # Choose the number of clusters
    n_clusters = 7

    # Perform k-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(weekly_patterns_array)

    # Get the cluster labels for each period
    cluster_labels = kmeans.labels_

    # Initialize an empty dictionary to store week numbers for each cluster
    cluster_weeks = {i: [] for i in range(n_clusters)}

    # Iterate through the cluster labels and corresponding week numbers
    for label, week_number in zip(cluster_labels, range(1, 54)):
        if week_number in merged_data["week_number"].values:
            cluster_weeks[label].append(week_number)

    import matplotlib.pyplot as plt

    # Plot the clusters
    for i in range(n_clusters):
        plt.figure(figsize=(12, 6))
        plt.title(f"Cluster {i}")
        for week in weekly_patterns_array[cluster_labels == i]:
            plt.plot(week, marker="o")
        plt.xlabel("Day of the Week")
        plt.ylabel("Sales")
        plt.xticks(
            ticks=range(7),
            labels=[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
        )

        # Add the week numbers as an annotation below the plot
        cluster_weeks_str = ", ".join(map(str, cluster_weeks[i]))
        plt.annotate(
            f"Weeks:\n{cluster_weeks_str}",
            xy=(0, 0),
            xycoords="axes fraction",
            fontsize=9,
            ha="left",
            va="top",
            xytext=(5, -5),
            textcoords="offset points",
        )

    # Uncomment this for analysis, but comment out when running regular predictions
    # plt.show()

    return cluster_weeks