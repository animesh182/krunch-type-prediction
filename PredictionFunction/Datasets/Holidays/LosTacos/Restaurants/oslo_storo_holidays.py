import pandas as pd

christmas_day = pd.DataFrame(
        {
            "holiday": "christmas eve",
            "ds": pd.to_datetime(["2022-12-24"]),
            "lower_window": -5,
            "upper_window": 0,
        }
    )

# firstweek_jan = pd.DataFrame(
#         {
#             "holiday": "firstweek_jan",
#             "ds": pd.to_datetime(["2022-01-10", "2023-01-08", "2024-01-07"]),
#             "lower_window": -7,
#             "upper_window": 0,
#         }
#     )

# new_years_day = pd.DataFrame(
#         {
#             "holiday": "new_years_day",
#             "ds": pd.to_datetime(["2022-01-01", "2023-01-01"]),
#             "lower_window": 0,
#             "upper_window": 0,
#         }
#     )

# only when the holiday is on a weekday. If it is in the weekend there is no effect
# first_may = pd.DataFrame(
#         {
#             "holiday": "first_may",
#             "ds": pd.to_datetime(["2021-05-01", "2023-05-01"]),
#             "lower_window": -1,
#             "upper_window": 0,
#         }
#     )
seventeenth_may = pd.DataFrame(
        {
            "holiday": "seventeenth_may",
            "ds": pd.to_datetime(
                ["2021-05-17", "2022-05-17", "2023-05-17", "2024-05-17"]
            ),
            "lower_window": -1,
            "upper_window": 0,
        }
    )

easter = pd.DataFrame(
        {
            "holiday": "easter",
            "ds": pd.to_datetime(
                [
                    "2022-04-14",
                    "2022-04-15",
                    "2022-04-16",
                    "2022-04-17",
                    "2023-04-06",
                    "2023-04-07",
                    "2023-04-08",
                    "2023-04-09",
                ]
            ),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

easter_lowsaturday = pd.DataFrame(
        {
            "holiday": "easter_lowsaturday",
            "ds": pd.to_datetime(["2022-04-16"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

easter_mondaydayoff = pd.DataFrame(
        {
            "holiday": "easter_mondaydayoff",
            "ds": pd.to_datetime(["2022-04-18", "2023-04-10"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

# pinse = pd.DataFrame(
#         {
#             "holiday": "pinse",
#             "ds": pd.to_datetime(["2022-06-06", "2023-05-29"]),
#             "lower_window": -4,
#             "upper_window": 0,
#         }
#     )

# 2023: falls the day after the national independence day, so no effect the day before this year
# himmelfart = pd.DataFrame(
#         {
#             "holiday": "himmelfart",
#             "ds": pd.to_datetime(["2022-05-26"]),
#             "lower_window": -1,
#             "upper_window": 0,
#         }
#     )

fadderuke = pd.DataFrame(
        {
            "holiday": "himmelfart",
            "ds": pd.to_datetime(["2022-08-21", "2023-08-20"]),
            "lower_window": -8,
            "upper_window": 0,
        }
    )

day_before_red_day = pd.DataFrame(
        {
            "holiday": "day_before_red_day",
            "ds": pd.to_datetime(
                [
                    "2022-04-14",
                    "2022-05-16",
                    "2022-05-25",
                    "2022-12-24",
                    "2023-04-05",
                    "2023-05-16",
                ]
            ),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

closed_days = pd.DataFrame(
        {
            "holiday": "closed_days",
            "ds": pd.to_datetime(
                [
                    "2021-12-23",
                    "2021-12-24",
                    "2021-12-25",
                    "2021-12-26",
                    "2021-11-08",
                    "2021-12-31",
                    "2022-05-17",
                    "2022-12-24",
                    "2022-12-25",
                    "2022-12-26",
                    "2022-12-31",
                    "2023-04-06",
                    "2023-04-07",
                    "2023-04-09",
                    "2023-04-10",
                    "2023-05-17",
                ]
            ),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

karriere_dag = pd.DataFrame(
        {
            "holiday": "Karrieredag første dag",
            "ds": pd.to_datetime(["2022-09-27", "2023-09-12"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

# oslo_pride = pd.DataFrame(
#         {
#             "holiday": "oslo_pride",
#             "ds": pd.to_datetime(["2023-07-01"]),
#             "lower_window": -7,
#             "upper_window": 3,
#         }
#     )    