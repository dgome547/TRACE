<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { resultStore } from '$lib/stores/resultStore';

  // Subscribe to result store
  let resultData;
  $: resultData = $resultStore;
  
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

  import './results.css';

</script>


<div class="main">
  <div class="header">
    <h1>
      Brute Force
      {#if status}
        <span class={`status-indicator status-${status}`}>{status}</span>
      {/if}
    </h1>
  </div>

  <div class="navigation">
    <div class="nav-item">Configuration</div>
    <div class="nav-item">Running</div>
    <div class="nav-item active">Results</div>
  </div>

  {#if resultData && results.length > 0}
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
  {:else}
    <div class="empty-state">No results data available. Please run a brute force scan first.</div>
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
  /* Add these styles to your results.css file or include them here */
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
</style>