#!/usr/bin/env python
# coding: utf-8

"""
Compute partial dependence plots
"""

from joblib import Parallel, delayed
from operator import itemgetter
from itertools import chain
import json
import math
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import iqr as inner_quartile_range

from pdpexplorer.metadata import Metadata
from pdpexplorer.ticks import nice, ticks
from .logging import log

from sklearn.linear_model import Ridge
from sklearn.preprocessing import SplineTransformer, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error
from plotnine import (
    ggplot,
    geom_line,
    geom_point,
    geom_tile,
    aes,
    labs,
    scale_fill_distiller,
    scale_y_continuous,
    theme_light,
    ggtitle,
    coord_cartesian,
)


def partial_dependence(
    *,
    predict,
    df,
    one_way_features=None,
    two_way_feature_pairs=None,
    n_instances=100,
    resolution=20,
    feature_to_one_hot=None,
    n_jobs=1,
    output_path=None,
    quant_threshold=12,
):
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

    md = Metadata(df, feature_to_one_hot, quant_threshold=quant_threshold)

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
        one_way_pds = [_calc_pd(**args) for args in one_way_work]
    else:
        one_way_pds = Parallel(n_jobs=n_jobs)(
            delayed(_calc_pd)(**args) for args in one_way_work
        )

    # two-way

    feature_to_pd = _get_feature_to_pd(one_way_pds) if one_way_pds else None

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
        for pair in two_way_feature_pairs
    ]

    if n_jobs == 1:
        two_way_pds = [_calc_pd(**args) for args in two_way_work]
    else:
        two_way_pds = Parallel(n_jobs=n_jobs)(
            delayed(_calc_pd)(**args) for args in two_way_work
        )

    # min and max predictions

    min_pred = min(one_way_pds, key=itemgetter("min_prediction"))["min_prediction"]
    max_pred = max(one_way_pds, key=itemgetter("max_prediction"))["max_prediction"]

    if two_way_pds:
        min_pred = min(
            min_pred,
            min(two_way_pds, key=itemgetter("min_prediction"))["min_prediction"],
        )
        max_pred = max(
            max_pred,
            max(two_way_pds, key=itemgetter("max_prediction"))["max_prediction"],
        )

    # marginal distributions

    marginal_distributions = get_marginal_distributions(
        df=subset, features=one_way_features, md=md
    )

    # output

    results = {
        "one_way_pds": one_way_pds,
        "two_way_pds": two_way_pds,
        "prediction_extent": [min_pred, max_pred],
        "marginal_distributions": marginal_distributions,
        "n_instances": n_instances,
        "resolution": resolution,
    }

    if output_path:
        path.write_text(json.dumps(results))
    else:
        return results


def plot(
    *,
    data,
    one_way_sort_by=None,
    two_way_sort_by=None,
    same_prediction_scale=True,
    output_path=None,
):
    # if data is a path or string, then read the file at that path
    if isinstance(data, Path) or isinstance(data, str):
        path = Path(data).resolve()

        if not path.exists():
            raise OSError(f"Cannot read {path}")

        json_data = path.read_text()
        data = json.loads(json_data)

    # check that the output path existsm fail early if it doesn't
    if output_path:
        output_path = Path(output_path).resolve()

        if not output_path.exists():
            raise OSError(f"Cannot write to {output_path}")

        one_way_output_path = output_path.joinpath("one_way")
        one_way_output_path.mkdir()

        if data["two_way_pds"]:
            two_way_output_path = output_path.joinpath("two_way")
            two_way_output_path.mkdir()

    min_pred, max_pred = data["prediction_extent"]

    nice_prediction_limits = nice(min_pred, max_pred, 5)
    nice_prediction_breaks = ticks(
        nice_prediction_limits[0], nice_prediction_limits[1], 5
    )

    # one-way

    one_way_pdps = []

    if one_way_sort_by == "good_fit":
        sorted_one_way_pds = sorted(
            data["one_way_pds"],
            key=lambda x: (-x["knots_good_fit"], -x["nrmse_good_fit"]),
        )
    elif one_way_sort_by == "deviation":
        sorted_one_way_pds = sorted(data["one_way_pds"], key=lambda x: -x["deviation"])
    else:
        sorted_one_way_pds = data["one_way_pds"]

    num_digits = math.floor(math.log10(len(sorted_one_way_pds))) + 1

    for i, par_dep in enumerate(sorted_one_way_pds):
        if par_dep["kind"] == "quantitative":
            df = pd.DataFrame(
                {
                    "x_values": par_dep["x_values"],
                    "mean_predictions": par_dep["mean_predictions"],
                    "trend": par_dep["trend_good_fit"],
                }
            )

            pdp = (
                ggplot(data=df, mapping=aes(x="x_values"))
                + geom_line(aes(y="trend"), color="#7C7C7C")
                + geom_line(aes(y="mean_predictions"), color="#792367")
                + labs(x=par_dep["x_feature"], y="prediction")
                + theme_light()
            )

            if same_prediction_scale:
                pdp += coord_cartesian(ylim=nice_prediction_limits, expand=False)
        else:
            df = pd.DataFrame(
                {
                    "x_values": par_dep["x_values"],
                    "mean_predictions": par_dep["mean_predictions"],
                }
            )

            pdp = (
                ggplot(data=df, mapping=aes(x="factor(x_values)", y="mean_predictions"))
                + geom_point(color="#792367")
                + labs(x=par_dep["x_feature"], y="prediction")
                + theme_light()
            )

            if same_prediction_scale:
                pdp += scale_y_continuous(limits=nice_prediction_limits, expand=(0, 0))

        if output_path:
            pdp.save(
                filename=one_way_output_path.joinpath(
                    f'{i:0>{num_digits}}_{par_dep["id"]}.png'
                ),
                format="png",
                dpi=300,
                verbose=False,
            )
        else:
            one_way_pdps.append(pdp)

    # two-way

    two_way_pdps = []

    if data["two_way_pds"]:
        if two_way_sort_by == "h":
            sorted_two_way_pds = sorted(data["two_way_pds"], key=lambda x: -x["H"])
        elif two_way_sort_by == "deviation":
            sorted_two_way_pds = sorted(
                data["two_way_pds"], key=lambda x: -x["deviation"]
            )
        else:
            sorted_two_way_pds = data["two_way_pds"]

        num_digits = math.floor(math.log10(len(sorted_two_way_pds))) + 1

        for i, par_dep in enumerate(sorted_two_way_pds):
            limits_and_breaks = (
                {"limits": nice_prediction_limits, "breaks": nice_prediction_breaks}
                if same_prediction_scale
                else {}
            )

            if par_dep["kind"] == "quantitative":
                df = pd.DataFrame(
                    {
                        "x_values": par_dep["x_values"],
                        "y_values": par_dep["y_values"],
                        "mean_predictions": par_dep["mean_predictions"],
                    }
                )

                pdp = (
                    ggplot(data=df, mapping=aes(x="x_values", y="y_values"))
                    + geom_tile(mapping=aes(fill="mean_predictions"))
                    + scale_fill_distiller(
                        palette="YlGnBu", direction=1, **limits_and_breaks
                    )
                    + labs(
                        fill="prediction",
                        x=par_dep["x_feature"],
                        y=par_dep["y_feature"],
                    )
                    + ggtitle(f'H* = {par_dep["H"]:.3f}')
                    + theme_light()
                )
            elif par_dep["kind"] == "categorical":
                df = pd.DataFrame(
                    {
                        "x_values": par_dep["x_values"],
                        "y_values": par_dep["y_values"],
                        "mean_predictions": par_dep["mean_predictions"],
                    }
                )

                pdp = (
                    ggplot(
                        data=df, mapping=aes(x="factor(x_values)", y="factor(y_values)")
                    )
                    + geom_tile(mapping=aes(fill="mean_predictions"))
                    + scale_fill_distiller(
                        palette="YlGnBu", direction=1, **limits_and_breaks
                    )
                    + labs(
                        fill="prediction",
                        x=par_dep["x_feature"],
                        y=par_dep["y_feature"],
                    )
                    + ggtitle(f'H* = {par_dep["H"]:.3f}')
                    + theme_light()
                )
            else:
                df = pd.DataFrame(
                    {
                        "x_values": par_dep["x_values"],
                        "y_values": par_dep["y_values"],
                        "mean_predictions": par_dep["mean_predictions"],
                    }
                )

                pdp = (
                    ggplot(data=df, mapping=aes(x="x_values", y="factor(y_values)"))
                    + geom_tile(mapping=aes(fill="mean_predictions"))
                    + scale_fill_distiller(
                        palette="YlGnBu", direction=1, **limits_and_breaks
                    )
                    + labs(
                        fill="prediction",
                        x=par_dep["x_feature"],
                        y=par_dep["y_feature"],
                    )
                    + ggtitle(f'H* = {par_dep["H"]:.3f}')
                    + theme_light()
                )

            if output_path:
                pdp.save(
                    filename=two_way_output_path.joinpath(
                        f'{i:0>{num_digits}}_{par_dep["id"]}.png'
                    ),
                    format="png",
                    dpi=300,
                    verbose=False,
                )
            else:
                two_way_pdps.append(pdp)

    if not output_path:
        return one_way_pdps, two_way_pdps


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
    x_values = _get_feature_values(
        feature, md.quantitative_features, resolution, md.unique_feature_vals
    )

    mean_predictions = []

    min_pred = math.inf
    max_pred = -math.inf

    for value in x_values:
        _set_feature(feature, value, data, md.feature_to_one_hot, md.value_to_one_hot)

        predictions = predict(data)
        mean_pred = np.mean(predictions).item()

        mean_predictions.append(mean_pred)

        if mean_pred < min_pred:
            min_pred = mean_pred

        if mean_pred > max_pred:
            max_pred = mean_pred

    _reset_feature(feature, data, data_copy, md.feature_to_one_hot)

    x_is_quant = feature in md.quantitative_features

    mean_predictions_centered = (
        np.array(mean_predictions) - np.mean(mean_predictions)
    ).tolist()

    par_dep = {
        "num_features": 1,
        "kind": "quantitative" if x_is_quant else "categorical",
        "id": feature,
        "x_feature": feature,
        "x_values": x_values,
        "mean_predictions": mean_predictions,
        "mean_predictions_centered": mean_predictions_centered,
        "min_prediction": min_pred,
        "max_prediction": max_pred,
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

    return par_dep


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

    # when one feature is quantitative and the other is categorical,
    # make the y feature be categorical
    if (
        y_feature in md.quantitative_features
        and x_feature not in md.quantitative_features
    ):
        x_feature, y_feature = y_feature, x_feature

    x_axis = _get_feature_values(
        x_feature, md.quantitative_features, resolution, md.unique_feature_vals
    )

    y_axis = _get_feature_values(
        y_feature, md.quantitative_features, resolution, md.unique_feature_vals
    )

    x_values = []
    y_values = []
    rows = []
    cols = []
    mean_predictions = []

    x_pdp = feature_to_pd[x_feature]
    y_pdp = feature_to_pd[y_feature]
    no_interactions = []

    min_pred = math.inf
    max_pred = -math.inf

    for c, x_value in enumerate(x_axis):
        _set_feature(
            x_feature, x_value, data, md.feature_to_one_hot, md.value_to_one_hot
        )

        for r, y_value in enumerate(y_axis):
            _set_feature(
                y_feature, y_value, data, md.feature_to_one_hot, md.value_to_one_hot
            )

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

            if mean_pred < min_pred:
                min_pred = mean_pred

            if mean_pred > max_pred:
                max_pred = mean_pred

            _reset_feature(y_feature, data, data_copy, md.feature_to_one_hot)

        _reset_feature(x_feature, data, data_copy, md.feature_to_one_hot)

    mean_predictions_centered = np.array(mean_predictions) - np.mean(mean_predictions)
    interactions = (mean_predictions_centered - np.array(no_interactions)).tolist()
    mean_predictions_centered = mean_predictions_centered.tolist()

    h_statistic = np.sqrt(np.square(interactions).sum()).item()

    x_is_quant = x_feature in md.quantitative_features
    y_is_quant = y_feature in md.quantitative_features

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
        "min_prediction": min_pred,
        "max_prediction": max_pred,
        "H": h_statistic,
        "deviation": np.std(mean_predictions).item(),
    }

    return par_dep


def _set_feature(feature, value, data, feature_to_one_hot, value_to_one_hot):
    if feature in feature_to_one_hot:
        value_feature = value_to_one_hot[(feature, value)]
        all_features = [feat for feat, _ in feature_to_one_hot[feature]]
        data[all_features] = 0
        data[value_feature] = 1
    else:
        data[feature] = value


def _reset_feature(
    feature,
    data,
    data_copy,
    feature_to_one_hot,
):
    if feature in feature_to_one_hot:
        all_features = [feat for feat, _ in feature_to_one_hot[feature]]
        data[all_features] = data_copy[all_features]
    else:
        data[feature] = data_copy[feature]


def _get_feature_values(
    feature, quantitative_features, resolution, unique_feature_vals
):
    if feature in quantitative_features and resolution < len(
        unique_feature_vals[feature]
    ):
        min_val = unique_feature_vals[feature][0]
        max_val = unique_feature_vals[feature][-1]
        return (np.linspace(min_val, max_val, resolution)).tolist()
    else:
        return unique_feature_vals[feature]


def _get_feature_to_pd(one_way_pds):
    return {par_dep["x_feature"]: par_dep for par_dep in one_way_pds}


def get_marginal_distributions(*, df, features, md):
    marginal_distributions = {}

    for feature in features:
        if feature in md.feature_to_one_hot:
            bins = []
            counts = []

            for one_hot_feature, value in md.feature_to_one_hot[feature]:
                bins.append(value)
                counts.append(df[one_hot_feature].sum().item())

            marginal_distributions[feature] = {
                "kind": "categorical",
                "bins": bins,
                "counts": counts,
            }
        elif feature in md.quantitative_features:
            counts, bins = np.histogram(
                df[feature],
                "auto",
                (
                    md.unique_feature_vals[feature][0],
                    md.unique_feature_vals[feature][-1],
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
