#!/usr/bin/env python
# coding: utf-8

"""
Compute partial dependence plots
"""

from operator import itemgetter
from itertools import chain
import json
import math
from copy import deepcopy
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from scipy.stats import iqr as inner_quartile_range

from tslearn.utils import to_time_series_dataset
from tslearn.clustering import TimeSeriesKMeans, silhouette_score as ts_silhouette_score

from sklearn.linear_model import Ridge
from sklearn.preprocessing import SplineTransformer, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, silhouette_score
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier, export_text

from pdpexplorer.metadata import Metadata


def partial_dependence(
    *,
    predict,
    df,
    one_way_features=None,
    two_way_feature_pairs=None,
    n_instances=100,
    resolution=20,
    one_hot_features=None,
    categorical_features=None,
    ordinal_features=None,
    n_jobs=1,
    output_path=None,
):
    """calculates the partial dependences for the given features and feature pairs"""

    # first check that the output path exists if provided so that the function
    # can fail quickly, rather than waiting until all the work is done
    if output_path:
        path = Path(output_path).resolve()

        if not path.parent.is_dir():
            raise OSError(f"Cannot write to {path.parent}")

    # handle default list arguments
    if one_way_features is None:
        one_way_features = []

    if two_way_feature_pairs is None:
        two_way_feature_pairs = []

    # we need to compute one-way partial dependencies for all features that are included in
    # two-way plots
    one_way_features = list(
        set(chain.from_iterable(two_way_feature_pairs)).union(one_way_features)
    )

    md = Metadata(df, one_hot_features, categorical_features, ordinal_features)

    subset = df.sample(n=n_instances)
    subset_copy = df.copy()

    iqr = inner_quartile_range(predict(df))

    # one-way

    one_way_work = [
        {
            "predict": predict,
            "data": subset,
            "data_copy": subset_copy,
            "feature": feature,
            "resolution": resolution,
            "md": md,
            "iqr": iqr,
            "feature_to_pd": None,
        }
        for feature in one_way_features
    ]

    if n_jobs == 1:
        one_way_results = [_calc_pd(**args) for args in one_way_work]
    else:
        one_way_results = Parallel(n_jobs=n_jobs)(
            delayed(_calc_pd)(**args) for args in one_way_work
        )

    one_way_pds = [x[0] for x in one_way_results]
    pairs = {pair for x in one_way_results for pair in x[1]}

    feature_to_pd = _get_feature_to_pd(one_way_pds) if one_way_pds else None

    one_way_quantitative_clusters, one_way_categorical_clusters = one_way_clustering(
        one_way_pds=one_way_pds, feature_to_pd=feature_to_pd, md=md, n_jobs=n_jobs
    )

    # two-way

    two_way_work = [
        {
            "predict": predict,
            "data": subset,
            "data_copy": subset_copy,
            "feature": pair,
            "resolution": resolution,
            "md": md,
            "iqr": iqr,
            "feature_to_pd": feature_to_pd,
        }
        for pair in pairs
    ]

    if n_jobs == 1:
        two_way_pds = [_calc_pd(**args) for args in two_way_work]
    else:
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

    # marginal distributions

    marginal_distributions = get_marginal_distributions(
        df=subset, features=one_way_features, md=md
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
        "marginal_distributions": marginal_distributions,
        "n_instances": n_instances,
        "resolution": resolution,
    }

    if output_path:
        path.write_text(json.dumps(results), encoding="utf-8")
    else:
        return results


def widget_partial_dependence(
    *, predict, subset, features, resolution, md, n_jobs, one_way_pds=None, iqr=None
):
    subset_copy = subset.copy()

    feature_to_pd = _get_feature_to_pd(one_way_pds) if one_way_pds else None

    work = [
        {
            "predict": predict,
            "data": subset,
            "data_copy": subset_copy,
            "feature": feature,
            "resolution": resolution,
            "md": md,
            "iqr": iqr,
            "feature_to_pd": feature_to_pd,
        }
        for feature in features
    ]

    if n_jobs == 1:
        results = [_calc_pd(**args) for args in work]
    else:
        results = Parallel(n_jobs=n_jobs)(delayed(_calc_pd)(**args) for args in work)

    return results


def _calc_pd(
    predict,
    data,
    data_copy,
    feature,
    resolution,
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
            resolution,
            md,
            feature_to_pd,
        )
    else:
        return _calc_one_way_pd(
            predict,
            data,
            data_copy,
            feature,
            resolution,
            md,
            iqr,
        )


def _calc_one_way_pd(
    predict,
    data,
    data_copy,
    feature,
    resolution,
    md,
    iqr,
):
    feat_info = md.feature_info[feature]

    x_values = _get_feature_values(feature, feat_info, resolution)

    ice_lines = []

    for value in x_values:
        _set_feature(feature, value, data, feat_info)

        predictions = predict(data)
        ice_lines.append(predictions.tolist())

    _reset_feature(feature, data, data_copy, feat_info)

    x_is_quant = (
        feat_info["kind"] == "integer"
        or feat_info["kind"] == "continuous"
        or feat_info["kind"] == "ordinal"
    )

    ice_lines = np.array(ice_lines).T
    mean_predictions = np.mean(ice_lines, axis=0)

    mean_predictions_centered = (mean_predictions - mean_predictions.mean()).tolist()

    pdp_min = mean_predictions.min().item()
    pdp_max = mean_predictions.max().item()

    mean_predictions = mean_predictions.tolist()

    ice, pairs = calculate_ice(ice_lines=ice_lines, data=data, feature=feature, md=md)

    par_dep = {
        "num_features": 1,
        "kind": "quantitative" if x_is_quant else "categorical",
        "id": feature,
        "x_feature": feature,
        "x_values": x_values,
        "mean_predictions": mean_predictions,
        "mean_predictions_centered": mean_predictions_centered,
        "pdp_min": pdp_min,
        "pdp_max": pdp_max,
        "ice": ice,
    }

    if x_is_quant:
        # This code is adapted from
        # https://scikit-learn.org/stable/auto_examples/linear_model/plot_polynomial_interpolation.html
        # Author: Mathieu Blondel
        #         Jake Vanderplas
        #         Christian Lorentzen
        #         Malte Londschien
        # License: BSD 3 clause

        # good-fit

        X = np.array(x_values).reshape((-1, 1))
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
    else:
        par_dep["nrmse_good_fit"] = -1
        par_dep["knots_good_fit"] = -1

    par_dep["deviation"] = np.std(mean_predictions)

    return par_dep, pairs


def _calc_two_way_pd(
    predict,
    data,
    data_copy,
    pair,
    resolution,
    md,
    feature_to_pd,
):
    x_feature, y_feature = pair

    x_feat_info = md.feature_info[x_feature]
    y_feat_info = md.feature_info[y_feature]

    # when one feature is quantitative and the other is categorical,
    # make the y feature be categorical

    x_is_quant = (
        x_feat_info["kind"] == "integer"
        or x_feat_info["kind"] == "continuous"
        or x_feat_info["kind"] == "ordinal"
    )
    y_is_quant = (
        y_feat_info["kind"] == "integer"
        or y_feat_info["kind"] == "continuous"
        or y_feat_info["kind"] == "ordinal"
    )

    if y_is_quant and not x_is_quant:
        x_feature, y_feature = y_feature, x_feature
        x_is_quant, y_is_quant = y_is_quant, x_is_quant
        x_feat_info, y_feat_info = y_feat_info, x_feat_info

    x_axis = _get_feature_values(x_feature, x_feat_info, resolution)
    y_axis = _get_feature_values(y_feature, y_feat_info, resolution)

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

    if x_is_quant and y_is_quant:
        kind = "quantitative"
    elif x_is_quant or y_is_quant:
        kind = "mixed"
    else:
        kind = "categorical"

    par_dep = {
        "num_features": 2,
        "kind": kind,
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
    if feature_info["kind"] == "one_hot":
        col = feature_info["value_to_column"][value]
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
    if feature_info["kind"] == "one_hot":
        all_features = [col for col, _ in feature_info["columns_and_values"]]
        data[all_features] = data_copy[all_features]
    else:
        data[feature] = data_copy[feature]


def _get_feature_values(feature, feature_info, resolution):
    n_unique = len(feature_info["unique_values"])

    if feature_info["kind"] == "continuous" and resolution < n_unique:
        min_val = feature_info["unique_values"][0]
        max_val = feature_info["unique_values"][-1]
        return (np.linspace(min_val, max_val, resolution)).tolist()
    elif feature_info["kind"] == "integer" and resolution < n_unique:
        return (
            [feature_info["unique_values"][0]]
            + feature_info["unique_values"][1 : -1 : n_unique // resolution]
            + [feature_info["unique_values"][-1]]
        )
    else:
        return feature_info["unique_values"]


def _get_feature_to_pd(one_way_pds):
    return {par_dep["x_feature"]: par_dep for par_dep in one_way_pds}


def get_marginal_distributions(*, df, features, md):
    marginal_distributions = {}

    for feature in features:
        feature_info = md.feature_info[feature]
        if feature_info["kind"] == "one_hot":
            bins = []
            counts = []

            for col, value in feature_info["columns_and_values"]:
                bins.append(value)
                counts.append(df[col].sum().item())

            marginal_distributions[feature] = {
                "kind": "categorical",
                "bins": bins,
                "counts": counts,
            }
        elif feature_info["kind"] == "integer" or feature_info["kind"] == "continuous":
            counts, bins = np.histogram(
                df[feature],
                "auto",
                (
                    feature_info["unique_values"][0],
                    feature_info["unique_values"][-1],
                ),
            )
            marginal_distributions[feature] = {
                "kind": "quantitative",
                "bins": bins.tolist(),
                "counts": counts.tolist(),
            }
        elif feature_info["kind"] == "ordinal":
            counts, bins = np.histogram(
                df[feature],
                len(feature_info["unique_values"]),
                (
                    feature_info["unique_values"][0],
                    feature_info["unique_values"][-1],
                ),
            )
            marginal_distributions[feature] = {
                "kind": "quantitative",
                "bins": bins.tolist(),
                "counts": counts.tolist(),
            }
        else:
            bins, counts = np.unique(df[feature], return_counts=True)
            marginal_distributions[feature] = {
                "kind": "categorical",
                "bins": bins.tolist(),
                "counts": counts.tolist(),
            }

    return marginal_distributions


def one_way_clustering(*, one_way_pds, feature_to_pd, md, n_jobs):
    quant_one_way = []
    cat_one_way = []

    for p in one_way_pds:
        if (
            md.feature_info[p["x_feature"]]["kind"] == "integer"
            or md.feature_info[p["x_feature"]]["kind"] == "continuous"
            or md.feature_info[p["x_feature"]]["kind"] == "ordinal"
        ):
            quant_one_way.append(p)
        else:
            cat_one_way.append(p)

    one_way_quantitative_clusters = quantitative_feature_clustering(
        one_way_pds=quant_one_way, feature_to_pd=feature_to_pd, n_jobs=n_jobs
    )

    n_quant_clusters = len(one_way_quantitative_clusters)

    one_way_categorical_clusters = categorical_feature_clustering(
        one_way_pds=cat_one_way,
        feature_to_pd=feature_to_pd,
        first_id=n_quant_clusters,
    )

    return one_way_quantitative_clusters, one_way_categorical_clusters


def quantitative_feature_clustering(*, one_way_pds, feature_to_pd, n_jobs):
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


def categorical_feature_clustering(*, one_way_pds, feature_to_pd, first_id):
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


def calculate_ice(ice_lines, data, feature, md):
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

    pairs = set()

    for n in range(best_n_clusters):
        lines = ice_lines[best_labels == n]
        centered_lines = centered_ice_lines[best_labels == n]

        y = (best_labels == n).astype(int)
        rule_tree, rule_list, interactions = describe_cluster(
            data, y, list(data.columns), feature, md
        )
        pairs.update(interactions)

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
                "rule_tree": rule_tree,
                "rule_list": rule_list,
            }
        )

        p10_min = min(p10_min, p10.min())
        p90_max = max(p90_max, p90.max())

        mean_min = min(mean_min, mean.min())
        mean_max = max(mean_max, mean.max())

        centered_mean_min = min(centered_mean_min, centered_mean.min())
        centered_mean_max = max(centered_mean_max, centered_mean.max())

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
        "centered_ice_lines": centered_ice_lines,
        "centered_pdp": centered_pdp.tolist(),
        "compare_pdp": (ice_lines.mean(axis=0) - ice_lines.mean(axis=0)[0]).tolist(),
        "cluster_distance": cluster_distance.item(),
    }

    return ice, pairs


def describe_cluster(X, y, feature_names, current_feature, md):
    # This code is adapted from
    # https://scikit-learn.org/stable/auto_examples/tree/plot_unveil_tree_structure.html
    clf = DecisionTreeClassifier(max_depth=3, ccp_alpha=0.01)
    clf.fit(X, y)
    leaves = clf.apply(X)

    children_left = clf.tree_.children_left
    children_right = clf.tree_.children_right
    threshold = clf.tree_.threshold
    feature = clf.tree_.feature
    value = clf.tree_.value
    label = np.argmax(clf.tree_.value, axis=2).ravel()

    interacting_features = {
        md.one_hot_to_feature.get(feature_names[f], feature_names[f])
        for f in feature
        if feature_names[f] != current_feature
    }

    root = {"id": 0, "depth": 0, "kind": "empty"}

    rules = traverse(
        children_left,
        children_right,
        threshold,
        feature,
        feature_names,
        value,
        label,
        leaves,
        root,
        {},
    )

    pairs = [
        (
            min(current_feature, interacting_feature),
            max(current_feature, interacting_feature),
        )
        for interacting_feature in interacting_features
    ]

    return root, rules, pairs


def traverse(
    children_left,
    children_right,
    threshold,
    feature,
    feature_names,
    value,
    label,
    leaves,
    node,
    path,
):
    node_id = node["id"]
    is_split_node = children_left[node_id] != children_right[node_id]

    children = []

    feature_name = feature_names[feature[node_id]]

    if is_split_node:
        node["kind"] = "split"

        node_left = {
            "id": children_left[node_id],
            "feature": feature_name,
            "sign": "lte",
            "threshold": threshold[node_id],
            "depth": node["depth"] + 1,
        }

        path_left = deepcopy(path)

        if feature_name in path_left and "lte" in path_left[feature_name]:
            path_left[feature_name]["lte"] = min(
                threshold[node_id], path_left[feature_name]["lte"]
            )
        elif feature_name in path_left and "gt" in path_left[feature_name]:
            path_left[feature_name]["lte"] = threshold[node_id]
        else:
            path_left[feature_name] = {"lte": threshold[node_id]}

        left_rules = traverse(
            children_left,
            children_right,
            threshold,
            feature,
            feature_names,
            value,
            label,
            leaves,
            node_left,
            path_left,
        )
        if len(left_rules) > 0:
            children.append(node_left)

        node_right = {
            "id": children_right[node_id],
            "feature": feature_name,
            "sign": "gt",
            "threshold": threshold[node_id],
            "depth": node["depth"] + 1,
        }

        path_right = deepcopy(path)

        if feature_name in path_right and "gt" in path_right[feature_name]:
            path_right[feature_name]["gt"] = max(
                threshold[node_id], path_right[feature_name]["gt"]
            )
        elif feature_name in path_right and "lte" in path_right[feature_name]:
            path_right[feature_name]["gt"] = threshold[node_id]
        else:
            path_right[feature_name] = {"gt": threshold[node_id]}

        right_rules = traverse(
            children_left,
            children_right,
            threshold,
            feature,
            feature_names,
            value,
            label,
            leaves,
            node_right,
            path_right,
        )
        if len(right_rules) > 0:
            children.append(node_right)

        node["children"] = children

        return left_rules + right_rules

    elif label[node_id] == 1:
        num_instances = value[node_id].sum()
        num_correct = value[node_id][0, 1]

        node["kind"] = "leaf"
        node["num_instances"] = num_instances
        node["num_correct"] = num_correct
        node["accuracy"] = num_correct / num_instances
        node["indices"] = np.where(leaves == node_id)[0]

        rule = {
            "num_instances": num_instances,
            "num_correct": num_correct,
            "accuracy": num_correct / num_instances,
            "conditions": path,
        }

        return [rule]
    else:
        return []
