<script lang="ts">
  export let expanded = false;
  export let title: string;

  const size = 8;
</script>

<div class="toggle-and-title">
  <button
    style:border="none"
    style:width="{size}px"
    style:height="{size}px"
    style:padding="0"
    on:click={() => (expanded = !expanded)}
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="icon-tabler icon-tabler-chevron-down"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      stroke-width="4"
      stroke="currentColor"
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
      <polyline points={'2 12 12 22 22 12'} class:rotate-polyline={!expanded} />
    </svg>
  </button>

  <div class="group-title">{title}</div>
</div>

<style>
  .toggle-and-title {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  .icon-tabler-chevron-down polyline {
    transition: transform 150ms;
  }

  .rotate-polyline {
    transform-origin: 50% 50%;
    transform: rotate(-90deg);
  }
</style>
