#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Rachel Kalafos.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import DOMWidget
from traitlets import Unicode
from ._frontend import module_name, module_version

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.inspection import partial_dependence

from .data_loader import load_bike_data


class PdpRanker(DOMWidget):
    """
    Generates and ranks partial dependency plots for the given ML model.
    """
    _model_name = Unicode('RankerModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('RankerView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    # Your widget state goes here. Make sure to update the corresponding
    # JavaScript widget state (defaultModelProperties) in widget.ts
    regression_model = Unicode('').tag(sync=True)

    supported_models = {
        "random_forest": RandomForestRegressor,
        "gradient_boost": GradientBoostingRegressor
    }

    def generate_pdp(self, feature: str):
        # Load the bike data
        data_x, data_y = load_bike_data()

        # Create a regression model
        model = self.supported_models.get(self.regression_model, RandomForestRegressor)
        model().fit(data_x, data_y)

        # Retrieve the partial dependence of the given feature
        pdp, axes = partial_dependence(model, data_x, [feature])
        return pdp, axes

