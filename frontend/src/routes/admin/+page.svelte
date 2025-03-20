<!-- src/routes/+page.svelte -->
<script>
  import { goto } from '$app/navigation';

  let attackTypes = ['webcrawler', 'Bruteforcer'];
  let selectedAttack = '';

  function navigateToPage() {
    if (selectedAttack) {
      // Converts to lowercase and replaces spaces with hyphens.
      goto(`/${selectedAttack.replace(/\s+/g, '-')}`);
    }
  }
</script>

<main class="container">
  <div class="island">
    <label for="attack-select">Select an Option:</label>
    <select id="attack-select" bind:value={selectedAttack}>
      <option value="" disabled selected>Select...</option>
      {#each attackTypes as type}
        <option value={type}>{type}</option>
      {/each}
    </select>
    <button on:click={navigateToPage}>Go</button>
  </div>
</main>

<style>
  .container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: #f0f0f0;
  }
  .island {
    background: white;
    padding: 2rem;
    border-radius: 0.5rem;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    text-align: center;
  }
  select {
    padding: 0.5rem;
    margin: 1rem 0;
    width: 100%;
  }
  button {
    padding: 0.5rem 1rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
  }
  button:hover {
    background: #0056b3;
  }
</style>
