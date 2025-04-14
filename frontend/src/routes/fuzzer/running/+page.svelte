<script>
	import { goto } from '$app/navigation';
    import { onMount, onDestroy } from 'svelte';
    import { fade } from 'svelte/transition';
    
    // Mock data for demonstration purposes
    let progress = 95;
    let status = "Scanning...";
    let runningTime = 75.036;
    let processedRequests = 352;
    let filteredRequests = 59;
    let requestsPerSec = 0.345;
    
    let tableData = [
      { id: 45, response: 200, lines: 0, word: 1, chars: 30, payload: "auto", length: 0.541, error: false },
      { id: 46, response: 200, lines: 0, word: 1, chars: 30, payload: "root", length: 0.526, error: false },
      { id: 47, response: 200, lines: 0, word: 1, chars: 30, payload: "guest", length: 0.468, error: false },
      { id: 48, response: 200, lines: 0, word: 109, chars: 1491, payload: "info", length: 0.552, error: false },
      { id: 49, response: 200, lines: 0, word: 49, chars: 703, payload: "test", length: 0.527, error: false },
      { id: 50, response: 200, lines: 0, word: 1, chars: 30, payload: "user", length: 0.492, error: false },
      { id: 51, response: 200, lines: 0, word: 1, chars: 30, payload: "NULL", length: 0.631, error: false },
      { id: 52, response: 200, lines: 0, word: 1, chars: 30, payload: "undefined", length: 0.533, error: false }
    ];
    
    // Column tooltips
    const columnTooltips = {
      id: "Unique identifier for each request",
      response: "HTTP response code returned",
      lines: "Number of lines in the response",
      word: "Number of words in the response",
      chars: "Number of characters in the response",
      payload: "The input tested for vulnerabilities",
      length: "Response time in seconds",
      error: "Whether the request resulted in an error"
    };
    
    let showConfirmationDialog = false;
    let intervalId;
    
    // Simulate real-time updates for the progress bar
    onMount(() => {
      intervalId = setInterval(() => {
        if (progress < 100) {
          progress += 0.5;
          runningTime += 0.25;
          processedRequests += 1;
          if (Math.random() > 0.8) filteredRequests += 1;
          requestsPerSec = (processedRequests / runningTime).toFixed(3);
        } else {
          status = "Completed";
          clearInterval(intervalId);
          goto('/fuzzer/results'); // Redirect to results page when completed
        }
      }, 1000);
    });
    
    onDestroy(() => {
      if (intervalId) clearInterval(intervalId);
    });
    
    //[SRS 23.3] 
    function handleStop() {
      showConfirmationDialog = true;
    }
    
    function confirmStop() {
      clearInterval(intervalId);
      status = "Stopped";
      showConfirmationDialog = false;
    }
    
    function cancelStop() {
      showConfirmationDialog = false;
    }
    
    function handleRestart() {
      progress = 0;
      status = "Scanning...";
      runningTime = 0;
      processedRequests = 0;
      filteredRequests = 0;
      requestsPerSec = 0;
      
      clearInterval(intervalId);
      intervalId = setInterval(() => {
        if (progress < 100) {
          progress += 0.5;
          runningTime += 0.25;
          processedRequests += 1;
          if (Math.random() > 0.8) filteredRequests += 1;
          requestsPerSec = (processedRequests / runningTime).toFixed(3);
        } else {
          status = "Completed";
          clearInterval(intervalId);
        }
      }, 1000);
    }
  </script>
    <style>
    @import './running.css';
    </style>
  
  <div class="parameter-fuzzing-container">
    <link rel="stylesheet" href="running.css">    
    <header>
      <h1>Parameter Fuzzing</h1>
      <div class="subtext">Running</div>
      
      <!-- Steps indicator -->
      <div class="steps-container">
        <div class="step completed">
          <div class="step-circle">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
          </div>
          <span>Configuration</span>
        </div>
        <div class="connector completed"></div>
        <div class="step active">
          <div class="step-circle">•</div>
          <span>Running</span>
        </div>
        <div class="connector"></div>
        <div class="step">
          <div class="step-circle">•</div>
          <span>Results</span>
        </div>
      </div>
    </header>
    
    <div class="progress-section">
      <div class="progress-indicator">
        <div class="progress-circle">
          <svg viewBox="0 0 36 36">
            <path
              class="progress-bg"
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              class="progress-value"
              stroke-dasharray="{progress}, 100"
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <div class="progress-text">{progress}%</div>
        </div>
        <div class="progress-status">{status}</div>
      </div>
      
      <div class="progress-bar">
        <div class="progress-inner" style="width: {progress}%"></div>
      </div>
    </div>
    
    <div class="metrics-container">
      <div class="metric">
        <h3>Running Time</h3>
        <div class="value">{runningTime.toFixed(3)}</div>
      </div>
      <div class="metric">
        <h3>Processed Requests</h3>
        <div class="value">{processedRequests}</div>
      </div>
      <div class="metric">
        <h3>Filtered Requests</h3>
        <div class="value">{filteredRequests}</div>
      </div>
      <div class="metric">
        <h3>Requests/sec.</h3>
        <div class="value">{requestsPerSec}</div>
      </div>
    </div>
    
    <div class="table-container">
      <table>
        <thead>
          <tr>
            {#each Object.keys(tableData[0]) as column}
              <th title={columnTooltips[column]}>
                {column === 'id' ? 'ID' : column.charAt(0).toUpperCase() + column.slice(1)}
              </th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each tableData as row}
            <tr>
              <td>{row.id}</td>
              <td>{row.response}</td>
              <td>{row.lines} L</td>
              <td>{row.word} W</td>
              <td>{row.chars}</td>
              <td>{row.payload}</td>
              <td>{row.length}</td>
              <td>{row.error ? 'True' : 'False'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    
    <div class="button-group">
      <button class="btn pause-btn">Pause</button>
      <button class="btn stop-btn" on:click={handleStop}>Stop</button>
      <button class="btn restart-btn" on:click={handleRestart}>Restart</button>
      <div class="spacer"></div>
      <button class="btn terminal-btn">Show Terminal</button>
    </div>
    
    {#if showConfirmationDialog}
      <div class="confirmation-dialog-backdrop" transition:fade>
        <div class="confirmation-dialog">
          <h3>Confirm Stop</h3>
          <p>Are you sure you want to stop the current scan? This action cannot be undone.</p>
          <div class="dialog-buttons">
            <button class="btn cancel-btn" on:click={cancelStop}>Cancel</button>
            <button class="btn confirm-btn" on:click={confirmStop}>Stop Scan</button>
          </div>
        </div>
      </div>
    {/if}
  </div>
  
  