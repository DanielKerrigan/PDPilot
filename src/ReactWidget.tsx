import React, { ChangeEvent, useState } from 'react';
import { WidgetModel } from '@jupyter-widgets/base';
import { useModelState, WidgetModelContext } from './hooks/widget-model';
import { VegaLite, VisualizationSpec } from 'react-vega';
import { Col, Row } from 'react-bootstrap';
import BootstrapSwitchButton from 'bootstrap-switch-button-react';

interface WidgetProps {
  model: WidgetModel;
}

function ReactWidget(props: WidgetProps) {
  // The features that a user can select from the dataset
  const [features] = useModelState('features');
  // The feature chosen to display a single PDP for.
  const [selectedSingleFeature, setSelectedSingleFeature] = useModelState(
    'selected_single_feature'
  );
  // The feature chosen to display a single PDP for.
  const [selectedDoubleFeatures, setSelectedDoubleFeatures] = useModelState(
    'selected_double_features'
  );

  // Toggle values used on the front end to show/hide plots
  const [showDoublePlots, setShowDoublePlots] = useState(false);

  const [selectedSinglePdp] = useModelState('selected_single_pdp');
  const singleVisData = { table: selectedSinglePdp.map((d) => ({ ...d })) };

  const [selectedDoublePdp] = useModelState('selected_double_pdp');
  const doubleVisData = { table: selectedDoublePdp.map((d) => ({ ...d })) };

  const lineChartSpec: VisualizationSpec = {
    width: 400,
    height: 200,
    mark: 'line',
    encoding: {
      x: { field: 'x', type: 'quantitative' },
      y: { field: 'y', type: 'quantitative' },
    },
    data: { name: 'table' },
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
          values: [...new Set(selectedDoublePdp.map((d) => d.x))].filter(
            (_, i) => i % 5 === 0
          ),
        },
      },
      y: {
        field: 'y',
        type: 'ordinal',
        axis: {
          format: '.3~f',
          values: [...new Set(selectedDoublePdp.map((d) => d.y))].filter(
            (_, i) => i % 5 === 0
          ),
        },
      },
      color: {
        field: 'value',
        type: 'quantitative',
      },
    },
    data: { name: 'table' },
  };

  function onSingleFeatureChange(e: ChangeEvent<HTMLSelectElement>) {
    setSelectedSingleFeature(+e.target.value);
  }

  function onFirstFeatureChange(e: ChangeEvent<HTMLSelectElement>) {
    const features = selectedDoubleFeatures.slice();
    features[0] = +e.target.value;
    setSelectedDoubleFeatures(features);
  }

  function onSecondFeatureChange(e: ChangeEvent<HTMLSelectElement>) {
    const i = +e.target.value;
    setSelectedDoubleFeatures([selectedDoubleFeatures[0], i]);
  }

  function renderToolbar() {
    return (
      <div>
        <Col style={{ backgroundColor: 'lightBlue' }} className="p-3">
          <Row>
            <h3>PDP Ranking Tool</h3>
          </Row>
          <Row className="mbp-3">
            <Col className="col-3">
              <BootstrapSwitchButton
                checked={showDoublePlots}
                onlabel="Show Single PDP's"
                offlabel="Show Double PDP's"
                onChange={(checked: boolean) => {
                  setShowDoublePlots(checked);
                }}
              />
            </Col>
            <Col></Col>
          </Row>
        </Col>
      </div>
    );
  }

  function renderSingleFeatures() {
    return (
      <div>
        <label>
          Single PDP Feature:
          <select
            value={selectedSingleFeature}
            onChange={onSingleFeatureChange}
          >
            {features.map((feature: string, i: number) => (
              <option value={i}>{feature}</option>
            ))}
          </select>
        </label>
        <VegaLite spec={lineChartSpec} data={singleVisData} />
      </div>
    );
  }

  function renderDoubleFeatures() {
    return (
      <div>
        <div>
          <label>
            Double PDP Feature #1:
            <select
              value={selectedDoubleFeatures[0]}
              onChange={onFirstFeatureChange}
            >
              {features.map((feature: string, i: number) => (
                <option value={i}>{feature}</option>
              ))}
            </select>
          </label>
        </div>
        <div>
          <label>
            Double PDP Feature #2:
            <select
              value={selectedDoubleFeatures[1]}
              onChange={onSecondFeatureChange}
            >
              {features.map((feature: string, i: number) => (
                <option value={i}>{feature}</option>
              ))}
            </select>
          </label>
        </div>
        <div>
          <VegaLite spec={heatMapSpec} data={doubleVisData} />
        </div>
      </div>
    );
  }

  return (
    <div className="Widget">
      {renderToolbar()}
      {!showDoublePlots && renderSingleFeatures()}
      {showDoublePlots && renderDoubleFeatures()}
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
