<script lang="ts">
  import Controls from "./components/Controls.svelte";
  import Main from "./components/Main.svelte";
</script>

<div class="pdp-explorer-widget-container">
  <Controls/>
  <Main/>
</div>

<style>
  div {
    width: 100%;
    height: 600px;
    display: flex;
    font-size: 16px;
    border-right: 1px solid var(--medium-gray);

    --blue: rgb(0, 99, 206);
    --dark-blue: rgb(1, 51, 104);
    --purple: rgb(123, 25, 179);
    --dark-purple: rgb(76, 0, 133);
    --light-gray: hsl(0, 0%, 98%);
    --medium-gray: hsl(0, 0%, 90%);
    --dark-gray: hsl(0, 0%, 30%);
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
    line-height: 1;
  }

  .pdp-explorer-widget-container :global(a) {
    color: var(--blue);
  }

  .pdp-explorer-widget-container :global(a:hover) {
    text-decoration: none;
  }

  .pdp-explorer-widget-container :global(button) {
    border: 1px solid var(--purple);
    border-radius: 0.25em;
    color: var(--purple);
    background-color: transparent;
    text-align: center;
    cursor: pointer;
    font-size: 1em;
    padding: 0.0625em 0.0625em;
    font-family : inherit;
  }

  .pdp-explorer-widget-container :global(button:hover:enabled) {
    background-color: var(--purple);
    color: white;
  }

  .pdp-explorer-widget-container :global(button:active:enabled) {
    border-color: var(--dark-purple);
    background-color: var(--dark-purple);
    color: white;
  }

  .pdp-explorer-widget-container :global(button:disabled) {
    cursor: not-allowed;
    color: var(--dark-gray);
    border-color: var(--dark-gray);
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
</style>