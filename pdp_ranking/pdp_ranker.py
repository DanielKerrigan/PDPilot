#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Rachel Kalafos.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""
from ipywidgets import DOMWidget
from traitlets import Unicode, List, Dict, Int, observe
from ._frontend import module_name, module_version

import statistics
from itertools import product, combinations
from sklearn.inspection import partial_dependence

from .output_widget_handler import OutputWidgetHandler
import logging

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

    # The selected feature for single PDP's
    selected_single_feature = Int(0).tag(sync=True)

    # The selected features for double PDP's
    selected_double_features = List([0, 1]).tag(sync=True)

    # The data for the selected single PDP
    selected_single_pdp = List([]).tag(sync=True)

    # The data for the selected double PDP
    selected_double_pdp = List([]).tag(sync=True)

    def __init__(self, model, dataset, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.dataset = dataset
        # Logging
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.handler = OutputWidgetHandler()
        self.logger.addHandler(self.handler)
        self.features = list(dataset.columns)

        # Generate all of the possible PDP's and store for retrieval
        self.all_single_pdps = self.generate_single_pdp_data()
        self.all_double_pdps = self.generate_double_pdp_data()

        # Set the values based on selected features
        self.set_single_pdp_data()
        self.set_double_pdp_data()

    @observe('selected_single_feature')
    def change_selected_single_feature(self, change):
        """This function runs when the selected single feature changes, and updates the single pdp data."""
        self.logger.info(f'selected_single_feature changed to {change.new}')
        self.set_single_pdp_data()

    @observe('selected_double_features')
    def change_selected_double_features(self, change):
        """This function runs when the selected double features change, and updates the double pdp data."""
        self.logger.info(f'selected_double_features changed to {change.new}')
        self.set_double_pdp_data()

    def set_single_pdp_data(self):
        selected_pdp = next((pdp for pdp in self.all_single_pdps if pdp["feature_index"] == self.selected_single_feature), None)
        self.selected_single_pdp = selected_pdp["pdp_graph_data"]

    def set_double_pdp_data(self):
        selected_pdp = next((pdp for pdp in self.all_double_pdps if pdp["features"] == self.selected_double_features), None)
        self.selected_double_pdp = selected_pdp["pdp_graph_data"]

    def generate_single_pdp_data(self):
        single_pdp_data = []
        for i, feature in enumerate(self.features):
            pdp = partial_dependence(self.model, self.dataset, [i], kind="average")
            ranking_metric = self.calculate_single_pdp_ranking_metric(pdp)
            single_pdp_data.append({
                "feature_index": i,
                "feature_name": feature,
                "ranking_metric": ranking_metric,
                "pdp_graph_data": self.generate_pdp([i]),
            })
        return sorted(single_pdp_data, key=lambda x: x["ranking_metric"], reverse=True)

    def generate_double_pdp_data(self):
        double_pdp_data = []
        for combo in combinations(range(len(self.features)), 2):
            pdp = partial_dependence(self.model, self.dataset, [combo], kind="average")
            ranking_metric = self.calculate_double_pdp_ranking_metric(pdp)
            double_pdp_data.append({
                "features": sorted(list(combo)),
                "ranking_metric": ranking_metric,
                "pdp_graph_data": self.generate_pdp(list(combo))
            })
        return double_pdp_data

    @staticmethod
    def calculate_single_pdp_ranking_metric(pdp):
        """
        Calculates the standard deviation of the y value points to
        determine how "interesting" a single PDP is.
        """
        y = list(pdp['average'][0])
        return statistics.stdev(y)

    @staticmethod
    def calculate_double_pdp_ranking_metric(pdp):
        """
        Calculates the standard deviation of the averages
        """
        averages = pdp['average'][0].flatten()
        return statistics.stdev(averages)

    def generate_pdp(self, features):
        # Retrieve the partial dependence of the given feature
        result = partial_dependence(self.model, self.dataset, [tuple(features)], kind='average')

        if len(features) == 1:
          y = list(result['average'][0])
          x = list(result['values'][0])
          return [{'x': x, 'y': y, 'value': 0} for (x, y) in zip(x, y)]
        elif len(features) == 2:
          grid = product(*result['values'])
          averages = result['average'][0].flatten()
          return [
            {'x': x, 'y': y, 'value': value}
            for (x, y), value in zip(grid, averages)
          ]
