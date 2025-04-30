<script>
    import { onMount, onDestroy} from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { fuzzerResultStore } from '$lib/stores/fuzzerResultStore';
    import { fuzzerConfigStore } from '$lib/stores/fuzzerConfigStore'; 
  
    // Subscribe to stores
    let resultData;
    let configData;
    let scanInProgress = false;
    let scanStarted = false;
    
    $: {
      resultData = $fuzzerResultStore;
      configData = $fuzzerConfigStore;
      
      // Automatically trigger scan when config data changes and scan hasn't started
      if (configData && !scanStarted && !scanInProgress) {
        console.log("Config data changed, starting fuzzing");
        startFuzzing();
      }
    }
    
    // Extract data from the correct structure
    $: results = resultData?.results || [];
    $: stats = resultData?.metrics || {};
    $: status = resultData?.status || "";
    
    // Extract stats data for display
    $: summaryMetrics = {
      runningTime: stats.running_time || "0m 0s",
      processedRequests: stats.processed_requests || 0,
      filteredRequests: stats.filtered_requests || 0,
      requestsPerSec: stats.requests_per_sec || 0,
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
        status_code: result.status_code,
        lines: result.lines,
        words: result.words,
        chars: result.chars,
        payload: result.payload,
        content_length: result.content_length,
        response_time: result.response_time || 0,
        response_time_display: (result.response_time?.toFixed(3) || "0.000") + "s",
        error: result.error
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
      `[INFO] Request #${result.id} - ${result.timestamp || 'Unknown time'}`,
      `[REQUEST] ${configData?.http_method || 'GET'} ${result.url || 'Unknown URL'}`,
      `[RESPONSE] Status: ${result.status_code}, Time: ${result.response_time?.toFixed(3) || 0}s, Length: ${result.content_length}`,
      result.error === "true" ? `[ERROR] Request failed` : ''
    ]).flat().filter(Boolean);
  
    // Perform the API call with the config data
    async function startFuzzing() {
      console.log("Starting fuzzing with config:", configData);
      
      if (!configData) {
        console.error("No configuration data available");
        alert("No configuration data available. Please go back to the configuration page.");
        goto('/fuzzer/config');
        return;
      }
  
      // Set flags to prevent multiple calls
      scanInProgress = true;
      scanStarted = true;
      
      console.log("Fuzzing in progress:", scanInProgress);
  
      const formData = new FormData();
      formData.append("target_url", configData.target_url);
  
      if (typeof configData.wordlist_file === 'object') {
        formData.append("wordlist_file", configData.wordlist_file);
        console.log("Added wordlist file to request");
      } else {
        console.warn("Wordlist file is not an object:", configData.wordlist_file);
      }
  
      formData.append("http_method", configData.http_method);
      formData.append("request_timeout", "5.0"); // Default timeout
      
      // Convert simple fields to strings for FormData
      if (configData.hide_status) {
        formData.append("hide_status", configData.hide_status);
      }
      
      if (configData.show_only_status) {
        formData.append("show_only_status", configData.show_only_status);
      }
      
      if (configData.filter_by_content_length) {
        formData.append("filter_by_content_length", configData.filter_by_content_length);
      }
      
      // Add cookies and additional parameters
      if (configData.cookies) {
        formData.append("cookies", configData.cookies);
      }
      
      if (configData.additional_parameters) {
        formData.append("additional_parameters", configData.additional_parameters);
      }
      
      console.log("FormData prepared, making API call...");
      
      try {
        // Make sure the DOM has been updated to show scanning status
        await new Promise(resolve => setTimeout(resolve, 0));
        
        console.log("Sending API request to:", "http://localhost:5000/api/fuzzer/scan");
        const res = await fetch("http://localhost:5000/api/fuzzer/scan", {
          method: "POST",
          body: formData
        });
  
        console.log("API response received, status:", res.status);
  
        if (!res.ok) { 
          const error = await res.text();
          throw new Error(`Server Error ${res.status}: ${error}`);
        }
  
        const result = await res.json();
        console.log("Fuzzing Result:", result);
        
        // Update the result store with the API response
        fuzzerResultStore.set(result);
      } catch (err) {
        console.error("Fuzzing error:", err);
        alert("Error starting fuzzing:\n\n" + err.message);
      } finally {
        console.log("Fuzzing completed, setting scanInProgress to false");
        scanInProgress = false;
      }
    }
    
    // Restart functionality
    function handleRestart() {
      // Clear results and navigate to configuration page
      goto('/fuzzer/config');    
    }
    
    // Export functionality
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
      const filename = `fuzzer-results-${timestamp}.json`;
      
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
    
    // Show Terminal functionality
    function toggleTerminal() {
      showTerminal = !showTerminal;
    }
  
    // Start scan when component mounts if there's config data
    onMount(async () => {
      console.log("Fuzzer results page mounted, config data:", configData);
      if (configData && !scanStarted) {
        // Start fuzzing immediately when the component mounts
        await startFuzzing();
      }
    });
  
    import '../fuzzer.css';
  </script>
  
  
  <div class="main">
    <div class="header">
      <h1>
        Parameter Fuzzer
        {#if status}
          <span class={`status-indicator status-${status}`}>{status}</span>
        {:else if scanInProgress}
          <span class="status-indicator status-running">Running</span>
        {/if}
      </h1>
    </div>
  
    <div class="navigation">
      <div class="nav-item" on:click={() => goto('/fuzzer/config')}>Configuration</div>
      <div class="nav-item" class:active={scanInProgress}>Running</div>
      <div class="nav-item" class:active={!scanInProgress}>Results</div>
    </div>
  
    {#if scanInProgress}
      <div class="scan-progress">
        <p>Fuzzing in progress...</p>
        <div class="spinner"></div>
        <p class="scan-details">Running fuzzing for: {configData?.target_url || 'Unknown target'}</p>
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
            <th on:click={() => handleSort('status_code')} class={sortField === 'status_code' ? `sorted-${sortDirection}` : ''}>
              Response {sortField === 'status_code' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
            <th on:click={() => handleSort('lines')} class={sortField === 'lines' ? `sorted-${sortDirection}` : ''}>
              Lines {sortField === 'lines' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
            <th on:click={() => handleSort('words')} class={sortField === 'words' ? `sorted-${sortDirection}` : ''}>
              Words {sortField === 'words' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
            <th on:click={() => handleSort('chars')} class={sortField === 'chars' ? `sorted-${sortDirection}` : ''}>
              Chars {sortField === 'chars' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
            <th on:click={() => handleSort('payload')} class={sortField === 'payload' ? `sorted-${sortDirection}` : ''}>
              Payload {sortField === 'payload' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
            <th on:click={() => handleSort('content_length')} class={sortField === 'content_length' ? `sorted-${sortDirection}` : ''}>
              Length {sortField === 'content_length' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
            <th on:click={() => handleSort('response_time')} class={sortField === 'response_time' ? `sorted-${sortDirection}` : ''}>
              Time {sortField === 'response_time' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
          </tr>
        </thead>
        <tbody>
          {#each requestDetails as detail}
            <tr>
              <td>{detail.id}</td>
              <td class={`response-${detail.status_code}`}>{detail.status_code}</td>
              <td>{detail.lines}</td>
              <td>{detail.words}</td>
              <td>{detail.chars}</td>
              <td>{detail.payload}</td>
              <td>{detail.content_length}</td>
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
          <p>Fuzzing complete, but no results were returned.</p>
          <button class="restart-button" on:click={startFuzzing}>
            Try Again
          </button>
        {:else}
          <p>Ready to start fuzzing with the provided configuration.</p>
          <button class="start-button" on:click={startFuzzing}>Start Fuzzing Now</button>
          <p class="scan-note">The fuzzing should start automatically. If it doesn't, click the button above.</p>
        {/if}
      </div>
    {/if}
  
    <!-- Action Buttons -->
    <div class="actions">
      <div class="left-actions">
        <!-- Restart button -->
        <button class="restart-button" on:click={handleRestart} disabled={!resultData || results.length === 0}>
          Restart
        </button>
        
        <!-- Export button -->
        <button class="export-button" on:click={handleExport} disabled={!resultData || results.length === 0}>
          Export ↗
        </button>
      </div>
      
      <div class="right-actions">
        <!-- Show Terminal button -->
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