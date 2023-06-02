import { DOMWidgetModel, DOMWidgetView } from '@jupyter-widgets/base';
import type { ISerializers } from '@jupyter-widgets/base';
import { setStores } from './stores';

import { MODULE_NAME, MODULE_VERSION } from './version';

import Widget from './components/Widget.svelte';

export class PDPilotModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: PDPilotModel.model_name,
      _model_module: PDPilotModel.model_module,
      _model_module_version: PDPilotModel.model_module_version,
      _view_name: PDPilotModel.view_name,
      _view_module: PDPilotModel.view_module,
      _view_module_version: PDPilotModel.view_module_version,
      feature_names: [],
      feature_info: {},
      dataset: {},
      labels: [],
      num_instances: 0,
      one_way_pds: [],
      feature_to_ice_lines: {},
      two_way_pds: [],
      two_way_pdp_extent: [0, 0],
      two_way_interaction_extent: [0, 0],
      one_way_pdp_extent: [0, 0],
      ice_line_extent: [0, 0],
      ice_cluster_center_extent: [0, 0],
      centered_ice_line_extent: [0, 0],
      height: 600,
      highlighted_indices: [],
      two_way_to_calculate: [],
      cluster_update: {},
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    // Add any extra serializers here
  };

  static model_name = 'PDPilotModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'PDPilotView'; // Set to null if no view
  static view_module = MODULE_NAME; // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

export class PDPilotView extends DOMWidgetView {
  render() {
    setStores(this.model);
    new Widget({ target: this.el });
  }
}
