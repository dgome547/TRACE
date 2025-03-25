<script>
  export let label = "Click";
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  function handleClick(event) {
    dispatch('click', event);
  }
</script>

<button on:click={handleClick} class="app-button">
  {label}
</button>

<style>
  .app-button {
    background-color: var(--primary);
    color: var(--text);
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
</style>