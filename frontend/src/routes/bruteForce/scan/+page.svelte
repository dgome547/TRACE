
<script>
    import { onMount, onDestroy } from 'svelte';
    import { goto } from '$app/navigation';
    /**
    26.	Brute Force Scan Page
    [SRS 3.2.3.1- 26a] When the “Pause” button is clicked, the system shall temporarily halt the brute force test while retaining the current state.
    [SRS 3.2.3.1– 26b] When the “Stop” button is clicked, the system shall terminate the brute force process and allow users to review partial results on the “Result” page. (as shown in Section 3.2.3.1.28) 
    [SRS 3.2.3.1– 26c] When the “Restart” button is clicked, the system shall clear all current progress and results. The user shall be navigated back to the “Configuration” page to reconfigure and initiate a new Brute Force Scan. (as shown in Section 3.2.3.1.26) 
    [SRS 3.2.3.1- 26d] When selecting the “Show Terminal” button, the system shall display a raw log of the brute force process, including detailed request and response data.
    */
    
    // Component imports - comment these out if you don't have them
    import Slider from "$lib/components/Slider.svelte";
    import Button from "$lib/components/Button.svelte";

    // Scan state management mostly hardcoded for demo purposes
    let isScanning = true;
    let isPaused = false;
    let progress = 0; // Initial progress value (0-100)
    let elapsedTime = "00:05:24";
    let estimatedTimeRemaining = "00:08:47";
    let attemptsMade = 1249;
    let successfulAttempts = 3;
    
    // Terminal log management
    let showTerminal = false;
    let terminalLogs = [
      "[INFO] Starting brute force scan at 14:25:32",
      "[REQUEST] POST /auth - User: admin123, Pass: password123",
      "[RESPONSE] Status: 401 Unauthorized",
      "[REQUEST] POST /auth - User: admin123, Pass: password124",
      "[RESPONSE] Status: 401 Unauthorized",
      "[REQUEST] POST /auth - User: admin123, Pass: letmein",
      "[RESPONSE] Status: 200 OK - Authentication successful",
      "[INFO] Credential found: admin123:letmein",
      "[REQUEST] POST /auth - User: user456, Pass: password123",
      "[RESPONSE] Status: 401 Unauthorized"
    ];
    
    let progressInterval;
    
    onMount(() => {
      // Start progress simulation when component mounts
      startProgressUpdate();
    });
    
    onDestroy(() => {
      // Clean up interval when component is destroyed
      if (progressInterval) {
        clearInterval(progressInterval);
      }
    });
    
    // SRS 3.2.3.1-26a: Pause functionality
    function handlePause() {
      isPaused = !isPaused;
      if (isPaused) {
        isScanning = false;
        // Stop the progress update
        if (progressInterval) {
          clearInterval(progressInterval);
          progressInterval = null;
        }
      } else {
        isScanning = true;
        // Resume the progress update
        startProgressUpdate();
      }
    }
    
    // SRS 3.2.3.1-26b: Stop functionality
    function handleStop() {
      isScanning = false;
      isPaused = false;
      if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
      }
      // TODO Logic to terminate the process TODO
      // Navigate to results page
      goto('/bruteForce/results');    
    }
    
    // SRS 3.2.3.1-26c: Restart functionality
    function handleRestart() {
      // Clear all progress and results
      isScanning = false;
      isPaused = false;
      progress = 0;
      attemptsMade = 0;
      successfulAttempts = 0;
      if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
      }
      // Navigate back to configuration page
      goto('/bruteForce/configuration');    
    
    }
    
    // SRS 3.2.3.1-26d: Show Terminal functionality
    function toggleTerminal() {
      showTerminal = !showTerminal;
    }
    
    // Function to start progress updates
    function startProgressUpdate() {
      if (!progressInterval) {
        progressInterval = setInterval(() => {
          if (isScanning && !isPaused && progress < 100) {
            progress += 0.5;
            attemptsMade += 3;
            if (Math.round(progress) % 10 === 0) {
              successfulAttempts += 1;
              terminalLogs = [...terminalLogs, `[INFO] New credential found at ${new Date().toLocaleTimeString()}`];
            }
          } else if (progress >= 100) {
            clearInterval(progressInterval);
            progressInterval = null;
          }
        }, 1000);
      }
    }
  </script>
  
  <style>
    .main {
      margin-left: 70px;
      padding: 40px;
      font-family: Arial, sans-serif;
      height: 100vh;
    }
  
    h2 {
      font-size: 28px;
      margin-bottom: 30px;
    }
  
    h3 {
      font-size: 18px;
      margin-bottom: 15px;
    }
  
    .section {
      margin-bottom: 40px;
    }
  
    .stats-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 30px;
    }
  
    .stat-box {
      background-color: #f5f5f5;
      padding: 15px;
      border-radius: 5px;
    }
  
    .stat-label {
      font-size: 14px;
      color: #666;
    }
  
    .stat-value {
      font-size: 20px;
      font-weight: bold;
      margin-top: 5px;
    }
  
    .progress-section {
      margin-bottom: 30px;
    }
    
    .progress-bar {
      height: 20px;
      background-color: #eee;
      border-radius: 10px;
      overflow: hidden;
      margin-bottom: 5px;
    }
    
    .progress-fill {
      height: 100%;
      background-color: var(--primary, #4CAF50);
      width: 0%;
      transition: width 0.3s ease;
    }
  
    .progress-value {
      text-align: right;
      font-size: 14px;
      color: #666;
    }
  
    .actions {
      display: flex;
      gap: 15px;
      margin-top: 30px;
    }
  
    .terminal {
      background-color: #000;
      color: #0f0;
      font-family: monospace;
      padding: 15px;
      height: 300px;
      overflow-y: auto;
      border-radius: 5px;
      margin-top: 20px;
    }
  
    .terminal-line {
      margin-bottom: 5px;
      word-break: break-all;
    }
  
    button {
      background-color: var(--primary, #4CAF50);
      border: none;
      border-radius: 5px;
      padding: 12px 25px;
      font-size: 16px;
      cursor: pointer;
      color: white;
    }
  
    .pause-button {
      background-color: #FFA500;
    }
  
    .stop-button {
      background-color: #FF6347;
    }
  
    .restart-button {
      background-color: #4682B4;
    }
  
    .terminal-button {
      background-color: #333;
    }
  </style>
  
  <div class="main">
    <h2>Brute Force Scan</h2>
  
    <!-- Progress Section -->
    <div class="progress-section">
      <h3>Progress</h3>
      <!-- Custom progress bar -->
      <div class="progress-bar">
        <div class="progress-fill" style="width: {progress}%"></div>
      </div>
      <div class="progress-value">{progress.toFixed(1)}%</div>
    </div>
  
    <!-- Stats Section -->
    <div class="stats-container">
      <div class="stat-box">
        <div class="stat-label">Elapsed Time</div>
        <div class="stat-value">{elapsedTime}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Estimated Time Remaining</div>
        <div class="stat-value">{estimatedTimeRemaining}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Attempts Made</div>
        <div class="stat-value">{attemptsMade}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Successful Attempts</div>
        <div class="stat-value">{successfulAttempts}</div>
      </div>
    </div>
  
    <!-- Action Buttons -->
    <div class="actions">
      <!-- SRS 3.2.3.1-26a: Pause button -->
      <button 
        class="pause-button" 
        on:click={handlePause}
      >
        {isPaused ? "Resume" : "Pause"}
      </button>
      
      <!-- SRS 3.2.3.1-26b: Stop button -->
      <button 
        class="stop-button" 
        on:click={handleStop}
      >
        Stop
      </button>
      
      <!-- SRS 3.2.3.1-26c: Restart button -->
      <button 
        class="restart-button" 
        on:click={handleRestart}
      >
        Restart
      </button>
      
      <!-- SRS 3.2.3.1-26d: Show Terminal button -->
      <button 
        class="terminal-button" 
        on:click={toggleTerminal}
      >
        {showTerminal ? "Hide Terminal" : "Show Terminal"}
      </button>
    </div>
  
    <!-- Terminal Log Section (toggleable) -->
    {#if showTerminal}
      <div class="section">
        <h3>Terminal Log</h3>
        <div class="terminal">
          {#each terminalLogs as log}
            <div class="terminal-line">{log}</div>
          {/each}
        </div>
      </div>
    {/if}
  </div>