#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Rachel Kalafos.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""
import pandas as pd
from ipywidgets import DOMWidget
from traitlets import Unicode
from ._frontend import module_name, module_version

from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import partial_dependence


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
    regression_model = Unicode(RandomForestRegressor()).tag(sync=False)
    dataset = Unicode(pd.DataFrame()).tag(sync=False)

    def __init__(self, model, dataset, **kwargs):
        super().__init__(**kwargs)
        self.regression_model = model
        self.dataset = dataset

    def generate_pdp(self, feature: str):
        # Retrieve the partial dependence of the given feature
        pdp, axes = partial_dependence(self.regression_model, self.dataset, [feature])
        return pdp, axes
