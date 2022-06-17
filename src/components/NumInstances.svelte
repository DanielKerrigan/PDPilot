<script lang="ts">
  import { total_num_instances } from "../stores";
  import { isNumeric } from "../Utils";
  export let localNumInstances: number;

  let localNumInstancesString: string = `${localNumInstances}`;

  function onChange() {
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



<style>
  label {
    display: flex;
    align-items: center;
    gap: 1em;
  }

  input {
    width: 0;
    flex: 1;
  }
</style>