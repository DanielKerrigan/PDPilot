#!/usr/bin/env python
# coding: utf-8

"""
Compute partial dependence plots
"""

import numpy as np

from .logging import log

def get_single_pdps(
  model,
  data,
  features,
  resolution,
  feature_to_one_hot,
  value_to_one_hot,
  quantitative_features,
  unique_feature_vals
):
  results = []

  data_copy = data.copy()

  for feature in features:
    result = _calc_single_pdp(
      model,
      data,
      data_copy,
      feature,
      resolution,
      feature_to_one_hot,
      value_to_one_hot,
      quantitative_features,
      unique_feature_vals
    )

    results.append(result)

  return results

def _calc_single_pdp(
  model,
  data,
  data_copy,
  feature,
  resolution,
  feature_to_one_hot,
  value_to_one_hot,
  quantitative_features,
  unique_feature_vals
):
  results = []

  for value in _get_feature_values(feature, quantitative_features, resolution, unique_feature_vals):
    _set_feature(feature, value, data, feature_to_one_hot, value_to_one_hot)

    X = data.to_numpy()
    predictions = model.predict(X)
    avg_pred = np.mean(predictions)

    results.append({
      'x': value,
      'avg_pred': avg_pred
    })

  _reset_feature(feature, data, data_copy, feature_to_one_hot)

  x_is_quant = feature in quantitative_features

  return {
    'type': 'quantitative-single' if x_is_quant else 'categorical-single',
    'id': feature,
    'x_feature': feature,
    'values': results
  }


def get_double_pdps(
  model,
  data,
  pairs,
  resolution,
  feature_to_one_hot,
  value_to_one_hot,
  quantitative_features,
  unique_feature_vals
):
  results = []

  data_copy = data.copy()

  for (x_feature, y_feature) in pairs:
    result = _calc_double_pdp(
      model,
      data,
      data_copy,
      x_feature,
      y_feature,
      resolution,
      feature_to_one_hot,
      value_to_one_hot,
      quantitative_features,
      unique_feature_vals
    )

    results.append(result)

  return results

def _calc_double_pdp(
  model,
  data,
  data_copy,
  x_feature,
  y_feature,
  resolution,
  feature_to_one_hot,
  value_to_one_hot,
  quantitative_features,
  unique_feature_vals
):
  results = []

  # when one feature is quantitative and the other is categorical,
  # make the y feature be categorical
  if y_feature in quantitative_features and x_feature not in quantitative_features:
    x_feature, y_feature = y_feature, x_feature

  x_axis = _get_feature_values(x_feature, quantitative_features, resolution, unique_feature_vals)
  y_axis = _get_feature_values(y_feature, quantitative_features, resolution, unique_feature_vals)

  for c, x_value in enumerate(x_axis):
    _set_feature(x_feature, x_value, data, feature_to_one_hot, value_to_one_hot)

    for r, y_value in enumerate(y_axis):
      _set_feature(y_feature, y_value, data, feature_to_one_hot, value_to_one_hot)

      X = data.to_numpy()
      predictions = model.predict(X)
      avg_pred = np.mean(predictions)

      results.append({
        'x': x_value,
        'y': y_value,
        'row': r,
        'col': c,
        'avg_pred': avg_pred
      })

      _reset_feature(y_feature, data, data_copy, feature_to_one_hot)

    _reset_feature(x_feature, data, data_copy, feature_to_one_hot)

  x_is_quant = x_feature in quantitative_features
  y_is_quant = y_feature in quantitative_features

  if x_is_quant and y_is_quant:
    type = 'quantitative-double'
  elif x_is_quant or y_is_quant:
    type = 'mixed-double'
  else:
    type = 'categorical-double'

  return {
    'type': type,
    'id': x_feature + ',' + y_feature,
    'x_feature': x_feature,
    'x_axis': x_axis,
    'y_feature': y_feature,
    'y_axis': y_axis,
    'values': results
  }


def _set_feature(feature, value, data, feature_to_one_hot, value_to_one_hot):
  if feature in feature_to_one_hot:
    value_feature = value_to_one_hot[(feature, value)]
    all_features = [feat for feat, _  in feature_to_one_hot[feature]]
    data[all_features] = 0
    data[value_feature] = 1
  else:
    data[feature] = value


def _reset_feature(
  feature,
  data,
  data_copy,
  feature_to_one_hot,
):
  if feature in feature_to_one_hot:
    all_features = [feat for feat, _  in feature_to_one_hot[feature]]
    data[all_features] = data_copy[all_features]
  else:
    data[feature] = data_copy[feature]


def _get_feature_values(
  feature,
  quantitative_features,
  resolution,
  unique_feature_vals
):
  if feature in quantitative_features and resolution < len(unique_feature_vals[feature]):
    min_val = unique_feature_vals[feature][0]
    max_val = unique_feature_vals[feature][-1]
    return list(np.linspace(min_val, max_val, resolution))
  else:
    return unique_feature_vals[feature]