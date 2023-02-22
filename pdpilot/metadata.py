from typing import Union, Dict, Tuple, List
import numpy as np
import pandas as pd


class Metadata:
    def __init__(
        self,
        df: pd.DataFrame,
        resolution: int,
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

        non_one_hot_features = [
            feat for feat in df.columns if feat not in one_hot_encoded_col_names
        ]

        # dictionary from feature name to sorted list of unique values for that feature
        unique_feature_vals = {
            col: sorted(df[col].unique().tolist()) for col in non_one_hot_features
        }
        for feature, one_hot_info in one_hot_features.items():
            names = [value for (_, value) in one_hot_info]
            indices = list(range(len(names)))
            feature_value_mappings[feature] = dict(zip(indices, names))
            unique_feature_vals[feature] = indices

        if nominal_features is None:
            nominal_features = {
                feature
                for feature, values in unique_feature_vals.items()
                if len(values) <= 2
            }

        if ordinal_features is None:
            ordinal_features = {
                feature
                for feature in df[non_one_hot_features]
                .select_dtypes([np.integer])
                .columns
                if len(unique_feature_vals[feature]) > 2
                and len(unique_feature_vals[feature]) < 13
            }

        quantitative_features = set(
            df[non_one_hot_features].select_dtypes(["number"]).columns
        )
        quantitative_features = quantitative_features - (
            nominal_features | ordinal_features
        )

        # list of features to show in the UI.
        self.one_hot_feature_names = list(one_hot_features.keys())

        self.features = sorted(
            self.one_hot_feature_names
            + list(nominal_features)
            + list(ordinal_features)
            + list(quantitative_features)
        )

        self.feature_info = {}

        for feature, one_hot_info in one_hot_features.items():
            bins = []
            counts = []
            for i, (col, _) in enumerate(one_hot_info):
                bins.append(i)
                counts.append(df[col].sum().item())

            self.feature_info[feature] = {
                "kind": "categorical",
                "subkind": "one_hot",
                "ordered": False,
                "values": unique_feature_vals[feature],
                "distribution": {"bins": bins, "counts": counts},
                "columns_and_values": one_hot_info,
                "value_to_column": {value: col for col, value in one_hot_info},
                "value_map": feature_value_mappings.get(feature, {}),
            }

        for feature in nominal_features:
            bins, counts = np.unique(df[feature], return_counts=True)
            self.feature_info[feature] = {
                "kind": "categorical",
                "subkind": "nominal",
                "ordered": False,
                "values": unique_feature_vals[feature],
                "distribution": {"bins": bins.tolist(), "counts": counts.tolist()},
                "value_map": feature_value_mappings.get(feature, {}),
            }

        for feature in ordinal_features:
            bins, counts = np.unique(df[feature], return_counts=True)
            self.feature_info[feature] = {
                "kind": "categorical",
                "subkind": "ordinal",
                "ordered": True,
                "values": unique_feature_vals[feature],
                "distribution": {"bins": bins.tolist(), "counts": counts.tolist()},
                "value_map": feature_value_mappings.get(feature, {}),
            }

        for feature in quantitative_features:
            unique_vals = unique_feature_vals[feature]
            n_unique = len(unique_vals)

            counts, bins = np.histogram(
                df[feature], "sturges", (unique_vals[0], unique_vals[-1])
            )

            if np.issubdtype(df[feature].dtype, np.integer):
                # TODO: remove this?
                # TODO: why does hr return 0-23?
                values = (
                    unique_vals[:: n_unique // resolution]
                    if resolution < n_unique
                    else unique_vals
                )
                if resolution < n_unique:
                    min_val, max_val = unique_vals[0], unique_vals[-1]
                    n_points = (max_val - min_val) + 1
                    values = np.arange(
                        min_val, max_val + 1, n_points // resolution
                    ).tolist()
                    # TODO: can this be done in a smarter way? something similar to
                    # how d3 does the ticks?
                    values[-1] = max_val
                else:
                    values = unique_vals
                self.feature_info[feature] = {
                    "kind": "quantitative",
                    "subkind": "discrete",
                    "ordered": True,
                    "values": values,
                    "distribution": {"bins": bins.tolist(), "counts": counts.tolist()},
                }
            else:
                values = (
                    np.linspace(unique_vals[0], unique_vals[-1], resolution).tolist()
                    if resolution < n_unique
                    else unique_vals
                )

                self.feature_info[feature] = {
                    "kind": "quantitative",
                    "subkind": "continuous",
                    "ordered": True,
                    "values": values,
                    "distribution": {"bins": bins.tolist(), "counts": counts.tolist()},
                }
