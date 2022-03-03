// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

// Add any needed widget imports here (or from controls)
// import {} from '@jupyter-widgets/base';

import { createTestModel } from './utils';

import { RankerModel } from '..';

describe('Example', () => {
  describe('ExampleModel', () => {
    it('should be createable', () => {
      const model = createTestModel(RankerModel);
      expect(model).toBeInstanceOf(RankerModel);
      expect(model.get('value')).toEqual('random_forest');
    });

    it('should be createable with a value', () => {
      const state = { value: 'Foo Bar!' };
      const model = createTestModel(RankerModel, state);
      expect(model).toBeInstanceOf(RankerModel);
      expect(model.get('value')).toEqual('Foo Bar!');
    });
  });
});
