import React from 'react';
import { WidgetModel } from '@jupyter-widgets/base';
import { useModelState, WidgetModelContext} from './hooks/widget-model';
import { VegaLite, VisualizationSpec } from 'react-vega';

interface WidgetProps {
  model: WidgetModel;
}

function ReactWidget(props: WidgetProps) {
  const [features] = useModelState('features');
  const [pdp_data] = useModelState('pdp_data');
  const [selectedFeature, setSelectedFeature] = useModelState('selected_feature');

  const visData = { table: pdp_data };
  const visSpec: VisualizationSpec = {
    width: 400,
    height: 200,
    mark: 'line',
    encoding: {
      x: { field: 'x', type: 'quantitative' },
      y: { field: 'y', type: 'quantitative' },
    },
    data: { name: 'table' }
  };

  return (
    <div className="Widget">
      <div>
        <label>
          Feature:
          <select value={selectedFeature} onChange={(e) => setSelectedFeature(+e.target.value)}>
            {features.map((feature: string, i: number) => (
              <option value={i}>{feature}</option>
            ))}
          </select>
        </label>
      </div>
      <div>
        <VegaLite spec={visSpec} data={visData}/>
      </div>
    </div>
  );
}

function withModelContext(Component: (props: WidgetProps) => JSX.Element) {
  return (props: WidgetProps) => (
    <WidgetModelContext.Provider value={props.model}>
      <Component {...props} />
    </WidgetModelContext.Provider>
  );
}

export default withModelContext(ReactWidget);
