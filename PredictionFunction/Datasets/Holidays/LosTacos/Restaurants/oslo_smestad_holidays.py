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
#             "ds": pd.to_datetime(
#                 [
#                     "2021-01-02",
#                     "2021-01-03",
#                     "2021-01-04",
#                     "2021-01-05",
#                     "2021-01-06",
#                     "2021-01-07",
#                     "2021-01-08",
#                     "2021-01-09",
#                     "2021-01-10",
#                     "2021-01-11",
#                     "2022-01-02",
#                     "2022-01-02",
#                     "2022-01-03",
#                     "2022-01-04",
#                     "2022-01-05",
#                     "2022-01-06",
#                     "2022-01-07",
#                     "2022-01-08",
#                     "2022-01-09",
#                     "2022-01-10",
#                     "2022-01-11",
#                     "2023-01-02",
#                     "2023-01-02",
#                     "2023-01-03",
#                     "2023-01-04",
#                     "2023-01-05",
#                     "2023-01-06",
#                     "2023-01-07",
#                     "2023-01-08",
#                     "2023-01-09",
#                     "2023-01-10",
#                     "2023-01-11",
#                 ]
#             ),
#             "lower_window": 0,
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

closed = pd.DataFrame(
        {
            "holiday": "closed",
            "ds": pd.to_datetime(["2022-12-24", "2022-12-25", "2022-12-31"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )
tons_of_rock = pd.DataFrame(
        {
            "holiday": "tons_of_rock",
            "ds": pd.to_datetime(["2023-06-24", "2022-06-25"]),
            "lower_window": -3,
            "upper_window": 1,
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