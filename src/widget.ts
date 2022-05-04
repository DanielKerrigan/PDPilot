// Copyright (c) Rachel Kalafos
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';
import ReactWidget from './ReactWidget';
import React from 'react';
import ReactDOM from 'react-dom';

import { MODULE_NAME, MODULE_VERSION } from './version';

// Import the CSS
import '../css/widget.css';

// Your widget state goes here. Make sure to update the corresponding
// Python state in pdp_ranker.py
export type WidgetModelState = {
  features: string[];
  selected_single_feature: number;
  selected_double_features: number[];
  selected_single_pdp: {
    x: number;
    y: number;
    value: number;
  }[];
  selected_double_pdp: {
    x: number;
    y: number;
    value: number;
  }[];
};

const defaultModelProperties: WidgetModelState = {
  features: [],
  selected_single_feature: 0,
  selected_double_features: [0, 1],
  selected_single_pdp: [],
  selected_double_pdp: [],
};

// export type WidgetModelState = typeof defaultModelProperties;

export class RankerModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: RankerModel.model_name,
      _model_module: RankerModel.model_module,
      _model_module_version: RankerModel.model_module_version,
      _view_name: RankerModel.view_name,
      _view_module: RankerModel.view_module,
      _view_module_version: RankerModel.view_module_version,
      ...defaultModelProperties,
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    // Add any extra serializers here
  };

  static model_name = 'RankerModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'RankerView'; // Set to null if no view
  static view_module = MODULE_NAME; // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

export class RankerView extends DOMWidgetView {
  render() {
    this.el.classList.add('custom-widget');

    const component = React.createElement(ReactWidget, {
      model: this.model,
    });
    ReactDOM.render(component, this.el);
  }
}
