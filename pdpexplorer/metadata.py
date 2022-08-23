class Metadata:
    def __init__(self, df, feature_to_one_hot, quant_threshold):
        self.size = df.shape[0]

        if not feature_to_one_hot:
            feature_to_one_hot = {}

        # dictionary from original feature to list of one hot feature and original value
        # { 'color': [('color_red', 'red'), ('color_blue', 'blue')] }
        self.feature_to_one_hot = feature_to_one_hot

        # set of one hot encoded features
        self.one_hot_features = {
            one_hot
            for one_hots in feature_to_one_hot.values()
            for one_hot, _ in one_hots
        }

        # list of non-one hot features
        normal_features = [
            feat for feat in df.columns if feat not in self.one_hot_features
        ]

        # list of feature to show in the UI. replace one hot features with the original feature.
        self.features = sorted(normal_features + list(self.feature_to_one_hot.keys()))

        # dictionary from tuple of original feature name and value to one hot feature name
        self.value_to_one_hot = {
            (feature, value): one_hot
            for feature, one_hots in self.feature_to_one_hot.items()
            for one_hot, value in one_hots
        }

        # dictionary from feature name to sorted list of unique values for that feature
        self.unique_feature_vals = {
            col: sorted(df[col].unique().tolist()) for col in normal_features
        }
        for feature, one_hot_info in self.feature_to_one_hot.items():
            self.unique_feature_vals[feature] = sorted(
                [value for (_, value) in one_hot_info]
            )

        # get numeric features with more than quant_threshold values
        self.quantitative_features = {
            feature
            for feature in df.select_dtypes(include="number").columns
            if feature not in self.one_hot_features
            and len(self.unique_feature_vals[feature]) > quant_threshold
        }
