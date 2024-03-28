import pandas as pd

pre_christmas = pd.DataFrame(
        {
            "holiday": "Pre christmas period",
            "ds": pd.to_datetime(["2022-12-23"]),
            "lower_window": -5,
            "upper_window": 0,
        }
    )

pre_christmas_covid21 = pd.DataFrame(
        {
            "holiday": "Pre Christmas covid 21",
            "ds": pd.to_datetime(["2021-12-22"]),
            "lower_window": -6,
            "upper_window": 0,
        }
    )

weekendmiddec_21covid = pd.DataFrame(
        {
            "holiday": "weekendmiddec_21covid",
            "ds": pd.to_datetime(["2021-12-12"]),
            "lower_window": -2,
            "upper_window": 0,
        }
    )

new_year_romjul = pd.DataFrame(
        {
            "holiday": "New Year romjul",
            "ds": pd.to_datetime(["2022-12-31"]),
            "lower_window": -6,
            "upper_window": 0,
        }
    )

# firstweek_jan = pd.DataFrame(
#         {
#             "holiday": "First week of january",
#             "ds": pd.to_datetime(["2022-01-10", "2023-01-08", "2024-01-07"]),
#             "lower_window": -7,
#             "upper_window": 0,
#         }
#     )

# new_years_day = pd.DataFrame(
#         {
#             "holiday": "New years day",
#             "ds": pd.to_datetime(["2022-01-01", "2022-01-01", "2023-01-01"]),
#             "lower_window": 0,
#             "upper_window": 0,
#         }
#     )

fadder_week = pd.DataFrame(
        {
            "holiday": "Fadder week",
            "ds": pd.to_datetime(["2022-08-21", "2023-08-20"]),
            "lower_window": -7,
            "upper_window": 0,
        }
    )   

# only when the holiday is on a weekday. If it is in the weekend there is no effect
# first_may = pd.DataFrame(
#         {
#             "holiday": "First of may",
#             "ds": pd.to_datetime(["2021-05-01", "2023-05-01"]),
#             "lower_window": -1,
#             "upper_window": 0,
#         }
#     )
seventeenth_may = pd.DataFrame(
        {
            "holiday": "Seventeenth of may",
            "ds": pd.to_datetime(
                ["2021-05-17", "2022-05-17", "2023-05-17", "2024-05-17"]
            ),
            "lower_window": -1,
            "upper_window": 0,
        }
    )

easter = pd.DataFrame(
        {
            "holiday": "Easter break",
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

# pinse = pd.DataFrame(
#         {
#             "holiday": "Pinse",
#             "ds": pd.to_datetime(["2022-06-06", "2023-05-29"]),
#             "lower_window": -4,
#             "upper_window": 0,
#         }
#     )

# himmelfart = pd.DataFrame(
#         {
#             "holiday": "Himmelfart",
#             "ds": pd.to_datetime(["2022-05-26"]),
#             "lower_window": -1,
#             "upper_window": 0,
#         }
#     )

military_excercise = pd.DataFrame(
        {
            "holiday": "Military excercise",
            "ds": pd.to_datetime(
                ["2022-03-12", "2022-03-13", "2022-03-19", "2022-03-20"]
            ),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

helg_før_fellesferie = pd.DataFrame(
        {
            "holiday": "Weekends before fellesferie",
            "ds": pd.to_datetime(["2022-07-01", "2022-07-02", "2022-07-03"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )  

closed = pd.DataFrame(
        {
            "holiday": "Closed",
            "ds": pd.to_datetime(
                [
                    "2021-12-22",
                    "2021-12-23",
                    "2021-12-24",
                    "2021-12-25",
                    "2021-12-26",
                    "2021-12-31",
                    "2022-12-24",
                    "2022-12-25",
                    "2022-12-31",
                ]
            ),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

unknown_outliers = pd.DataFrame(
        {
            "holiday": "unknown_outliers",
            "ds": pd.to_datetime(["2021-09-06", "2022-11-07"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )    

covid_christmas21_startjan22 = pd.DataFrame(
        {
            "holiday": "covid_christmas21_startjan22",
            "ds": pd.to_datetime(
                [
                    "2021-12-27",
                    "2021-12-28",
                    "2021-12-29",
                    "2021-12-30",
                    "2021-12-31",
                    "2022-01-01",
                    "2022-01-02",
                    "2022-01-03",
                    "2022-01-04",
                    "2022-01-05",
                    "2022-01-06",
                    "2022-01-07",
                    "2022-01-08",
                    "2022-01-09",
                ]
            ),
            "lower_window": 0,
            "upper_window": 0,
        }
    )