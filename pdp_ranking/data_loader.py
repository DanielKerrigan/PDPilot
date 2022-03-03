import pandas as pd


def load_bike_data():
    # Load the dataframe from the CSV file to the data
    dataframe = pd.read_csv("../data/bike-sharing-dataset/day.csv")
    # Separate into x and y
    features = ["holiday", "weekday", "workingday", "weathersit", "temp", "hum", "windspeed"]
    data_x = dataframe.loc[:, features]
    data_y = dataframe["cnt"]
    return data_x, data_y
