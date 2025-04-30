<script>
	import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  
  
  
  let results = [];

    // Placeholder values – Logic not implemented in backend
    let runtime = 0;
    let processedRequests = 0;    
    let filteredRequests = 0;
    let requestsPerSec = (processedRequests / runtime).toFixed(2);
  
    onMount(async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/crawler/results');
        const metricsRes = await fetch('http://127.0.0.1:8000/api/crawler/metrics');

        if (metricsRes.ok) {
          const metricsData = await metricsRes.json();
          runtime = metricsData.running_time ?? 0;
          processedRequests = metricsData.processed_requests ?? 0;
          filteredRequests = metricsData.filtered_requests ?? 0;
          requestsPerSec = metricsData.requests_per_second?.toFixed(2) ?? "0.00";
        }

        if (res.ok) {
          const data = await res.json();
          results = data;
        } else {
          console.error("Failed to fetch CSV results");
        }
      } catch (err) {
        console.error("Error loading results:", err);
      }
    });
  
    function restartCrawl() {
      goto("/tools/crawler/") 
    }
  
    function exportResults() {
      if (results.length === 0) {
        alert("No results to export.");
        return;
      }

      // Build CSV content
      let csvContent = "data:text/csv;charset=utf-8," 
          + "ID,URL,Title,WordCount,CharCount,LinksFound,Error\n"
          + results.map(r => 
              `${r.id ?? ''},${r.URL ?? ''},${r.Title ?? ''},${r.WordCount ?? 0},${r.CharCount ?? 0},${r.LinksFound ?? 0},${r.Error ?? ''}`
            ).join("\n");

      // Create download link
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", "crawl_results.csv");
      document.body.appendChild(link);

      // Auto-click the link to trigger download
      link.click();

      // Clean up
      document.body.removeChild(link);
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
  
    .table-wrapper {
      display: flex;
      justify-content: center;
      padding: 0 20px;
      overflow-x: auto;
      overflow-y: auto;
      max-height: min(50vh, 500px);
    }

    table {
      width: 100%;
      max-width: 1200px;
      border-collapse: collapse;
      margin: 0 auto;
      border-radius: 10px;
      overflow: hidden;
      border: none;
    }
  
    th, td {
      border: none;
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

    thead th {
      position: sticky;
      top: 0;
      background-color: #9BC2CB;
      z-index: 2;
      border: none;
    }

    tbody tr:nth-child(even) {
      background-color: #0000001c;
    }

    tbody tr:nth-child(odd) {
      background-color: white;
    }
  </style>
  
  <div class="main">
    <h2>Crawler</h2>
    <p style="margin: 0 0 20px 0; font-size: 14px;">Results</p>
  
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
  
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>URL</th>
            <th>Title</th>
            <th>Word Count</th>
            <th>Character Count</th>
            <th>Links Found</th>
            <th>Error </th>
          </tr>
        </thead>
        <tbody>
          {#each results as row, i}
            <tr>
              <td>{row.id ?? ''}</td>
              <td>{row.URL ?? ''}</td>
              <td>{row.Title ?? ''}</td>
              <td>{row.WordCount ?? 0}</td>
              <td>{row.CharCount ?? 0}</td>
              <td>{row.LinksFound ?? 0}</td>
              <td>{row.Error ? row.Error : 'False'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  
    <div class="button-container">
      <div>
        <button on:click={restartCrawl}>Restart</button>
        <button on:click={exportResults}>Export |→</button>
      </div>
    </div>
  </div>