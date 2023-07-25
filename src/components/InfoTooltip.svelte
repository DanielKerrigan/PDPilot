<script lang="ts">
  export let kind: 'alert' | 'help' = 'help';
  export let top = 'auto';
  export let left = 'auto';
  export let right = 'auto';
  export let bottom = 'auto';

  export let marginTop = '0';
  export let marginRight = '0';
  export let marginBottom = '0';
  export let marginLeft = '0';

  export let width = '30em';

  let show = false;
</script>

<div class="tooltip-container">
  {#if kind === 'alert'}
    <!-- TODO: do this accessibly-->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="pdpilot-icon icon-tabler icon-tabler-alert-circle"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      stroke-width="2"
      stroke="currentColor"
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
      on:mouseenter={() => (show = true)}
      on:mouseleave={() => (show = false)}
    >
      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
      <circle cx="12" cy="12" r="9" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  {:else}
    <!-- question mark icon -->
    <!-- TODO: do this accessibly-->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="pdpilot-icon icon-tabler icon-tabler-help"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      stroke-width="2"
      stroke="currentColor"
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
      on:mouseenter={() => (show = true)}
      on:mouseleave={() => (show = false)}
    >
      <path stroke="none" d="M0 0h24v24H0z" />
      <circle cx="12" cy="12" r="9" />
      <line x1="12" y1="17" x2="12" y2="17.01" />
      <path d="M12 13.5a1.5 1.5 0 0 1 1 -1.5a2.6 2.6 0 1 0 -3 -4" />
    </svg>
  {/if}

  {#if show}
    <div
      class="tooltip-content pdpilot-small"
      style:top
      style:right
      style:bottom
      style:left
      style:margin="{marginTop}
      {marginRight}
      {marginBottom}
      {marginLeft}"
      style:width
    >
      <slot />
    </div>
  {/if}
</div>

<style>
  /*
      https://stackoverflow.com/questions/7117073/add-a-tooltip-to-a-div
      https://elazizi.com/a-step-by-step-guide-to-making-pure-css-tooltips
    */

  .tooltip-container {
    position: relative;
    display: flex;
    align-items: center;
  }

  .tooltip-content {
    position: absolute;

    padding: 5px;

    border-radius: 5px;
    max-width: 30em;

    border: 1px solid black;
    color: black;
    background-color: white;

    z-index: 1;

    pointer-events: none;
  }
</style>
