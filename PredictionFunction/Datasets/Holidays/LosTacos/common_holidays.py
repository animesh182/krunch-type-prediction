# Drammen is not used for comparison
import pandas as pd

# ------Event--------
first_may = pd.DataFrame(
        {
            "holiday": "First of may",
            "ds": pd.to_datetime(["2021-05-01", "2023-05-01"]),
            "lower_window": -1,
            "upper_window": 0,
        }
    )

# NO 17th may in oslo_city
# seventeenth_may = pd.DataFrame(
#         {
#             "holiday": "Seventeenth of may",
#             "ds": pd.to_datetime(
#                 ["2021-05-17", "2022-05-17", "2023-05-17", "2024-05-17"]
#             ),
#             "lower_window": -1,
#             "upper_window": 0,
#         }
#     )

# ------Holidays--------
# firstweek_jan = pd.DataFrame(
#         {
#             "holiday": "firstweek_jan",
#             "ds": pd.to_datetime(["2022-01-10", "2023-01-08", "2024-01-07"]),
#             "lower_window": -7,
#             "upper_window": 0,
#         }
#     )

''' 
Fredrikstad, Smestad, and Torggata have the most dates for firstweek_jan
'''

firstweek_jan = pd.DataFrame(
        {
            "holiday": "firstweek_jan",
            "ds": pd.to_datetime(
                [
                    "2021-01-02",
                    "2021-01-02",
                    "2021-01-03",
                    "2021-01-04",
                    "2021-01-05",
                    "2021-01-06",
                    "2021-01-07",
                    "2021-01-08",
                    "2021-01-09",
                    "2021-01-10",
                    "2021-01-11",
                    "2022-01-02",
                    "2022-01-02",
                    "2022-01-03",
                    "2022-01-04",
                    "2022-01-05",
                    "2022-01-06",
                    "2022-01-07",
                    "2022-01-08",
                    "2022-01-09",
                    "2022-01-10",
                    "2022-01-11",
                    "2023-01-02",
                    "2023-01-02",
                    "2023-01-03",
                    "2023-01-04",
                    "2023-01-05",
                    "2023-01-06",
                    "2023-01-07",
                    "2023-01-08",
                    "2023-01-09",
                    "2023-01-10",
                    "2023-01-11",
                ]
            ),
            "lower_window": 0,
            "upper_window": 0,
        }
    )
first_weekend_christmas_school_vacation = pd.DataFrame(
        {
            "holiday": "First weekend of christmas school break",
            "ds": pd.to_datetime(["2022-12-18", "2023-12-17", "2021-12-19"]),
            "lower_window": -2,
            "upper_window": 0,
        }
    )

new_years_day = pd.DataFrame(
        {
            "holiday": "new_years_day",
            "ds": pd.to_datetime(["2022-01-01", "2023-01-01"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

pinse = pd.DataFrame(
        {
            "holiday": "Pinse",
            "ds": pd.to_datetime(["2022-06-06", "2023-05-29"]),
            "lower_window": -4,
            "upper_window": 0,
        }
    )

himmelfart = pd.DataFrame(
        {
            "holiday": "Himmelfart",
            "ds": pd.to_datetime(["2022-05-26"]),
            "lower_window": -1,
            "upper_window": 0,
        }
    )
halloween_weekend = pd.DataFrame(
        {
            "holiday": "Halloween weekend",
            "ds": pd.to_datetime(["2023-10-28", "2022-10-29", "2021-10-30"]),
            "lower_window": -1,
            "upper_window": 0,
        }
    )
halloween_day = pd.DataFrame(
    {
        "holiday": "Halloween Day",
        "ds": pd.to_datetime(["2024-10-31", "2023-10-31", "2022-10-31", "2021-10-31"]),
        "lower_window": -1,
        "upper_window": 0,
    }
)
hostferie_sor_ostlandet_weekdays = pd.DataFrame(
    {
        "holiday": "Høstferie weekdays",
        "ds": pd.to_datetime(["2023-10-05", "2022-10-06", "2021-10-07"]),
        "lower_window": -1,
        "upper_window": 0,
    }
) 
hostferie_sor_ostlandet_weekdend = pd.DataFrame(
    {
        "holiday": "Høstferie weekend",
        "ds": pd.to_datetime(["2023-10-07", "2022-10-08", "2021-10-09"]),
        "lower_window": -1,
        "upper_window": 0,
    }
) 
hostferie_vestlandet_weekdays = pd.DataFrame(
    {
        "holiday": "Høstferie weekdays",
        "ds": pd.to_datetime(["2023-10-12", "2022-10-13", "2021-10-14"]),
        "lower_window": -3,
        "upper_window": 0,
    }
) 
hostferie_vestlandet_weekdend = pd.DataFrame(
    {
        "holiday": "Høstferie weekend",
        "ds": pd.to_datetime(["2023-10-14", "2022-10-15", "2021-10-16"]),
        "lower_window": -1,
        "upper_window": 0,
    }
) 
vinterferie_vestlandet_weekend_before = pd.DataFrame(
    {
        "holiday": "Helgen før vinterferie",
        "ds": pd.to_datetime(["2022-02-26", "2023-02-25", "2024-02-24"]),
        "lower_window": -1,
        "upper_window": 0,
    }
) 
vinterferie_vestlandet_weekend = pd.DataFrame(
    {
        "holiday": "Helgen i vinterferien",
        "ds": pd.to_datetime(["2022-03-05", "2023-03-04", "2024-03-02"]),
        "lower_window": -1,
        "upper_window": 0,
    }
) 
vinterferie_ostlandet_saturday_before = pd.DataFrame(
    {
        "holiday": "Lørdagen før vinterferien",
        "ds": pd.to_datetime(["2022-02-19", "2023-02-18", "2024-02-17"]),
        "lower_window": 0,
        "upper_window": 0,
    }
) 
vinterferie_ostlandet_saturday = pd.DataFrame(
    {
        "holiday": "Lørdagen i vinterferien",
        "ds": pd.to_datetime(["2022-02-26", "2023-02-25", "2024-02-24"]),
        "lower_window": 0,
        "upper_window": 0,
    }
) 