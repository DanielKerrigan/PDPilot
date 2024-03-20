import logging
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd


logger = logging.getLogger("pdpilot")


class Metadata:
    def __init__(
        self,
        df: pd.DataFrame,
        resolution: int,
        intial_features_to_plot: List[str],
        one_hot_features: Union[Dict[str, List[Tuple[str, str]]], None],
        nominal_features: Union[List[str], None],
        ordinal_features: Union[List[str], None],
        feature_value_mappings: Union[Dict[str, Dict[str, str]], None],
    ):
        self.size = df.shape[0]

        if one_hot_features is None:
            one_hot_features = {}

        if feature_value_mappings is None:
            feature_value_mappings = {}

        one_hot_encoded_col_names = {
            encoded_col_name
            for col_and_value in one_hot_features.values()
            for encoded_col_name, _ in col_and_value
        }

        self.one_hot_encoded_col_name_to_feature = {
            encoded_col_name: feature
            for feature, col_and_value in one_hot_features.items()
            for encoded_col_name, _ in col_and_value
        }

        non_one_hot_features = {
            feat for feat in df.columns if feat not in one_hot_encoded_col_names
        }

        # dictionary from feature name to sorted list of unique values for that feature
        unique_feature_vals = {
            col: sorted(df[col].unique().tolist()) for col in non_one_hot_features
        }
        for feature, one_hot_info in one_hot_features.items():
            names = [value for (_, value) in one_hot_info]
            indices = list(range(len(names)))
            feature_value_mappings[feature] = dict(zip(indices, names))
            unique_feature_vals[feature] = indices

        self.features_to_plot = []

        for feature in intial_features_to_plot:
            if len(unique_feature_vals[feature]) == 1:
                logger.warning(
                    'Feature "%s" has only one unique value (%s). It will not be plotted.',
                    feature,
                    unique_feature_vals[feature][0],
                )
            else:
                self.features_to_plot.append(feature)

        if nominal_features is None:
            nominal_features = {
                feature
                for feature, values in unique_feature_vals.items()
                if len(values) <= 2
            }
        else:
            nominal_features = set(nominal_features)

        if ordinal_features is None:
            ordinal_features = {
                feature
                for feature in df[list(non_one_hot_features - nominal_features)]
                .select_dtypes([np.integer])
                .columns
                if len(unique_feature_vals[feature]) > 2
                and len(unique_feature_vals[feature]) < 13
            }
        else:
            ordinal_features = set(ordinal_features)

        # TODO: this is sloppy. can we assume that any remaining features are
        # numeric? or do we need to be checking the type? how would remaining
        # non-numeric features get handled?
        quantitative_features = set(
            df[list(non_one_hot_features - nominal_features - ordinal_features)]
            .select_dtypes(["number"])
            .columns
        )

        # list of features to show in the UI.
        self.one_hot_feature_names = list(one_hot_features.keys())
        # TODO: where is this actually used?
        self.features = sorted(
            self.one_hot_feature_names
            + list(nominal_features)
            + list(ordinal_features)
            + list(quantitative_features)
        )

        self.feature_info = {}

        for feature, one_hot_info in sorted(one_hot_features.items()):
            bins = []
            counts = []
            for i, (col, _) in enumerate(one_hot_info):
                bins.append(i)
                counts.append(df[col].sum().item())

            bins = np.array(bins)
            counts = np.array(counts)

            # get the order of the indices for sorting the counts in descending order
            order = np.argsort(-counts)
            # sort the bins (values), counts, and one_hot_info in that order
            bins = bins[order]
            counts = counts[order]
            one_hot_info = [one_hot_info[i] for i in order]

            percents = counts / np.sum(counts)

            self.feature_info[feature] = {
                "kind": "categorical",
                "subkind": "one_hot",
                "ordered": False,
                "values": bins.tolist(),
                "distribution": {
                    "bins": bins.tolist(),
                    "counts": counts.tolist(),
                    "percents": percents.tolist(),
                },
                "columns_and_values": one_hot_info,
                "value_to_column": {value: col for col, value in one_hot_info},
                "value_map": feature_value_mappings.get(feature, {}),
            }

        # sorting for consistent JSON output for a given random seed
        for feature in sorted(nominal_features):
            bins, counts = np.unique(df[feature], return_counts=True)

            order = np.argsort(-counts)
            bins = bins[order]
            counts = counts[order]

            percents = counts / np.sum(counts)

            self.feature_info[feature] = {
                "kind": "categorical",
                "subkind": "nominal",
                "ordered": False,
                "values": bins.tolist(),
                "distribution": {
                    "bins": bins.tolist(),
                    "counts": counts.tolist(),
                    "percents": percents.tolist(),
                },
                "value_map": feature_value_mappings.get(feature, {}),
            }

        for feature in sorted(ordinal_features):
            bins, counts = np.unique(df[feature], return_counts=True)
            percents = counts / np.sum(counts)
            self.feature_info[feature] = {
                "kind": "categorical",
                "subkind": "ordinal",
                "ordered": True,
                "values": unique_feature_vals[feature],
                "distribution": {
                    "bins": bins.tolist(),
                    "counts": counts.tolist(),
                    "percents": percents.tolist(),
                },
                "value_map": feature_value_mappings.get(feature, {}),
            }

        for feature in sorted(quantitative_features):
            unique_vals = unique_feature_vals[feature]
            n_unique = len(unique_vals)

            counts, bins = np.histogram(
                df[feature], "sturges", (unique_vals[0], unique_vals[-1])
            )
            percents = counts / np.sum(counts)

            # https://stackoverflow.com/a/49249910/5016634
            if np.issubdtype(df[feature].dtype, np.integer) or np.array_equal(
                df[feature], df[feature].astype(int)
            ):
                min_val, max_val = int(unique_vals[0]), int(unique_vals[-1])
                n_points = (max_val - min_val) + 1

                if n_points < resolution:
                    logger.warning(
                        'Integer feature "%s" has %d unique values in the range [%d,%d], but the resolution is set to %d. %d values will be used.',
                        feature,
                        n_unique,
                        min_val,
                        max_val,
                        resolution,
                        n_points,
                    )

                values = np.arange(
                    min_val, max_val + 1, max(1, round(n_points / resolution))
                ).tolist()
                # TODO: can this be done in a smarter way? something similar to
                # how d3 does the ticks?
                if values[-1] != max_val:
                    values.append(max_val)

                self.feature_info[feature] = {
                    "kind": "quantitative",
                    "subkind": "discrete",
                    "ordered": True,
                    "values": values,
                    "distribution": {
                        "bins": bins.tolist(),
                        "counts": counts.tolist(),
                        "percents": percents.tolist(),
                    },
                }
            else:
                values = np.linspace(
                    unique_vals[0], unique_vals[-1], resolution
                ).tolist()

                self.feature_info[feature] = {
                    "kind": "quantitative",
                    "subkind": "continuous",
                    "ordered": True,
                    "values": values,
                    "distribution": {
                        "bins": bins.tolist(),
                        "counts": counts.tolist(),
                        "percents": percents.tolist(),
                    },
                }
