<script lang="ts">
  import Controls from './Controls.svelte';
  import Main from './Main.svelte';
</script>

<div class='pdp-explorer-widget-container'>
  <Controls />
  <Main />
</div>

<style>
  div {
    box-sizing: border-box;
    width: 100%;
    height: 700px;
    display: flex;
    font-size: 16px;
    border: 1px solid var(--gray-1);
    background-color: white;
    color: black;

    --magenta: rgb(121, 35, 103);

    --blue: rgb(0, 95, 204);

    --gray-0: rgb(247, 247, 247);
    --gray-1: rgb(226, 226, 226);
    --gray-2: rgb(198, 198, 198);
    --gray-3: rgb(171, 171, 171);
    --gray-4: rgb(145, 145, 145);
    --gray-5: rgb(119, 119, 119);
    --gray-6: rgb(94, 94, 94);
    --gray-7: rgb(71, 71, 71);
    --gray-8: rgb(48, 48, 48);
    --gray-9: rgb(27, 27, 27);
    
    --red: red;
  }

  /* global styles */

  .pdp-explorer-widget-container :global(canvas),
  .pdp-explorer-widget-container :global(svg) {
    display: block;
  }

  .pdp-explorer-widget-container :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    line-height: 1.2;
  }

  .pdp-explorer-widget-container :global(a) {
    color: var(--blue);
  }

  .pdp-explorer-widget-container :global(a:hover) {
    text-decoration: none;
  }

  .pdp-explorer-widget-container :global(button) {
    color: black;
    background-color: white;
    border: 1px solid black;
    border-radius: 0.25em;
    text-align: center;
    cursor: pointer;
    font-size: 1em;
    padding: 0.0625em 0.0625em;
    font-family: inherit;
  }

  .pdp-explorer-widget-container :global(button:hover:enabled) {
    background-color: var(--gray-0);
  }

  .pdp-explorer-widget-container :global(button:active:enabled) {
    background-color: var(--gray-1);
  }

  .pdp-explorer-widget-container :global(button:disabled) {
    cursor: not-allowed;
    background-color: transparent;
    color: var(--gray-4);
    border-color: var(--gray-4);
  }

  .pdp-explorer-widget-container :global(h1) {
    font-size: 1.125em;
    font-weight: 500;
  }

  .pdp-explorer-widget-container :global(.large) {
    font-size: 1.125rem;
  }

  .pdp-explorer-widget-container :global(.small) {
    font-size: 0.875rem;
  }

  .pdp-explorer-widget-container :global(.bold) {
    font-weight: 500;
  }

  .pdp-explorer-widget-container :global(.icon) {
    width: 1em;
    height: 1em;
  }

  .pdp-explorer-widget-container :global(.cutoff) {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .pdp-explorer-widget-container :global(:focus-visible) {
    outline: var(--blue) auto 1px;
  }
</style>
