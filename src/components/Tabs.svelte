<script lang="ts">
  export let mode = 'individual';

  function changeMode(newMode: string) {
    mode = newMode;
  }
</script>

<div class="tabs-container">
  <ul>
    <li>
      <button
        id="button-tab-individual"
        class:tab-selected={mode === 'individual'}
        on:click={() => changeMode('individual')}
      >
        Individual Plots
      </button>
    </li>
    <li>
      <button
        id="button-tab-cluster"
        class:tab-selected={mode === 'cluster'}
        on:click={() => changeMode('cluster')}
      >
        Clusters
      </button>
    </li>
  </ul>
</div>

<style>
  .tabs-container {
    display: flex;
    padding: 0.25em;
  }

  #button-tab-individual, #button-tab-cluster {
    border: none;
    border-radius: 0;
  }

  #button-tab-individual.tab-selected, #button-tab-cluster.tab-selected {
    border-bottom: 1px solid black;
  }

  ul {
    list-style-type: none;
  }

  li {
    display: inline-flex;
  }

  li + li {
    margin-left: 0.5em;
  }
</style>