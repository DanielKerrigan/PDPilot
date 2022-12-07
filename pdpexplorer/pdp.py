#!/usr/bin/env python
# coding: utf-8

"""
Compute partial dependence plots
"""

import json
import math
from operator import itemgetter
from pathlib import Path
from typing import Callable, Union

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.stats import iqr as inner_quartile_range
from sklearn.cluster import KMeans
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, silhouette_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm
from tslearn.clustering import TimeSeriesKMeans
from tslearn.clustering import silhouette_score as ts_silhouette_score
from tslearn.utils import to_time_series_dataset

from pdpexplorer.metadata import Metadata
from pdpexplorer.tqdm_joblib import tqdm_joblib


def partial_dependence(
    *,
    predict: Callable[[pd.DataFrame], list[float]],
    df: pd.DataFrame,
    features: list[str],
    resolution: int = 20,
    one_hot_features: Union[dict[str, list[tuple[str, str]]], None] = None,
    nominal_features: Union[list[str], None] = None,
    ordinal_features: Union[list[str], None] = None,
    feature_value_mappings: Union[dict[str, dict[str, str]], None] = None,
    n_jobs: int = 1,
    output_path: str | None = None,
) -> dict | None:
    """Calculates the data needed for the widget. This includes computing the
    data for the partial dependence plots and ICE plots, calculating the metrics
    to rank the plots by, clustering the PDPs, and clustering the lines within
    each ICE plot.

    :param predict: A function whose input is a DataFrame of instances and
        returns the model's predictions on those instances.
    :type predict: Callable[[pd.DataFrame], list[float]]
    :param df: Instances to use to compute the PDPs and ICE plots.
    :type df: pd.DataFrame
    :param features: List of feature names to compute the plots for.
    :type features: list[str]
    :param resolution: For quantitative features, the number of evenly
        spaced to use to compute the plots, defaults to 20.
    :type resolution: int, optional
    :param one_hot_features: A dictionary that maps from the name of a feature
        to a list tuples containg the corresponding one-hot encoded column
        names and feature values, defaults to None.
    :type one_hot_features: dict[str, list[tuple[str, str]]] | None, optional
    :param nominal_features: List of nominal and binary features in the
        dataset that are not one-hot encoded. If None, defaults to binary
        features in the dataset.
    :type nominal_features: list[str] | None, optional
    :param ordinal_features: List of ordinal features in the dataset.
        If None, defaults to integer features with 3-12 unique values.
    :type ordinal_features: list[str] | None, optional
    :param feature_value_mappings: Nested dictionary that maps from the name
        of a nominal or ordinal feature, to a value for that feature in
        the dataset, to the desired label for that value in the UI,
        defaults to None.
    :type feature_value_mappings: dict[str, dict[str, str]] | None, optional
    :param n_jobs: Number of jobs to use to parallelize computation,
        defaults to 1.
    :type n_jobs: int, optional
    :param output_path: A file path to write the results to.
        If None, then the results are instead returned.
    :type output_path: str | None, optional
    :raises OSError: Raised when the ``output_path``, if provided, cannot be written to.
    :return: Wigdet data, or None if an ``output_path`` is provided.
    :rtype: dict | None
    """

    # first check that the output path exists if provided so that the function
    # can fail quickly, rather than waiting until all the work is done
    if output_path:
        path = Path(output_path).resolve()

        if not path.parent.is_dir():
            raise OSError(f"Cannot write to {path.parent}")

    md = Metadata(
        df,
        resolution,
        one_hot_features,
        nominal_features,
        ordinal_features,
        feature_value_mappings,
    )

    subset = df.copy()
    subset_copy = df.copy()

    iqr = inner_quartile_range(predict(df))

    # one-way

    one_way_work = [
        {
            "predict": predict,
            "data": subset,
            "data_copy": subset_copy,
            "feature": feature,
            "md": md,
            "iqr": iqr,
            "feature_to_pd": None,
        }
        for feature in features
    ]

    num_one_way = len(features)
    print(f"Calculating {num_one_way} one-way PDPs")

    if n_jobs == 1:
        one_way_results = [_calc_pd(**args) for args in tqdm(one_way_work, ncols=80)]
    else:
        with tqdm_joblib(tqdm(total=num_one_way, unit="PDP", ncols=80)) as _:
            one_way_results = Parallel(n_jobs=n_jobs)(
                delayed(_calc_pd)(**args) for args in one_way_work
            )

    one_way_pds = [x[0] for x in one_way_results]
    feature_pairs = {pair for x in one_way_results for pair in x[1]}

    feature_to_pd = _get_feature_to_pd(one_way_pds) if one_way_pds else None

    print("Clustering one-way PDPs")
    one_way_quantitative_clusters, one_way_categorical_clusters = _one_way_clustering(
        one_way_pds=one_way_pds, feature_to_pd=feature_to_pd, md=md, n_jobs=n_jobs
    )

    # two-way

    two_way_work = [
        {
            "predict": predict,
            "data": subset,
            "data_copy": subset_copy,
            "feature": pair,
            "md": md,
            "iqr": iqr,
            "feature_to_pd": feature_to_pd,
        }
        for pair in feature_pairs
    ]
    num_two_way = len(feature_pairs)
    print(f"Calculating {num_two_way} two-way PDPs")

    if n_jobs == 1:
        two_way_pds = [_calc_pd(**args) for args in tqdm(two_way_work, ncols=80)]
    else:
        with tqdm_joblib(tqdm(total=num_two_way, unit="PDP", ncols=80)) as _:
            two_way_pds = Parallel(n_jobs=n_jobs)(
                delayed(_calc_pd)(**args) for args in two_way_work
            )

    # min and max predictions

    ice_min = min(one_way_pds, key=lambda d: d["ice"]["centered_ice_min"])["ice"][
        "centered_ice_min"
    ]
    ice_max = max(one_way_pds, key=lambda d: d["ice"]["centered_ice_max"])["ice"][
        "centered_ice_max"
    ]

    cluster_min = min(one_way_pds, key=lambda d: d["ice"]["centered_mean_min"])["ice"][
        "centered_mean_min"
    ]
    cluster_max = max(one_way_pds, key=lambda d: d["ice"]["centered_mean_max"])["ice"][
        "centered_mean_max"
    ]

    p10_min = min(one_way_pds, key=lambda d: d["ice"]["p10_min"])["ice"]["p10_min"]
    p90_max = max(one_way_pds, key=lambda d: d["ice"]["p90_max"])["ice"]["p90_max"]

    pdp_min = min(one_way_pds, key=itemgetter("pdp_min"))["pdp_min"]
    pdp_max = max(one_way_pds, key=itemgetter("pdp_max"))["pdp_max"]

    if two_way_pds:
        pdp_min = min(
            pdp_min,
            min(two_way_pds, key=itemgetter("pdp_min"))["pdp_min"],
        )
        pdp_max = max(
            pdp_max,
            max(two_way_pds, key=itemgetter("pdp_max"))["pdp_max"],
        )

    # output

    results = {
        "one_way_pds": one_way_pds,
        "two_way_pds": two_way_pds,
        "one_way_quantitative_clusters": one_way_quantitative_clusters,
        "one_way_categorical_clusters": one_way_categorical_clusters,
        "pdp_extent": [pdp_min, pdp_max],
        "ice_mean_extent": [cluster_min, cluster_max],
        "ice_band_extent": [p10_min, p90_max],
        "ice_line_extent": [ice_min, ice_max],
        "num_instances": md.size,
        "dataset": subset.to_dict(orient="list"),
        "feature_info": md.feature_info,
    }

    if output_path:
        path.write_text(json.dumps(results), encoding="utf-8")
    else:
        return results


def _calc_pd(
    predict,
    data,
    data_copy,
    feature,
    md,
    iqr,
    feature_to_pd,
):
    if isinstance(feature, tuple) or isinstance(feature, list):
        return _calc_two_way_pd(
            predict,
            data,
            data_copy,
            feature,
            md,
            feature_to_pd,
        )
    else:
        return _calc_one_way_pd(
            predict,
            data,
            data_copy,
            feature,
            md,
            iqr,
        )


def _calc_one_way_pd(
    predict,
    data,
    data_copy,
    feature,
    md,
    iqr,
):
    feat_info = md.feature_info[feature]

    ice_lines = []

    for value in feat_info["values"]:
        _set_feature(feature, value, data, feat_info)
        predictions = predict(data)
        ice_lines.append(predictions.tolist())

    _reset_feature(feature, data, data_copy, feat_info)

    ice_lines = np.array(ice_lines).T
    mean_predictions = np.mean(ice_lines, axis=0)

    mean_predictions_centered = (mean_predictions - mean_predictions.mean()).tolist()

    pdp_min = mean_predictions.min().item()
    pdp_max = mean_predictions.max().item()

    mean_predictions = mean_predictions.tolist()

    ice, pairs = _calculate_ice(ice_lines=ice_lines, data=data, feature=feature, md=md)

    par_dep = {
        "num_features": 1,
        "id": feature,
        "ordered": feat_info["ordered"],
        "x_feature": feature,
        "x_values": feat_info["values"],
        "mean_predictions": mean_predictions,
        "mean_predictions_centered": mean_predictions_centered,
        "pdp_min": pdp_min,
        "pdp_max": pdp_max,
        "ice": ice,
    }

    if feat_info["ordered"]:
        # This code is adapted from
        # https://scikit-learn.org/stable/auto_examples/linear_model/plot_polynomial_interpolation.html
        # Author: Mathieu Blondel
        #         Jake Vanderplas
        #         Christian Lorentzen
        #         Malte Londschien
        # License: BSD 3 clause

        # good-fit

        X = np.array(feat_info["values"]).reshape((-1, 1))
        y = np.array(mean_predictions)

        for i in range(2, 10):
            trend_model = make_pipeline(
                StandardScaler(), SplineTransformer(i, 3), Ridge(alpha=0.1)
            )

            trend_model.fit(X, y)
            trend = trend_model.predict(X)

            rmse = mean_squared_error(y, trend, squared=False)
            # normalize it
            nrmse = rmse / iqr

            if nrmse < 0.02 or i == 9:
                par_dep["trend_good_fit"] = trend.tolist()
                par_dep["nrmse_good_fit"] = nrmse.item()
                par_dep["knots_good_fit"] = i
                break

    par_dep["deviation"] = np.std(mean_predictions)

    return par_dep, pairs


def _calc_two_way_pd(
    predict,
    data,
    data_copy,
    pair,
    md,
    feature_to_pd,
):
    x_feature, y_feature = pair

    x_feat_info = md.feature_info[x_feature]
    y_feat_info = md.feature_info[y_feature]

    # when one feature is quantitative and the other is categorical,
    # make the y feature be categorical

    if y_feat_info["kind"] == "quantitative" and x_feat_info["kind"] != "quantitative":
        x_feature, y_feature = y_feature, x_feature
        x_feat_info, y_feat_info = y_feat_info, x_feat_info

    x_axis = x_feat_info["values"]
    y_axis = y_feat_info["values"]

    x_values = []
    y_values = []
    rows = []
    cols = []
    mean_predictions = []

    x_pdp = feature_to_pd[x_feature]
    y_pdp = feature_to_pd[y_feature]
    no_interactions = []

    pdp_min = math.inf
    pdp_max = -math.inf

    for c, x_value in enumerate(x_axis):
        _set_feature(x_feature, x_value, data, x_feat_info)

        for r, y_value in enumerate(y_axis):
            _set_feature(y_feature, y_value, data, y_feat_info)

            predictions = predict(data)
            mean_pred = np.mean(predictions).item()

            mean_predictions.append(mean_pred)

            x_values.append(x_value)
            y_values.append(y_value)
            rows.append(r)
            cols.append(c)

            no_interactions.append(
                x_pdp["mean_predictions_centered"][c]
                + y_pdp["mean_predictions_centered"][r]
            )

            if mean_pred < pdp_min:
                pdp_min = mean_pred

            if mean_pred > pdp_max:
                pdp_max = mean_pred

            _reset_feature(y_feature, data, data_copy, y_feat_info)

        _reset_feature(x_feature, data, data_copy, x_feat_info)

    mean_predictions_centered = np.array(mean_predictions) - np.mean(mean_predictions)
    interactions = (mean_predictions_centered - np.array(no_interactions)).tolist()
    mean_predictions_centered = mean_predictions_centered.tolist()

    h_statistic = np.sqrt(np.square(interactions).sum()).item()

    par_dep = {
        "num_features": 2,
        "id": x_feature + "_" + y_feature,
        "x_feature": x_feature,
        "x_values": x_values,
        "x_axis": x_axis,
        "y_feature": y_feature,
        "y_values": y_values,
        "y_axis": y_axis,
        "mean_predictions": mean_predictions,
        "interactions": interactions,
        "pdp_min": pdp_min,
        "pdp_max": pdp_max,
        "H": h_statistic,
        "deviation": np.std(mean_predictions).item(),
    }

    return par_dep


def _set_feature(feature, value, data, feature_info):
    if feature_info["subkind"] == "one_hot":
        col = feature_info["value_to_column"][feature_info["value_map"][value]]
        all_features = [feat for feat, _ in feature_info["columns_and_values"]]
        data[all_features] = 0
        data[col] = 1
    else:
        data[feature] = value


def _reset_feature(
    feature,
    data,
    data_copy,
    feature_info,
):
    if feature_info["subkind"] == "one_hot":
        all_features = [col for col, _ in feature_info["columns_and_values"]]
        data[all_features] = data_copy[all_features]
    else:
        data[feature] = data_copy[feature]


def _get_feature_to_pd(one_way_pds):
    return {par_dep["x_feature"]: par_dep for par_dep in one_way_pds}


def _one_way_clustering(*, one_way_pds, feature_to_pd, md, n_jobs):
    quant_one_way = []
    cat_one_way = []

    for p in one_way_pds:
        if (
            md.feature_info[p["x_feature"]]["kind"] == "quantitative"
            or md.feature_info[p["x_feature"]]["subkind"] == "ordinal"
        ):
            quant_one_way.append(p)
        else:
            cat_one_way.append(p)

    one_way_quantitative_clusters = _quantitative_feature_clustering(
        one_way_pds=quant_one_way, feature_to_pd=feature_to_pd, n_jobs=n_jobs
    )

    n_quant_clusters = len(one_way_quantitative_clusters)

    one_way_categorical_clusters = _categorical_feature_clustering(
        one_way_pds=cat_one_way,
        feature_to_pd=feature_to_pd,
        first_id=n_quant_clusters,
    )

    return one_way_quantitative_clusters, one_way_categorical_clusters


def _quantitative_feature_clustering(*, one_way_pds, feature_to_pd, n_jobs):
    if not one_way_pds:
        return []

    timeseries_dataset = to_time_series_dataset(
        [d["mean_predictions"] for d in one_way_pds]
    )
    features = [d["x_feature"] for d in one_way_pds]

    min_clusters = 2
    max_clusters = (
        int(len(features) / 2) if int(len(features) / 2) > 2 else len(features)
    )
    n_clusters_options = range(min_clusters, max_clusters)

    best_n_clusters = -1
    best_clusters = []
    best_score = -math.inf
    best_model = None

    for n in n_clusters_options:
        cluster_model = TimeSeriesKMeans(
            n_clusters=n, metric="dtw", max_iter=50, n_init=5, n_jobs=n_jobs
        )
        cluster_model.fit(timeseries_dataset)
        labels = cluster_model.predict(timeseries_dataset)

        score = ts_silhouette_score(timeseries_dataset, labels, metric="dtw")

        if score > best_score:
            best_score = score
            best_clusters = labels
            best_n_clusters = n
            best_model = cluster_model

    distance_to_centers = best_model.transform(timeseries_dataset)
    distances = np.min(distance_to_centers, axis=1).tolist()

    clusters_dict = {
        i: {
            "id": i,
            "type": "quantitative",
            "mean_distance": 0,
            "mean_complexity": 0,
            "features": [],
        }
        for i in range(best_n_clusters)
    }

    for feature, cluster, distance in zip(features, best_clusters, distances):
        p = feature_to_pd[feature]
        c = clusters_dict[cluster]

        p["distance_to_cluster_center"] = distance
        p["cluster"] = cluster.item()

        c["mean_distance"] += distance
        c["features"].append(feature)

    clusters = list(clusters_dict.values())

    for c in clusters:
        c["mean_distance"] = c["mean_distance"] / len(c["features"])

    return clusters


def _categorical_feature_clustering(*, one_way_pds, feature_to_pd, first_id):
    if not one_way_pds:
        return []

    features = [d["x_feature"] for d in one_way_pds]

    min_clusters = 2
    max_clusters = (
        int(len(features) / 2) if int(len(features) / 2) > 2 else len(features)
    )
    n_clusters_options = range(min_clusters, max_clusters)

    deviations = np.array([d["deviation"] for d in one_way_pds]).reshape(-1, 1)

    best_n_clusters = -1
    best_clusters = []
    best_score = -math.inf
    best_model = None

    for n in n_clusters_options:
        cluster_model = KMeans(n_clusters=n, n_init=5, max_iter=300)
        cluster_model.fit(deviations)
        labels = cluster_model.labels_

        score = silhouette_score(deviations, labels, metric="euclidean")

        if score > best_score:
            best_score = score
            best_clusters = labels
            best_n_clusters = n
            best_model = cluster_model

    distance_to_centers = best_model.transform(deviations)
    distances = np.min(distance_to_centers, axis=1).tolist()

    best_clusters += first_id

    clusters_dict = {
        (i + first_id): {
            "id": i + first_id,
            "type": "categorical",
            "mean_distance": 0,
            "mean_complexity": 0,
            "features": [],
        }
        for i in range(best_n_clusters)
    }

    # sort features by distance to cluster center
    feat_clust_dist = sorted(zip(features, best_clusters, distances), key=itemgetter(2))

    for feature, cluster, distance in feat_clust_dist:
        p = feature_to_pd[feature]
        c = clusters_dict[cluster]

        p["distance_to_cluster_center"] = distance
        p["cluster"] = cluster.item()

        c["mean_distance"] += distance
        c["features"].append(feature)

    clusters = list(clusters_dict.values())

    for c in clusters:
        c["mean_distance"] = c["mean_distance"] / len(c["features"])

    return clusters


def _calculate_ice(ice_lines, data, feature, md):
    centered_ice_lines = []

    # todo - vectorize
    for instance in ice_lines:
        centered_ice_lines.append(instance - instance[0])

    centered_ice_lines = np.array(centered_ice_lines)

    timeseries_dataset = to_time_series_dataset(centered_ice_lines)

    best_labels = []
    best_score = -math.inf
    best_n_clusters = -1

    for n in range(2, 5):
        cluster_model = TimeSeriesKMeans(
            n_clusters=n, metric="euclidean", max_iter=50, n_init=1, n_jobs=1
        )
        cluster_model.fit(timeseries_dataset)
        labels = cluster_model.predict(timeseries_dataset)

        score = ts_silhouette_score(timeseries_dataset, labels, metric="euclidean")

        if score > best_score:
            best_score = score
            best_n_clusters = n
            best_labels = labels

    clusters = []

    mean_min = math.inf
    mean_max = -math.inf

    p10_min = math.inf
    p90_max = -math.inf

    centered_mean_min = math.inf
    centered_mean_max = -math.inf

    interacting_features = set()

    for n in range(best_n_clusters):
        lines = ice_lines[best_labels == n]
        centered_lines = centered_ice_lines[best_labels == n]

        y = (best_labels == n).astype(int)
        interacting_features.update(_get_interacting_features(data, y, md))

        mean = lines.mean(axis=0)
        centered_mean = centered_lines.mean(axis=0)
        compared_mean = mean - mean[0]

        p10 = np.percentile(centered_lines, 10, axis=0)
        p25 = np.percentile(centered_lines, 25, axis=0)
        p75 = np.percentile(centered_lines, 75, axis=0)
        p90 = np.percentile(centered_lines, 90, axis=0)

        clusters.append(
            {
                "id": n,
                "ice_lines": lines.tolist(),
                "centered_ice_lines": centered_lines.tolist(),
                "mean": mean.tolist(),
                "p10": p10.tolist(),
                "p25": p25.tolist(),
                "p75": p75.tolist(),
                "p90": p90.tolist(),
                "centered_mean": centered_mean.tolist(),
                "compared_mean": compared_mean.tolist(),
            }
        )

        p10_min = min(p10_min, p10.min())
        p90_max = max(p90_max, p90.max())

        mean_min = min(mean_min, mean.min())
        mean_max = max(mean_max, mean.max())

        centered_mean_min = min(centered_mean_min, centered_mean.min())
        centered_mean_max = max(centered_mean_max, centered_mean.max())

    pairs = {
        (min(feature, other), max(feature, other))
        for other in interacting_features
        if feature != other
    }

    centered_pdp = centered_ice_lines.mean(axis=0)

    cluster_distance = 0

    for cluster in clusters:
        cluster_distance += np.mean(
            np.absolute(cluster["centered_mean"] - centered_pdp)
        )

    ice = {
        "ice_min": ice_lines.min().item(),
        "ice_max": ice_lines.max().item(),
        "centered_ice_min": centered_ice_lines.min().item(),
        "centered_ice_max": centered_ice_lines.max().item(),
        "mean_min": mean_min.item(),
        "mean_max": mean_max.item(),
        "centered_mean_min": centered_mean_min.item(),
        "centered_mean_max": centered_mean_max.item(),
        "p10_min": p10_min.item(),
        "p90_max": p90_max.item(),
        "clusters": clusters,
        "centered_pdp": centered_pdp.tolist(),
        "cluster_distance": cluster_distance.item(),
        "interacting_features": list(interacting_features),
        "cluster_labels": best_labels.tolist(),
    }

    return ice, pairs


def _get_interacting_features(X, y, md):
    clf = DecisionTreeClassifier(max_depth=3, ccp_alpha=0.01)
    clf.fit(X, y)

    return {
        md.one_hot_encoded_col_name_to_feature.get(X.columns[i], X.columns[i])
        for i in clf.tree_.feature
    }
