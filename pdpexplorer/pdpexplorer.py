#!/usr/bin/env python
# coding: utf-8

"""
TODO: Add module docstring
"""

from ipywidgets import DOMWidget
from traitlets import Unicode, List, Bool, Int, observe
from ._frontend import module_name, module_version

from itertools import combinations
import numpy as np

from .logging import log
from .pdp import get_single_pdps, get_double_pdps

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
      subset = self.dataset.sample(n=self.num_instances_used)

      pairs = combinations(self.selected_features, 2)

      self.single_pdps = get_single_pdps(
        self.model,
        subset,
        self.selected_features,
        self.resolution,
        self.feature_to_one_hot,
        self.value_to_one_hot,
        self.quantitative_features,
        self.unique_feature_vals
      )

      self.double_pdps = get_double_pdps(
        self.model,
        subset,
        pairs,
        self.resolution,
        self.feature_to_one_hot,
        self.value_to_one_hot,
        self.quantitative_features,
        self.unique_feature_vals
      )
