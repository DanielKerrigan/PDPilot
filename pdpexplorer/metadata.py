import numpy as np


class Metadata:
    def __init__(
        self,
        df,
        one_hot_features,
        categorical_features,
        ordinal_features,
    ):
        self.size = df.shape[0]

        if one_hot_features is None:
            one_hot_features = {}

        one_hot_encoded_col_names = {
            encoded_col_name
            for col_and_value in one_hot_features.values()
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
            unique_feature_vals[feature] = sorted(
                [value for (_, value) in one_hot_info]
            )

        if categorical_features is None:
            categorical_features = list(
                df[non_one_hot_features].select_dtypes(["category", "object"]).columns
            )
            binary_features = {
                feature
                for feature, values in unique_feature_vals.items()
                if len(values) <= 2
            }
            categorical_features = binary_features.union(categorical_features)

        if ordinal_features is None:
            ordinal_features = {
                feature: unique_feature_vals[feature]
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
            categorical_features | set(ordinal_features.keys())
        )

        # list of feature to show in the UI.
        self.features = sorted(
            list(one_hot_features.keys())
            + list(categorical_features)
            + list(ordinal_features.keys())
            + list(quantitative_features)
        )

        self.feature_info = {}

        for feature, one_hot_info in one_hot_features.items():
            self.feature_info[feature] = {
                "kind": "one_hot",
                "columns_and_values": one_hot_info,
                "value_to_column": {value: col for col, value in one_hot_info},
                "unique_values": unique_feature_vals[feature],
            }

        for feature in categorical_features:
            self.feature_info[feature] = {
                "kind": "categorical",
                "unique_values": unique_feature_vals[feature],
            }

        for feature in ordinal_features:
            self.feature_info[feature] = {
                "kind": "ordinal",
                "unique_values": unique_feature_vals[feature],
            }

        for feature in quantitative_features:
            if np.issubdtype(df[feature].dtype, np.integer):
                self.feature_info[feature] = {
                    "kind": "integer",
                    "unique_values": unique_feature_vals[feature],
                }
            else:
                self.feature_info[feature] = {
                    "kind": "continuous",
                    "unique_values": unique_feature_vals[feature],
                }
