#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Rachel Kalafos.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""
from ipywidgets import DOMWidget
from traitlets import Unicode, List, Int, observe
from ._frontend import module_name, module_version

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

    # features in the dataset
    features = List([]).tag(sync=True)

    # feature that the user has selected to view the PDP of
    selected_feature = Int(0).tag(sync=True)

    # info to show in pdp
    pdp_data = List([]).tag(sync=True)

    def __init__(self, model, dataset, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.dataset = dataset
        self.features = list(dataset.columns)
        self.generate_pdp(self.selected_feature)

    # this function runs when the selected_feature is changed
    @observe('selected_feature')
    def change_selected_feature(self, change):
        self.generate_pdp(change.new)

    def generate_pdp(self, feature):
        # Retrieve the partial dependence of the given feature
        result = partial_dependence(self.model, self.dataset, [feature], kind='average')
        y = list(result['average'][0])
        x = list(result['values'][0])
        self.pdp_data = [{'x': x, 'y': y} for (x, y) in zip(x, y)]
