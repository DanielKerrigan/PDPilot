<script lang="ts">
  import { mode } from '../stores';
  import type { Mode } from '../types';

  function changeMode(newMode: Mode) {
    $mode = newMode;
  }
</script>

<div class="tabs-container">
  <ul>
    <li>
      <button
        id="button-tab-grid"
        class:tab-selected={$mode === 'grid'}
        on:click={() => changeMode('grid')}
      >
        Plots Grid
      </button>
    </li>
    <li>
      <button
        id="button-tab-clusters"
        class:tab-selected={$mode === 'clusters'}
        on:click={() => changeMode('clusters')}
      >
        Clustered Plots
      </button>
    </li>
    <li>
      <button
        id="button-tab-individual"
        class:tab-selected={$mode === 'individual'}
        on:click={() => changeMode('individual')}
      >
        Individual Plot
      </button>
    </li>
  </ul>
</div>

<style>
  .tabs-container {
    display: flex;
    padding: 0.25em;
    background-color: var(--gray-1);
  }

  #button-tab-grid,
  #button-tab-clusters,
  #button-tab-individual {
    border: none;
    border-radius: 0;
    background-color: transparent;
  }

  #button-tab-grid.tab-selected,
  #button-tab-clusters.tab-selected,
  #button-tab-individual.tab-selected {
    border-bottom: 1px solid black;
  }

  ul {
    list-style: none;
  }

  li {
    display: inline-flex;
  }

  li + li {
    margin-left: 0.5em;
  }
</style>
