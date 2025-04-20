

<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';
  import { goto } from '$app/navigation';

  


  let urls = [];

  onMount(() => {
    const config = get(page).state;
    const socket = new WebSocket(`ws://127.0.0.1:5000/ws/crawler?targetUrl=${encodeURIComponent(config.targetUrl)}&depth=${config.crawlDepth}&timeout=${config.requestDelay}`);

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.url) {
        urls = [...urls, data.url];
      }
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected, redirecting to results");
      goto('/crawler/results');
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  });

  function pauseCrawler() {
    console.log("⏸️ Pause button coming Soon");
  }

  function stopCrawler() {
    console.log("Stop button coming Soon");
  }
</script>

<style>
  .main {
    margin-left: 70px;
    padding: 20px;
    font-family: Arial, sans-serif;
    height: 100vh;
    position: relative;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }

  th, td {
    border: 1px solid var(--border);
    padding: 8px;
    text-align: left;
  }

  th {
    background-color: var(--primary);
    color: var(--text);
  }

  /* Fixed bottom buttons */
  .button-container {
    display: flex;
    justify-content: space-between;
    position: fixed;
    bottom: 20px;
    width: calc(100% - 70px);
    left: 70px;
    padding: 10px 20px;
  }

  .button-container button {
    padding: 10px 20px;
    margin: 5px;
    font-size: 16px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }

  .pause {
    background-color: var(--primary);
  }

  .stop {
    background-color: var(--primary);
  }
</style>

<div class="main">
  <h2> Crawler</h2>

  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>URL</th>
      </tr>
    </thead>
    <tbody>
      {#each urls as url, i}
        <tr>
          <td>{i + 1}</td>
          <td>{url}</td>
        </tr>
      {/each}
    </tbody>
  </table>

  <!-- Fixed bottom buttons -->
  <div class="button-container">
    <div>
      <button class="pause" on:click={pauseCrawler}>Pause</button>
      <button class="stop" on:click={stopCrawler}>Stop</button>
    </div>
  </div>
</div>