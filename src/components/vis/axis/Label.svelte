<script lang="ts">
  export let width = 0;
  export let height = 0;
  export let x = 0;
  export let y = 0;
  export let bold = false;
  export let rotate = false;
  export let label = '';
  export let fontSize = 14;
  export let outlineColor = 'transparent';
</script>

<!-- using a foreignObject because SVG text does
not support anything like `text-overflow: ellipsis` -->

<foreignObject
  {x}
  {y}
  width={rotate ? height : width}
  height={rotate ? width : height}
>
  <div class="label-container">
    <div
      class="label-content"
      class:rotate
      style="width: {width}px; height: {height}px;"
      style:width="{width}px"
      style:height="{height}px"
      style:--outlineColor={outlineColor}
      class:outlineText={outlineColor !== 'transparent'}
    >
      <div
        class:bold
        class="cutoff"
        style="font-size: {fontSize}px; line-height: normal;"
        title={label}
      >
        {label}
      </div>
    </div>
  </div>
</foreignObject>

<style>
  .label-container {
    width: 100%;
    height: 100%;

    /* we want to center the content div in the container
    so that we can rotate the content div around its center
    and have it stay in the foreignObject */
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .label-content {
    /* center the label in the div */
    display: flex;
    justify-content: center;
    align-items: center;

    /* removing this messes up the rotation on safari,
    but adding it causes the div to appear above tooltips */
    position: fixed;
  }

  .outlineText {
    --outline-size-pos: 1px;
    --outline-size-neg: -1px;
    text-shadow: var(--outline-size-neg) var(--outline-size-neg) 0
        var(--outlineColor),
      0 var(--outline-size-neg) 0 var(--outlineColor),
      var(--outline-size-pos) var(--outline-size-neg) 0 var(--outlineColor),
      var(--outline-size-pos) 0 0 var(--outlineColor),
      var(--outline-size-pos) var(--outline-size-pos) 0 var(--outlineColor),
      0 var(--outline-size-pos) 0 var(--outlineColor),
      var(--outline-size-neg) var(--outline-size-pos) 0 var(--outlineColor),
      var(--outline-size-neg) 0 0 var(--outlineColor);
  }

  .rotate {
    transform: rotate(270deg);
  }
</style>
