"""Unit tests for utility functions."""

import numpy as np
import pandas as pd

from pdpilot.pdp import _get_interacting_features


def test__get_interacting_features():
    seed = 1
    rng = np.random.default_rng(seed=seed)
    num_instances = 1000

    X = pd.DataFrame(
        {
            "x1": rng.uniform(low=-1, high=1, size=(num_instances,)),
            "x2": rng.uniform(low=-1, high=1, size=(num_instances,)),
            "x3": rng.choice([0, 1], size=(num_instances,)),
            "x4": rng.choice([0, 1], size=(num_instances,)),
        }
    )

    y = X["x3"].to_numpy()

    expected = {"x3": 1.0}

    actual = _get_interacting_features(
        X=X,
        y=y,
        one_hot_encoded_col_name_to_feature={},
        decision_tree_params={"max_depth": 3, "ccp_alpha": 0.01},
        random_state=seed,
    )

    assert expected == actual
