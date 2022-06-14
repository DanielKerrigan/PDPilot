// Copyright (c) Daniel Kerrigan
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';
import { setStoreModels } from './stores';

import { MODULE_NAME, MODULE_VERSION } from './version';

import Widget from './Widget.svelte'

export class PDPExplorerModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: PDPExplorerModel.model_name,
      _model_module: PDPExplorerModel.model_module,
      _model_module_version: PDPExplorerModel.model_module_version,
      _view_name: PDPExplorerModel.view_name,
      _view_module: PDPExplorerModel.view_module,
      _view_module_version: PDPExplorerModel.view_module_version,
      features: [],
      selected_features: [],
      single_pdps: [],
      double_pdps: [],
      is_calculating: false,
      num_instances_used: 0,
      resolution: 0,
      plot_button_clicked: 0,
      total_num_instances: 0,
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    // Add any extra serializers here
  };

  static model_name = 'PDPExplorerModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'PDPExplorerView'; // Set to null if no view
  static view_module = MODULE_NAME; // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

export class PDPExplorerView extends DOMWidgetView {
  render() {
    setStoreModels(this.model);
    new Widget({ target: this.el });
  }
}
