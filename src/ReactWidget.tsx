import React, { ChangeEvent } from 'react';
import { WidgetModel } from '@jupyter-widgets/base';
import { useModelState, WidgetModelContext} from './hooks/widget-model';
import { VegaLite, VisualizationSpec } from 'react-vega';

interface WidgetProps {
  model: WidgetModel;
}

function ReactWidget(props: WidgetProps) {
  const [features] = useModelState('features');
  const [pdp_data] = useModelState('pdp_data');
  const [selectedFeatures, setSelectedFeatures] = useModelState('selected_features');

  const visData = { table: pdp_data.map(d => ({...d})) };

  const lineChartSpec: VisualizationSpec = {
    width: 400,
    height: 200,
    mark: 'line',
    encoding: {
      x: { field: 'x', type: 'quantitative' },
      y: { field: 'y', type: 'quantitative' },
    },
    data: { name: 'table' }
  };

  const heatMapSpec: VisualizationSpec = {
    width: 400,
    height: 400,
    mark: 'rect',
    encoding: {
      x: {
        field: 'x',
        type: 'ordinal',
        axis: {
          format: '.3~f',
          values: [...new Set(pdp_data.map(d => d.x))].filter((_, i) => i % 5 === 0)
        }
      },
      y: {
        field: 'y',
        type: 'ordinal',
        axis: {
          format: '.3~f',
          values: [...new Set(pdp_data.map(d => d.y))].filter((_, i) => i % 5 === 0)
        }
      },
      color: {
        field: 'value',
        type: 'quantitative'
      },
    },
    data: { name: 'table' }
  };

  function onFirstFeatureChange(e: ChangeEvent<HTMLSelectElement>) {
    const features = selectedFeatures.slice();
    features[0] = +e.target.value;
    setSelectedFeatures(features)
  }

  function onSecondFeatureChange(e: ChangeEvent<HTMLSelectElement>) {
    const i = +e.target.value;

    if (i === -1) {
      setSelectedFeatures(selectedFeatures.slice(0, 1));
    } else {
      setSelectedFeatures([selectedFeatures[0], i])
    }
  }

  return (
    <div className="Widget">
      <div>
        <label>
          First feature:
          <select value={selectedFeatures[0]} onChange={onFirstFeatureChange}>
            {features.map((feature: string, i: number) => (
              <option value={i}>{feature}</option>
            ))}
          </select>
        </label>
      </div>
      <div>
        <label>
          Second feature:
          <select value={selectedFeatures.length === 1 ? -1 : selectedFeatures[1]} onChange={onSecondFeatureChange}>
            <option value={-1}>none</option>
            {features.map((feature: string, i: number) => (
              <option value={i}>{feature}</option>
            ))}
          </select>
        </label>
      </div>
      <div>
        <VegaLite spec={selectedFeatures.length === 1 ? lineChartSpec : heatMapSpec} data={visData}/>
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
