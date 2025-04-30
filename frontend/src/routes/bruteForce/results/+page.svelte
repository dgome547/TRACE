<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { resultStore } from '$lib/stores/resultStore';
  import { configStore } from '$lib/stores/configStore'; // Import the config store

  // Subscribe to stores
  let resultData;
  let configData;
  let scanInProgress = false;
  let scanStarted = false;
  
  $: {
    resultData = $resultStore;
    configData = $configStore;
    
    // Automatically trigger scan when config data changes and scan hasn't started
    if (configData && !scanStarted && !scanInProgress) {
      console.log("Config data changed, starting scan");
      startScan();
    }
  }
  
  // Extract data from the correct structure
  $: results = resultData?.results || [];
  $: stats = resultData?.stats || {};
  $: status = resultData?.status || "";
  
  // Extract stats data for display
  $: summaryMetrics = {
    runningTime: stats.raw_running_time?.toFixed(3) || "0.000",
    processedRequests: stats.processed_requests || 0,
    filteredRequests: stats.filtered_requests || 0,
    requestsPerSec: stats.requests_per_second?.toFixed(3) || "0.000"
  };

  // Sorting functionality
  let sortField = 'id'; // Default sort field
  let sortDirection = 'asc'; // Default sort direction (ascending)

  // Handle column header click for sorting
  function handleSort(field) {
    if (sortField === field) {
      // If already sorting by this field, toggle direction
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      // New field, set to ascending by default
      sortField = field;
      sortDirection = 'asc';
    }
  }

  // Format and sort request details for the table
  $: requestDetails = [...results]
    .map(result => ({
      id: result.id,
      response: result.status_code,
      lines: result.line_count,
      linesDisplay: `${result.line_count} L`,
      word: result.word_count,
      wordDisplay: `${result.word_count} W`,
      chars: result.char_count,
      payload: result.payload,
      response_time: result.response_time || 0,
      response_time_display: result.response_time?.toFixed(3) || "0.000"
    }))
    .sort((a, b) => {
      let valueA = a[sortField];
      let valueB = b[sortField];
      
      // Handle numeric comparison
      if (typeof valueA === 'number' && typeof valueB === 'number') {
        return sortDirection === 'asc' 
          ? valueA - valueB 
          : valueB - valueA;
      }
      
      // Handle string comparison
      if (typeof valueA === 'string' && typeof valueB === 'string') {
        return sortDirection === 'asc'
          ? valueA.localeCompare(valueB)
          : valueB.localeCompare(valueA);
      }
      
      // Fallback for mixed types
      return sortDirection === 'asc'
        ? String(valueA).localeCompare(String(valueB))
        : String(valueB).localeCompare(String(valueA));
    });
  
  // Show terminal toggle functionality
  let showTerminal = false;
  
  // Create terminal logs from results
  $: terminalLogs = results.map(result => [
    `[INFO] Request #${result.id} - ${result.timestamp}`,
    `[REQUEST] GET ${result.url}`,
    `[RESPONSE] Status: ${result.status_code}, Time: ${result.response_time?.toFixed(3)}s, Length: ${result.content_length}`,
    result.error ? `[ERROR] ${result.error}` : ''
  ]).flat().filter(Boolean);

  // Perform the API call with the config data
  async function startScan() {
    console.log("Starting scan with config:", configData);
    
    if (!configData) {
      console.error("No configuration data available");
      alert("No configuration data available. Please go back to the configuration page.");
      goto('/bruteForce');
      return;
    }

    // Set flags to prevent multiple calls
    scanInProgress = true;
    scanStarted = true;
    
    console.log("Scan in progress:", scanInProgress);

    const formData = new FormData();
    formData.append("target_url", configData.target_url);

    if (typeof configData.wordlist_file === 'object') {
      formData.append("wordlist_file", configData.wordlist_file);
      console.log("Added wordlist file to request");
    } else {
      console.warn("Wordlist file is not an object:", configData.wordlist_file);
    }

    formData.append("max_concurrent_requests", configData.max_concurrent_requests);
    formData.append("request_timeout", configData.request_timeout);
    formData.append("output_format", configData.output_format);
    formData.append("hide_status", configData.hide_status);
    formData.append("show_only_status", configData.show_only_status);
    formData.append("top_level_directory", configData.top_level_directory);
    formData.append("filter_by_content_length", configData.filter_by_content_length);
    formData.append("additional_parameters", configData.additional_parameters);
    
    console.log("FormData prepared, making API call...");
    
    try {
      // Make sure the DOM has been updated to show scanning status
      await new Promise(resolve => setTimeout(resolve, 0));
      
      console.log("Sending API request to:", "http://localhost:5000/api/bruteforce/scan");
      const res = await fetch("http://localhost:5000/api/bruteforce/scan", {
        method: "POST",
        body: formData
      });

      console.log("API response received, status:", res.status);

      if (!res.ok) { 
        const error = await res.text();
        throw new Error(`Server Error ${res.status}: ${error}`);
      }

      const result = await res.json();
      console.log("Scan Result:", result);
      
      // Update the result store with the API response
      resultStore.set(result);
    } catch (err) {
      console.error("Scan error:", err);
      alert("Error starting scan:\n\n" + err.message);
    } finally {
      console.log("Scan completed, setting scanInProgress to false");
      scanInProgress = false;
    }
  }
  
  // SRS 3.2.3.1-27a: Restart functionality
  function handleRestart() {
    // Clear results and navigate to configuration page
    goto('/bruteForce');    
  }
  
  // SRS 3.2.3.1-27b: Export functionality
  function handleExport() {
    if (!resultData) return;
    
    // Use actual data from store for export
    const exportData = resultData;
    
    // Convert to JSON string
    const jsonData = JSON.stringify(exportData, null, 2);
    
    // Create a blob and download link
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Generate filename with timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `brute-force-results-${timestamp}.json`;
    
    // Create download link and trigger click
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 0);
  }
  
  // SRS 3.2.3.1-27c: Show Terminal functionality
  function toggleTerminal() {
    showTerminal = !showTerminal;
  }

  // Start scan when component mounts if there's config data
  onMount(async () => {
    console.log("Results page mounted, config data:", configData);
    if (configData && !scanStarted) {
      // Start scan immediately when the component mounts
      await startScan();
    }
  });

  import './results.css';
</script>


<div class="main">
  <div class="header">
    <h1>
      Brute Force
      {#if status}
        <span class={`status-indicator status-${status}`}>{status}</span>
      {:else if scanInProgress}
        <span class="status-indicator status-running">Running</span>
      {/if}
    </h1>
  </div>

  <div class="navigation">
    <div class="nav-item">Configuration</div>
    <div class="nav-item">Running</div>
    <div class="nav-item active">Results</div>
  </div>

  {#if scanInProgress}
    <div class="scan-progress">
      <p>Scan in progress...</p>
      <div class="spinner"></div>
      <p class="scan-details">Running scan for: {configData?.target_url || 'Unknown target'}</p>
    </div>
  {:else if resultData && results.length > 0}
    <!-- Summary Metrics -->
    <div class="metrics-container">
      <div class="metric-box">
        <div class="metric-label">Running Time</div>
        <div class="metric-value">{summaryMetrics.runningTime}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Processed Requests</div>
        <div class="metric-value">{summaryMetrics.processedRequests}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Filtered Requests</div>
        <div class="metric-value">{summaryMetrics.filteredRequests}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Requests/sec.</div>
        <div class="metric-value">{summaryMetrics.requestsPerSec}</div>
      </div>
    </div>

    <!-- Request Details Table -->
    <table>
      <thead>
        <tr>
          <th on:click={() => handleSort('id')} class={sortField === 'id' ? `sorted-${sortDirection}` : ''}>
            ID {sortField === 'id' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
          </th>
          <th on:click={() => handleSort('response')} class={sortField === 'response' ? `sorted-${sortDirection}` : ''}>
            Response {sortField === 'response' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
          </th>
          <th on:click={() => handleSort('lines')} class={sortField === 'lines' ? `sorted-${sortDirection}` : ''}>
            Lines {sortField === 'lines' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
          </th>
          <th on:click={() => handleSort('word')} class={sortField === 'word' ? `sorted-${sortDirection}` : ''}>
            Word {sortField === 'word' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
          </th>
          <th on:click={() => handleSort('chars')} class={sortField === 'chars' ? `sorted-${sortDirection}` : ''}>
            Chars {sortField === 'chars' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
          </th>
          <th on:click={() => handleSort('payload')} class={sortField === 'payload' ? `sorted-${sortDirection}` : ''}>
            Payload {sortField === 'payload' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
          </th>
          <th on:click={() => handleSort('response_time')} class={sortField === 'response_time' ? `sorted-${sortDirection}` : ''}>
            Response Time {sortField === 'response_time' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
          </th>
        </tr>
      </thead>
      <tbody>
        {#each requestDetails as detail}
          <tr>
            <td>{detail.id}</td>
            <td class={`response-${detail.response}`}>{detail.response}</td>
            <td>{detail.linesDisplay}</td>
            <td>{detail.wordDisplay}</td>
            <td>{detail.chars}</td>
            <td>{detail.payload}</td>
            <td>{detail.response_time_display}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else if !configData}
    <div class="empty-state">
      No configuration data available. Please go back to the configuration page.
      <button class="restart-button" on:click={handleRestart}>
        Go to Configuration
      </button>
    </div>
  {:else}
    <div class="empty-state">
      {#if scanStarted}
        <p>Scan complete, but no results were returned.</p>
        <button class="restart-button" on:click={startScan}>
          Try Again
        </button>
      {:else}
        <p>Ready to start scan with the provided configuration.</p>
        <button class="start-button" on:click={startScan}>Start Scan Now</button>
        <p class="scan-note">The scan should start automatically. If it doesn't, click the button above.</p>
      {/if}
    </div>
  {/if}

  <!-- Action Buttons -->
  <div class="actions">
    <div class="left-actions">
      <!-- SRS 3.2.3.1-27a: Restart button -->
      <button class="restart-button" on:click={handleRestart}>
        Restart
      </button>
      
      <!-- SRS 3.2.3.1-27b: Export button -->
      <button class="export-button" on:click={handleExport} disabled={!resultData || results.length === 0}>
        Export ↗
      </button>
    </div>
    
    <div class="right-actions">
      <!-- SRS 3.2.3.1-27c: Show Terminal button -->
      <button class="terminal-button" on:click={toggleTerminal} disabled={!resultData || results.length === 0}>
        {showTerminal ? "Hide Terminal" : "Show Terminal"}
      </button>
    </div>
  </div>
  
  <!-- Terminal content shown when toggled -->
  {#if showTerminal && terminalLogs.length > 0}
    <div class="terminal">
      {#each terminalLogs as log}
        <div class="terminal-line">{log}</div>
      {/each}
    </div>
  {/if}
</div>

<style>
  /* Existing styles from results.css */
  th {
    cursor: pointer;
    user-select: none;
    position: relative;
  }
  
  th:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .sorted-asc, .sorted-desc {
    font-weight: bold;
  }
  
  /* Enhanced styles for scan progress */
  .scan-progress {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    margin: 2rem 0;
  }
  
  .scan-details {
    margin-top: 1rem;
    color: #666;
    font-size: 0.9rem;
  }
  
  .scan-note {
    margin-top: 1rem;
    color: #999;
    font-size: 0.8rem;
    font-style: italic;
  }
  
  .spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #7FBFB6;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin-top: 1rem;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .start-button {
    background-color: #7FBFB6;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 30px;
    font-size: 16px;
    cursor: pointer;
    margin-top: 20px;
    transition: background-color 0.2s;
  }
  
  .start-button:hover {
    background-color: #6EAFA6;
  }
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    margin: 2rem 0;
    text-align: center;
  }
  
  .empty-state p {
    margin-bottom: 1rem;
  }
  
  /* Status indicator styles */
  .status-indicator {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.8rem;
    margin-left: 0.5rem;
    color: white;
  }
  
  .status-running {
    background-color: #4A90E2;
  }
  
  .status-completed {
    background-color: #7ED321;
  }
  
  .status-error {
    background-color: #FF3B30;
  }
</style> 