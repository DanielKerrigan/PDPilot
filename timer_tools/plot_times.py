#!/usr/bin/env python
from tokenize import group
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time_generation import METRICS_COLUMNS
import random


DATA_PATH = "/Users/rkalafos/pdp-ranking/timer_tools/pdp_gen_times.csv"

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

def get_random_color():
    r = random.randint(0, 100) / 100
    g = random.randint(0, 100) / 100
    b = random.randint(0, 100) / 100
    return (r, g, b)


def plot_num_features_vs_time(data: pd.DataFrame):
    """
    Plots the number of features on the x axis and the time on the y axis.
    Each line will represent a unique combo of dataset and number of rows used.
    """
    groups = data.groupby(["dataset", "num_rows"])
    for key, group_df in groups:
        group_df = group_df[(group_df["grid_resolution"] == 100.0)]
        x_values = np.array(group_df["features"])
        y_values = np.array(group_df["time_in_seconds"])
        color = get_color(key[1])
        plt.plot(x_values, y_values, color, label=f"{key[1]} Rows")

    plt.xlabel("Number of Features")
    plt.ylabel("Seconds")
    plt.title("Time to generate PDP's - Grid Resolution 100.0")
    plt.legend(loc="upper right")
    plt.savefig("time_plots/num_features_vs_time.png")


def plot_grid_resolution_vs_time(data: pd.DataFrame):
    """
    Plots the grid resolution on the x axis and the time on the y axis.
    Each line will represent a unique combo of dataset and number of rows used.
    """
    groups = data.groupby(["dataset", "num_rows"])
    for key, group_df in groups:
        group_df = group_df[group_df["features"] == 9]
        x_values = np.array(group_df["grid_resolution"])
        y_values = np.array(group_df["time_in_seconds"])
        color = get_color(key[1])
        plt.plot(x_values, y_values, color, label=f"{key[1]} Rows")

    plt.xlabel("Grid Resolution")
    plt.ylabel("Seconds")
    plt.title("Time to generate PDP's - 9 Features")
    plt.legend(loc="upper right")
    plt.savefig("time_plots/grid_resolution_vs_time_9_feat.png")

def plot_method_vs_time(data: pd.DataFrame):
    """
    Plots the dataset vs. the method used to generate pdp's
    """
    data = data[
        (data["grid_resolution"] == 100.0) &
        (data["dataset"] == "../data/bike-sharing-dataset/day.csv")
    ]
    groups = data.groupby(["dataset", "pdp_method"])
    for key, group_df in groups:
        x_values = np.array(group_df["features"])
        y_values = np.array(group_df["time_in_seconds"])
        color = get_random_color()
        plt.plot(x_values, y_values, color, label=f"Method: {key[1]}")
    
    plt.xlabel("Features")
    plt.ylabel("Seconds")
    plt.title("Time to generate PDP's - Bike Sharing (Day)")
    plt.legend(loc="upper right")
    plt.savefig("time_plots/method_vs_time.png")

def run():
    time_data = pd.read_csv(DATA_PATH)
    # plot_num_features_vs_time(time_data)
    # plot_grid_resolution_vs_time(time_data)
    plot_method_vs_time(time_data)


if __name__ == "__main__":
    run()