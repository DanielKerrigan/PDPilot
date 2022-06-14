<!-- <script lang="ts">
</script>

<div>
</div>

<style>
  div {
    position: relative;
    width: 100%;
    height: 100%;
    background-color: aquamarine;
  }
</style> -->

<script lang="ts">
  export let width: number;
  export let height: number;

  $: console.log(`TEST width = ${width}, height = ${height}`);
</script>

<!-- <svg {width} {height}> -->
<!-- <svg style="width: {width}; height: {height}"> -->
<svg style="width: 100%; height: 100%;">
  <rect {width} {height} fill="purple"></rect>
</svg>

<!-- <style>
  svg {
    width: 100%;
    height: 100%;
  }
</style> -->