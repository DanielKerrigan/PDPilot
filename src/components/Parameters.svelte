<script lang="ts">
  import { total_num_instances } from "../stores";
  import { isNumeric } from "../Utils";

  export let localResolution: number;
  export let localNumInstances: number;

  let localResolutionString: string = `${localResolution}`;
  let localNumInstancesString: string = `${localNumInstances}`;

  function onChangeResolution() {
    if (!isNumeric(localResolutionString)) {
      return;
    }

    const num: number = +localResolutionString;

    if (num <= 3 || num > $total_num_instances) {
      return;
    }

    localResolution = num;
  }

  function onChangeNumInstances() {
    if (!isNumeric(localNumInstancesString)) {
      return;
    }

    const num: number = +localNumInstancesString;

    if (num <= 0 || num > $total_num_instances) {
      return;
    }

    localNumInstances = num;
  }
</script>

<div class="parameters">
  <label for="resolution-input">Resolution</label>
  <input id="resolution-input" bind:value={localResolutionString} on:change={onChangeResolution}/>

  <label for="instances-input">Instances</label>
  <input id="instances-input" bind:value={localNumInstancesString} on:change={onChangeNumInstances}/>
</div>

<style>
  input {
    min-width: 0;
    text-align: right;
  }

  .parameters {
    display: grid;
    grid-template-columns: max-content 1fr;
    column-gap: 1em;
    row-gap: 0.25em;
    align-items: center;
  }
</style>