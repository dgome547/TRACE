<script>
	import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
  
    let results = [];
  
    // Placeholder values – Logic not implemented in backend
    let runtime = 12.5;
    let processedRequests = 0;    
    let filteredRequests = 30;
    let requestsPerSec = (processedRequests / runtime).toFixed(2);
  
    onMount(async () => {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/crawler/results');
        if (res.ok) {
          const data = await res.json();
          results = data;
          processedRequests = data.length;
          requestsPerSec = (processedRequests / runtime).toFixed(2);
        } else {
          console.error("Failed to fetch CSV results");
        }
      } catch (err) {
        console.error("Error loading results:", err);
      }
    });
  
    function restartCrawl() {
      goto("/crawler/launch") 
    }
  
    function exportResults() {
      alert("Export to CSV coming soon");
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
  
    .status-metrics {
      display: flex;
      justify-content: space-around;
      padding: 10px;
      margin-bottom: 10px;
    }
  
    .status-box {
      text-align: center;
      font-size: 16px;
      padding: 10px;
    }
  
    .status-box span {
      font-weight: bold;
      font-size: 20px;
    }
  
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
  
    th, td {
      border: 1px solid #ccc;
      padding: 8px;
      text-align: left;
    }
  
    th {
      background-color: #9BC2CB;
      color: black;
    }
  
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
      background-color: #9BC2CB;
    }
  </style>
  
  <div class="main">
    <h2>Crawler</h2>
  
    <div class="status-metrics">
      <div class="status-box">
        <p>Running Time</p>
        <span>{runtime}</span>
      </div>
      <div class="status-box">
        <p>Processed Requests</p>
        <span>{processedRequests}</span>
      </div>
      <div class="status-box">
        <p>Filtered Requests</p>
        <span>{filteredRequests}</span>
      </div>
      <div class="status-box">
        <p>Requests/sec</p>
        <span>{requestsPerSec}</span>
      </div>
    </div>
  
    <table>
        <thead>
          <tr>
            <th>#</th>
            <th>URL</th>
            <th>Depth</th>
          </tr>
        </thead>
        <tbody>
          {#each results as row, i}
            <tr>
              <td>{i + 1}</td>
              <td>{row.URL}</td>
              <td>{row.Depth}</td>
            </tr>
          {/each}
        </tbody>
      </table>
  
    <div class="button-container">
      <div>
        <button on:click={restartCrawl}>Restart</button>
        <button on:click={exportResults}>Export |→</button>
      </div>
    </div>
  </div>