#!/usr/bin/env python
import time
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import partial_dependence
import matplotlib.pyplot as plt
from dataset_info import DATASETS


MAX_FEATURES = 15
FEATURES_STEP = 3


def get_color(num_rows: int) -> str:
    """Returns the pyplot color to assign based on the number of rows"""
    color = 'k'
    if num_rows > 500:
        color = 'b'
    if num_rows > 1000:
        color = 'g'
    if num_rows > 5000:
        color = 'y'
    if num_rows > 10000:
        color = 'r'

    return color


def run():

    # For each of the datasets, load, test, and train a model, then generate pdp's for them
    for name, info in DATASETS.items():
        path = info["data_path"]
        total_features = info["features"]
        target = info["target"]

        x_values = []
        y_values = []
        for i in min(range(len(total_features)), MAX_FEATURES):
            if i % FEATURES_STEP == (FEATURES_STEP - 1) or i == len(total_features):
                for y in [1, 2]:
                    x_values.append(i)
                    features = total_features[:i]

                    # Read in and split the data
                    dataframe = pd.read_csv(path)
                    dataframe = dataframe[features + [target]]
                    dataframe.dropna(axis=0, inplace=True)

                    data_x = dataframe[features]
                    data_y = dataframe[target]

                    data_x = data_x.reset_index()
                    data_y = data_y.reset_index()

                    model = RandomForestRegressor()
                    model.fit(data_x, data_y)

                    # Time the creation of the PDP's
                    start_time = time.time()
                    for first_feature in range(len(features)):
                        for second_feature in range(len(features)):
                            if first_feature == second_feature:
                                partial_dependence(model, data_x, [first_feature], kind='average')
                            else:
                                partial_dependence(model, data_x, [(first_feature, second_feature)], kind='average')

                    end_time = time.time() - start_time
                    y_values.append(end_time)

        color = get_color(dataframe.shape[0])
        plt.plot(x_values, y_values, color, label=f"{dataframe.shape[0]} Rows")

    plt.xlabel("Number of Features")
    plt.ylabel("Seconds")
    plt.title("Time to generate PDP's")
    plt.legend(loc="upper right")
    plt.show()


# TODO: Figure out how to use categorical and numerical data with less data cleaning and preprocessing
"""
# Separate out the numerical and categorical columns for processing
numerical_columns_selector = selector(dtype_exclude=object)
categorical_columns_selector = selector(dtype_include=object)

numerical_columns = numerical_columns_selector(data_x)
categorical_columns = categorical_columns_selector(data_x)

categorical_preprocessor = OneHotEncoder(handle_unknown="ignore")
numerical_preprocessor = StandardScaler()

preprocessor = ColumnTransformer([
    ('one-hot-encoder', categorical_preprocessor, categorical_columns),
    ('standard_scaler', numerical_preprocessor, numerical_columns)]
)

model = make_pipeline(preprocessor, RandomForestRegressor())
"""


if __name__ == "__main__":
    run()
