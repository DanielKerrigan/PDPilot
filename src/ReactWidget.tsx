import React from 'react';
import { WidgetModel } from '@jupyter-widgets/base';
import { useModelState, WidgetModelContext} from './hooks/widget-model';

interface WidgetProps {
  model: WidgetModel;
}

function ReactWidget(props: WidgetProps) {
  const [regModel, setRegModel] = useModelState('regression_model');
  const modelOptions = [
    { value: 'random_forest', label: 'Random Forest Regression' },
    { value: 'gradient_boost', label: 'Gradient Boosting Regression' },
  ];
  return (
    <div className="Widget">
      <h3>Selected Model: {regModel}</h3>
      <select value={regModel} onChange={(e) => setRegModel(e.target.value)}>
        {modelOptions.map((option) => (
          <option value={option.value}>{option.label}</option>
        ))}
      </select>
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
