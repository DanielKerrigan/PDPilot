import { DOMWidgetModel, DOMWidgetView } from '@jupyter-widgets/base';
import type { ISerializers } from '@jupyter-widgets/base';
import { setStores } from './stores';

import { MODULE_NAME, MODULE_VERSION } from './version';

import Widget from './components/Widget.svelte';

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
      feature_names: [],
      feature_info: {},
      dataset: {},
      num_instances: 0,
      one_way_pds: [],
      two_way_pds: [],
      two_way_pdp_extent: [0, 0],
      two_way_interaction_extent: [0, 0],
      ice_line_extent: [0, 0],
      ice_cluster_center_extent: [0, 0],
      ice_cluster_band_extent: [0, 0],
      ice_cluster_line_extent: [0, 0],
      height: 600,
      highlighted_indices: [],
      two_way_to_calculate: [],
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
    setStores(this.model);
    new Widget({ target: this.el });
  }
}
