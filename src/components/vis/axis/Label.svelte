<script lang="ts">
  import { onMount } from 'svelte';

  export let width = 0;
  export let height = 0;
  export let x = 0;
  export let y = 0;
  export let bold = false;
  export let rotate = false;
  export let label = '';
  export let fontSize = 14;

  let tspan: SVGTSpanElement;

  function updateText(label: string, width: number) {
    if (!tspan) {
      return;
    }

    tspan.textContent = label;

    let part = label;

    while (part.length > 0 && tspan.getComputedTextLength() > width) {
      part = part.slice(0, -1);
      tspan.textContent = part + '…';
    }
  }

  onMount(() => {
    updateText(label, width);
  });

  $: updateText(label, width);
</script>

<text
  {x}
  {y}
  {width}
  {height}
  fill="black"
  class:pdpilot-bold={bold}
  font-size={fontSize}
  transform={rotate ? `rotate(270, ${x}, ${y})` : null}
>
  <tspan dominant-baseline="hanging" text-anchor="middle" bind:this={tspan} />
  <title>{label}</title>
</text>

<style>
</style>
