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

  let text: SVGTextElement;

  function updateText(label: string, width: number) {
    if (!text) {
      return;
    }

    text.textContent = label;

    let part = label;

    while (part.length > 0 && text.getComputedTextLength() > width) {
      part = part.slice(0, -1);
      text.textContent = part + '…';
    }
  }

  onMount(() => {
    updateText(label, width);
  });

  $: updateText(label, width);
</script>

<text
  bind:this={text}
  {x}
  {y}
  {width}
  {height}
  fill="black"
  dominant-baseline="hanging"
  text-anchor="middle"
  class:pdpilot-bold={bold}
  font-size={fontSize}
  transform={rotate ? `rotate(270, ${x}, ${y})` : null}
>
  <title>{label}</title>
</text>

<style>
</style>
