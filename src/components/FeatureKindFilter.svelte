<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import type { Shape, ShapeSelections } from '../types';

  let allShapes: Shape[] = ['increasing', 'decreasing', 'mixed'];

  const allSelected: ShapeSelections = {
    ordered: {
      checked: true,
      shapes: allShapes,
    },
    nominal: {
      checked: true,
    },
  };

  function getNoneSelected(): ShapeSelections {
    return {
      ordered: {
        checked: false,
        shapes: [],
      },
      nominal: {
        checked: false,
      },
    };
  }

  let selections: ShapeSelections = getNoneSelected();

  export function clear() {
    selections = getNoneSelected();
  }

  // if all of the checkboxes are checked, then uncheck all of them
  $: if (
    selections.nominal.checked &&
    selections.ordered.checked &&
    selections.ordered.shapes.length === allShapes.length
  ) {
    selections = getNoneSelected();
  }

  function orderedChange() {
    if (selections.ordered.checked) {
      selections.ordered.shapes = allShapes;
    } else {
      selections.ordered.shapes = [];
    }
  }

  function orderedShapeChange() {
    selections.ordered.checked = selections.ordered.shapes.length !== 0;
  }

  const dispatch = createEventDispatcher<{
    changeKindFilters: ShapeSelections;
  }>();

  function dispatchSelections(shapeSelections: ShapeSelections) {
    // if nothing is selected, then the default is that all are selected
    if (
      !shapeSelections.nominal.checked &&
      !shapeSelections.ordered.checked &&
      shapeSelections.ordered.shapes.length === 0
    ) {
      dispatch('changeKindFilters', allSelected);
    } else {
      dispatch('changeKindFilters', shapeSelections);
    }
  }

  onMount(() => {
    dispatchSelections(selections);
  });

  $: dispatchSelections(selections);
</script>

<div>
  <ul>
    <li>
      <label class="label-and-input">
        <input
          type="checkbox"
          indeterminate={selections.ordered.shapes.length > 0 &&
            selections.ordered.shapes.length < allShapes.length}
          bind:checked={selections.ordered.checked}
          on:change={orderedChange}
        /><span>Ordered</span>
      </label>
      <ul>
        <li>
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:group={selections.ordered.shapes}
              on:change={orderedShapeChange}
              value="increasing"
            /><span>Increasing</span>
          </label>
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:group={selections.ordered.shapes}
              on:change={orderedShapeChange}
              value="decreasing"
            /><span>Decreasing</span>
          </label>
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:group={selections.ordered.shapes}
              on:change={orderedShapeChange}
              value="mixed"
            /><span>Mixed</span>
          </label>
        </li>
      </ul>
    </li>
    <li>
      <label class="label-and-input">
        <input type="checkbox" bind:checked={selections.nominal.checked} /><span
          >Nominal</span
        >
      </label>
    </li>
  </ul>
</div>

<style>
  ul {
    list-style: none;
  }

  .label-and-input {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  ul ul {
    margin-left: 1em;
  }
</style>
