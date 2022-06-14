#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Daniel Kerrigan.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import DOMWidget
from traitlets import Unicode, List, Bool, Int, observe
from ._frontend import module_name, module_version

from itertools import combinations
import numpy as np

from .logging import log

class PDPExplorerWidget(DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('PDPExplorerModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('PDPExplorerView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    features = List([]).tag(sync=True)

    selected_features = List([]).tag(sync=True)
    resolution = Int(20).tag(sync=True)
    num_instances_used = Int(100).tag(sync=True)
    total_num_instances = Int(100).tag(sync=True)

    single_pdps = List([]).tag(sync=True)
    double_pdps = List([]).tag(sync=True)

    is_calculating = Bool(False).tag(sync=True)

    plot_button_clicked = Int(0).tag(sync=True)


    def __init__(self, model, dataset, feature_to_one_hot, **kwargs):
      super().__init__(**kwargs)

      # sklearn model
      self.model = model

      # pandas dataframe
      self.dataset = dataset

      self.total_num_instances = dataset.shape[0]
      self.num_instances_used = min(100, self.num_instances_used)

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
        feat
        for feat in dataset.columns
        if feat not in self.one_hot_features
      ]

      # list of feature to show in the UI. replace one hot features with the original feature.
      self.features = sorted(normal_features + list(self.feature_to_one_hot.keys()))

      # dictionary from tuple of original feature name and value to one hot feature name
      self.value_to_one_hot = {
        (feature, value): one_hot
        for feature, one_hots in feature_to_one_hot.items()
        for one_hot, value in one_hots
      }

      # dictionary from feature name to sorted list of unique values for that feature
      self.unique_feature_vals = {
        col: sorted(list(dataset[col].unique()))
        for col in normal_features
      }
      for feature, one_hot_info in self.feature_to_one_hot.items():
        self.unique_feature_vals[feature] = sorted([value for (_, value) in one_hot_info])

      # get numeric features with more than 12 values
      self.quantitative_features = {
        feature
        for feature in dataset.select_dtypes(include='number').columns
        if feature not in self.one_hot_features and len(self.unique_feature_vals[feature]) > 12
      }


    @observe('plot_button_clicked')
    def on_plot_button_clicked(self, change):
      if self.num_instances_used == self.total_num_instances:
        subset = self.dataset
        subset_copy = subset.copy()
      else:
        subset = self.dataset.sample(n=self.num_instances_used)
        subset_copy = subset.copy()

      singles = self.selected_features
      pairs = combinations(self.selected_features, 2)

      single_results = []

      for feature in singles:
        single_results.append(self.calc_single_pdp(feature, subset, subset_copy))

      double_results = []

      for (x_feature, y_feature) in pairs:
        double_results.append(self.calc_double_pdp(x_feature, y_feature, subset, subset_copy))

      self.single_pdps = single_results
      self.double_pdps = double_results


    def calc_single_pdp(self, feature, subset, subset_copy):
      results = []

      for value in self.get_feature_values(feature):
        self.set_feature(feature, value, subset)

        X = subset.to_numpy()
        predictions = self.model.predict(X)
        avg_pred = np.mean(predictions)

        results.append({
          'x': value,
          'avg_pred': avg_pred
        })

      self.reset_feature(feature, subset, subset_copy)

      x_is_quant = feature in self.quantitative_features

      return {
        'type': 'quantitative-single' if x_is_quant else 'categorical-single',
        'x_feature': feature,
        'values': results
      }


    def calc_double_pdp(self, x_feature, y_feature, subset, subset_copy):
      results = []

      # when one feature is quantitative and the other is categorical,
      # make the y feature be categorical
      if y_feature in self.quantitative_features and x_feature not in self.quantitative_features:
        x_feature, y_feature = y_feature, x_feature

      x_axis = self.get_feature_values(x_feature)
      y_axis = self.get_feature_values(y_feature)

      for c, x_value in enumerate(x_axis):
        self.set_feature(x_feature, x_value, subset)

        for r, y_value in enumerate(y_axis):
          self.set_feature(y_feature, y_value, subset)

          X = subset.to_numpy()
          predictions = self.model.predict(X)
          avg_pred = np.mean(predictions)

          results.append({
            'x': x_value,
            'y': y_value,
            'row': r,
            'col': c,
            'avg_pred': avg_pred
          })

          self.reset_feature(y_feature, subset, subset_copy)

        self.reset_feature(x_feature, subset, subset_copy)

      x_is_quant = x_feature in self.quantitative_features
      y_is_quant = y_feature in self.quantitative_features

      if x_is_quant and y_is_quant:
        type = 'quantitative-double'
      elif x_is_quant or y_is_quant:
        type = 'mixed-double'
      else:
        type = 'categorical-double'

      return {
        'type': type,
        'x_feature': x_feature,
        'x_axis': x_axis,
        'y_feature': y_feature,
        'y_axis': y_axis,
        'values': results
      }


    def set_feature(self, feature, value, subset):
      if feature in self.feature_to_one_hot:
        value_feature = self.value_to_one_hot[(feature, value)]
        all_features = [feat for feat, _  in self.feature_to_one_hot[feature]]
        subset[all_features] = 0
        subset[value_feature] = 1
      else:
        subset[feature] = value


    def reset_feature(self, feature, subset, subset_copy):
      if feature in self.feature_to_one_hot:
        all_features = [feat for feat, _  in self.feature_to_one_hot[feature]]
        subset[all_features] = subset_copy[all_features]
      else:
        subset[feature] = subset_copy[feature]


    def get_feature_values(self, feature):
      if feature in self.quantitative_features and self.resolution < len(self.unique_feature_vals[feature]):
        min_val = self.unique_feature_vals[feature][0]
        max_val = self.unique_feature_vals[feature][-1]
        return list(np.linspace(min_val, max_val, self.resolution))
      else:
        return self.unique_feature_vals[feature]