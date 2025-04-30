<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';
  import { goto } from '$app/navigation';
  import LoadingIcon from '$lib/components/loadingIcon.svelte';

  let urls = [];
  let bottom;
  let isPausing = false;
  let isStopping = false;
  let isPaused = false;
  let tableWrapper;
  let progress = 0;
  let stats = {
    running_time: 0,
    processed_requests: 0,
    filtered_requests: 0,
    requests_per_second: 0
  };

  onMount(() => {
    const config = get(page).state;
    const socket = new WebSocket(`ws://127.0.0.1:8000/ws/crawler`);

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket data:', data);

      if (typeof data.progress === 'number') {
        progress = data.progress;
      }

      if (data.stats) {
        console.log("Received stats:", data.stats);
        stats = {
          running_time: data.stats.running_time
            ? parseFloat(data.stats.running_time).toFixed(2)
            : '0.00',
          processed_requests: data.stats.processed_requests || 0,
          filtered_requests: data.stats.filtered_requests ?? 0,
          requests_per_second: data.stats.requests_per_second
            ? data.stats.requests_per_second.toFixed(3)
            : 0
        };
      }

      if (data.URL) {
        urls = [...urls, data];

        // Auto-scroll inside the table wrapper
        setTimeout(() => {
          if (tableWrapper) {
            tableWrapper.scrollTop = tableWrapper.scrollHeight;
          }
        }, 50);
      }
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected");
      progress = 100;
      setTimeout(() => {
        goto('/tools/crawler/results');
      }, 500); // small delay to let progress bar update visually
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  });

  async function pauseCrawler() {
      isPausing = true;
      if (isPaused) {
        await fetch('http://127.0.0.1:8000/api/crawler/resume', { method: 'POST' });
      } else {
        await fetch('http://127.0.0.1:8000/api/crawler/pause', { method: 'POST' });
      }
      isPaused = !isPaused;
      isPausing = false;
  }

  async function stopCrawler() {
      isStopping = true;
      await fetch('http://127.0.0.1:8000/api/crawler/stop', { method: 'POST' });
      isStopping = false;
  }
</script>

<style>
  .main {
    margin-left: 70px;
    padding: 20px 20px 0 20px;
    font-family: Arial, sans-serif;
    height: 100vh;
    position: relative;
    box-sizing: border-box;
  }

  .table-wrapper {
  overflow-x: auto;
  overflow-y: auto;
  max-width: 100%;
  max-height: min(60vh, 500px);
  /* border: 1px solid #ccc; */ /* removed border */
  padding: 0;
}

  .table-wrapper table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: none;
    border-radius: 10px;
    overflow: hidden;
  }

  table {
    border-collapse: separate;
    border-spacing: 0;
    width: 100%;
  }

  th, td {
    border: none;
  }

  tbody tr:nth-child(even) {
    background-color: #f2f2f2;
  }

  tbody tr:nth-child(odd) {
    background-color: #ffffff;
  }

  .table-wrapper {
    margin-top: 40px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 0;
  }

  th, td {
    /* border: 1px solid #ccc; */ /* removed border */
    padding: 8px;
    text-align: left;
  }

  thead th {
    position: sticky;
    top: 0;
    background-color: #9BC2CB;
    z-index: 2;
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
    background-color: #9BC2CB;
  }

  .stop {
    background-color: #9BC2CB;
  }

  .spinner {
    border: 3px solid #f3f3f3;
    border-top: 3px solid #333;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    animation: spin 0.6s linear infinite;
    display: inline-block;
    vertical-align: middle;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  progress {
    transition: all 0.3s ease-in-out;
  }

  progress::-webkit-progress-value {
    background-color: #9BC2CB;
    transition: width 0.3s ease-in-out;
  }

  progress::-moz-progress-bar {
    background-color: #9BC2CB;
    transition: width 0.3s ease-in-out;
  }

  .custom-progress-bar {
    width: 100%;
    height: 24px;
    background-color: #eee;
    border-radius: 12px;
    position: relative;
    overflow: hidden;
    margin-top: 5px;
  }

  .custom-progress-fill {
    height: 100%;
    background-color: #9BC2CB;
    width: 0%;
    transition: width 0.3s ease-in-out;
  }

  .custom-progress-label {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    font-size: 14px;
    line-height: 24px;
    font-weight: bold;
    color: #333;
  }

  .progress-status {
    display: flex;
    align-items: center;
    gap: 20px; /* ← Adjust spacing between spinner and text */
    font-weight: bold;
    font-size: 20px;
    margin-bottom: 10px;
  }

  .crawler-metrics {
    margin: 40px 0;
    display: flex;
    justify-content: space-between;
    text-align: center;
  }

  .crawler-metrics > div {
    flex: 1;
  }

  .crawler-metrics .metric-label {
    font-size: 20px;
    margin-bottom: 6px;
  }

  .crawler-metrics .metric-value {
    font-size: 24px;
    font-weight: bold;
  }
</style>

<div class="main">
  <h2 style="margin-bottom: 0;"> Crawler</h2>
  <p style="margin: 0 0 20px 0; font-size: 12px;">Running</p>

  

  <div style="margin: 40px 0;">
    <div class="progress-status">
      <LoadingIcon />
      <span>{progress}% Scanning</span>
    </div>
    <div class="custom-progress-bar">
      <div class="custom-progress-fill" style="width: {progress}%"></div>
    </div>
  </div>
  <div class="crawler-metrics">
    <div>
      <div class="metric-label">Running Time</div>
      <div class="metric-value">{stats.running_time}</div>
    </div>
    <div>
      <div class="metric-label">Processed Requests</div>
      <div class="metric-value">{stats.processed_requests}</div>
    </div>
    <div>
      <div class="metric-label">Filtered Requests</div>
      <div class="metric-value">{stats.filtered_requests}</div>
    </div>
    <div>
      <div class="metric-label">Requests/sec</div>
      <div class="metric-value">{stats.requests_per_second}</div>
    </div>
  </div>

  <div class="table-wrapper" bind:this={tableWrapper}>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>URL</th>
          <th>Title</th>
          <th>Word Count</th>
          <th>Character Count</th>
          <th>Links Found</th>
          <th>Error</th>
        </tr>
      </thead>
      <tbody>
        {#each urls as urlObj, i}
          <tr>
            <td>{urlObj.id}</td>
            <td>{urlObj.URL}</td>
            <td>{urlObj.Title}</td>
            <td>{urlObj.WordCount}</td>
            <td>{urlObj.CharCount}</td>
            <td>{urlObj.LinksFound}</td>
            <td>{urlObj.Error || "False"}</td>
          </tr>
        {/each}
        <tr><td colspan="7"><div bind:this={bottom}></div></td></tr>
      </tbody>
    </table>
  </div>

  <!-- Fixed bottom buttons -->
  <div class="button-container">
    <div>
      <button class="pause" on:click={pauseCrawler}>
        {#if isPausing}
          <span class="spinner"></span>
        {:else}
          {isPaused ? 'Resume' : 'Pause'}
        {/if}
      </button>
      <button class="stop" on:click={stopCrawler}>
        {#if isStopping}
          <span class="spinner"></span>
        {:else}
          Stop
        {/if}
      </button>
    </div>
  </div>
</div>