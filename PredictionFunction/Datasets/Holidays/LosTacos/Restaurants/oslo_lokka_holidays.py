import pandas as pd

christmas_day = pd.DataFrame(
        {
            "holiday": "christmas eve",
            "ds": pd.to_datetime(["2022-12-25", "2023-12-25"]),
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
            "ds": pd.to_datetime(["2022-04-16", "2023-04-08"]),
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

closed = pd.DataFrame(
        {
            "holiday": "closed",
            "ds": pd.to_datetime(
                [
                    "2021-12-23",
                    "2021-12-24",
                    "2021-12-25",
                    "2021-12-31",
                    "2022-12-24",
                    "2022-12-25",
                    "2022-12-31",
                    "2023-03-13",
                ]
            ),
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

black_friday = pd.DataFrame(
        {
            "holiday": "Black Friday",
            "ds": pd.to_datetime(["2022-11-25", "2023-11-24"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )    