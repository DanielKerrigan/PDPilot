<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import type { Shape, ShapeSelections } from '../types';

  let allShapes: Shape[] = ['increasing', 'decreasing', 'mixed'];

  let selections: ShapeSelections = {
    quantitative: {
      checked: true,
      shapes: allShapes,
    },
    ordinal: {
      checked: true,
      shapes: allShapes,
    },
    nominal: {
      checked: true,
    },
  };

  function quantitativeChange() {
    if (selections.quantitative.checked) {
      selections.quantitative.shapes = allShapes;
    } else {
      selections.quantitative.shapes = [];
    }
  }

  function quantitativeShapeChange() {
    selections.quantitative.checked =
      selections.quantitative.shapes.length !== 0;
  }

  function ordinalChange() {
    if (selections.ordinal.checked) {
      selections.ordinal.shapes = allShapes;
    } else {
      selections.ordinal.shapes = [];
    }
  }

  function ordinalShapeChange() {
    selections.ordinal.checked = selections.ordinal.shapes.length !== 0;
  }

  const dispatch = createEventDispatcher<{
    changeKindFilters: ShapeSelections;
  }>();

  onMount(() => {
    dispatch('changeKindFilters', selections);
  });

  $: dispatch('changeKindFilters', selections);
</script>

<div>
  <ul>
    <li>
      <label class="label-and-input">
        <input
          type="checkbox"
          indeterminate={selections.quantitative.shapes.length > 0 &&
            selections.quantitative.shapes.length < allShapes.length}
          bind:checked={selections.quantitative.checked}
          on:change={quantitativeChange}
        /><span>Quantitative</span>
      </label>
      <ul>
        <li>
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:group={selections.quantitative.shapes}
              on:change={quantitativeShapeChange}
              value="increasing"
            /><span>Increasing</span>
          </label>
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:group={selections.quantitative.shapes}
              on:change={quantitativeShapeChange}
              value="decreasing"
            /><span>Decreasing</span>
          </label>
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:group={selections.quantitative.shapes}
              on:change={quantitativeShapeChange}
              value="mixed"
            /><span>Mixed</span>
          </label>
        </li>
      </ul>
    </li>
    <li>
      <label class="label-and-input">
        <input
          type="checkbox"
          indeterminate={selections.ordinal.shapes.length > 0 &&
            selections.ordinal.shapes.length < allShapes.length}
          bind:checked={selections.ordinal.checked}
          on:change={ordinalChange}
        /><span>Ordinal</span>
      </label>
      <ul>
        <li>
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:group={selections.ordinal.shapes}
              on:change={ordinalShapeChange}
              value="increasing"
            /><span>Increasing</span>
          </label>
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:group={selections.ordinal.shapes}
              on:change={ordinalShapeChange}
              value="decreasing"
            /><span>Decreasing</span>
          </label>
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:group={selections.ordinal.shapes}
              on:change={ordinalShapeChange}
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
