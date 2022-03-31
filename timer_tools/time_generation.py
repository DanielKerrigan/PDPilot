#!/usr/bin/env python
from functools import total_ordering
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import partial_dependence
from dataset_info import DATASETS
import pandas as pd
from typing import Tuple, List


# Keys for the datasets you want run in dataset_info.py
DATASETS_TO_RUN = [
    "home_data_train",
    "bike_sharing_day",
    "bike_sharing_hour"
]
# The step for number of features to test per run
FEATURES_STEP = 3
# The name for the file to export the generated times
EXPORT_CSV_FILE = "pdp_gen_times.csv"
# The percentage of the full dataset to use. I.e. .5 = 50%
PERCENTAGE_OF_ROWS = 1
# The columns to be saved to the CSV file
METRICS_COLUMNS = [
    "dataset",
    "num_rows",
    "features",
    "num_pdps_generated",
    "time_in_seconds",
    "pdp_method"
]


def load_data(
    data_path: str, features: List[str], target: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """ Load the data from the given path. """
    dataframe = pd.read_csv(data_path)
    dataframe = dataframe[features + [target]]
    # Cut down the dataframe by a percentage
    dataframe = dataframe.sample(frac=PERCENTAGE_OF_ROWS)
    dataframe.dropna(axis=0, inplace=True)
    
    data_x = dataframe[features]
    data_y = dataframe[target]

    data_x = data_x.reset_index()
    data_y = data_y.reset_index()

    return data_x, data_y


def run():
    to_save = pd.DataFrame(columns=METRICS_COLUMNS)
    for data_key in DATASETS_TO_RUN:
        print(f"Processing {data_key}")
        data_info = DATASETS[data_key]
        # Load the dataset
        data_x, data_y = load_data(
            data_path=data_info["data_path"],
            features=data_info["features"],
            target=data_info["target"]
        )

        # Create a dummy model
        model = RandomForestRegressor()
        model.fit(data_x, data_y)

        # Generate PDP's and time
        for num_features in range(1, len(data_info["features"])):
            if num_features % FEATURES_STEP == 0 or num_features == len(data_info["features"]):
                for grid_res in [20, 40, 60, 80, 100]:
                    print(f"Processing {num_features} features with grid resolution of {grid_res}.")
                    start_time = time.time()
                    pdps_generated = 0
                    for first_feature in range(num_features):
                        for second_feature in range(num_features):
                            pdps_generated += 1
                            if first_feature == second_feature:
                                partial_dependence(model, data_x, [tuple(first_feature)], kind='average', grid_resolution=grid_res)
                            else:
                                partial_dependence(model, data_x, [tuple(first_feature, second_feature)], kind='average', grid_resolution=grid_res)
                    total_time = time.time() - start_time
                    # TODO: Add sampling of dataset / percentage of dataset being used
                    new_row = {
                        "dataset": data_info["data_path"],
                        "num_rows": data_x.shape[0],
                        "features": num_features,
                        "grid_resolution": grid_res,
                        "num_pdps_generated": pdps_generated,
                        "time_in_seconds": total_time,
                        "pdp_method": "half_grid_resolution"
                    }
                    to_save = to_save.append(new_row, ignore_index=True)
    
    # Append the new data to the file
    previous_data = pd.read_csv(EXPORT_CSV_FILE)
    new_data = pd.concat([previous_data, to_save], ignore_index=True)
    new_data.to_csv(EXPORT_CSV_FILE)


if __name__ == "__main__":
    run()
