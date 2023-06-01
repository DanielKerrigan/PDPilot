<script lang="ts">
  export let segments: { value: string; label: string; enabled: boolean }[];
  export let selectedValue: string;
  export let title = '';

  function onChangeValue(value: string) {
    selectedValue = value;
  }
</script>

<div class="segmented-control-container">
  {#if title}
    <div class="pdpilot-bold">{title}</div>
  {/if}
  <div class="segmented-control-buttons-row">
    {#each segments as { value, label, enabled }}
      <button
        class:selected-segment={value === selectedValue}
        disabled={!enabled}
        on:click={() => onChangeValue(value)}>{label}</button
      >
    {/each}
  </div>
</div>

<style>
  .segmented-control-container {
    display: flex;
    gap: 0.25em;
    align-items: center;
  }

  .segmented-control-buttons-row {
    display: inline-grid;
    grid-auto-columns: 1fr;
    grid-auto-flow: column;
  }

  .segmented-control-buttons-row button {
    border-radius: 0;
    border-left: none;
    padding: 0.0625em 0.125em;
  }

  .segmented-control-buttons-row button:first-child {
    border-top-left-radius: 0.25em;
    border-bottom-left-radius: 0.25em;
    border-left: 1px solid var(--blue);
  }

  .segmented-control-buttons-row button:last-child {
    border-top-right-radius: 0.25em;
    border-bottom-right-radius: 0.25em;
  }

  .segmented-control-buttons-row button.selected-segment {
    color: white;
    background-color: var(--blue);
  }

  .segmented-control-buttons-row button.selected-segment:active {
    color: white;
    background-color: var(--dark-blue);
    border-color: var(--dark-blue);
  }
</style>
