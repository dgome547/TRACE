<script>
    /**
     * 27.	Brute Force Results Page
    [SRS 3.2.3.1- 27a] When the “Restart” button is clicked, the system shall clear all current progress and results. The user shall be navigated back to the “Configuration” page to reconfigure and initiate a new Brute Force scan. (as shown in Section 3.2.3.1.26)
    [SRS 3.2.3.1- 27b] When the “Export” button is clicked, the system shall generate a downloadable file containing the brute force test results in a standardized format.
    [SRS 3.2.3.1– 27c] When selecting the “Show Terminal” button, the system shall provide a raw output log of the test, including all sent requests and received responses.
     * 
    */
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    
    // Mock test results data
    let scanResults = {
      scanId: "BF-2025-04-02-143721",
      startTime: "2025-04-02 14:37:21",
      endTime: "2025-04-02 14:52:45",
      duration: "00:15:24",
      targetUrl: "https://example.com/login",
      totalAttempts: 3752,
      successfulAttempts: 8,
      completionPercentage: 100
    };


    //---AI GENERATED DEMO RESULTS------------------------------------------------------------------
    // Discovered credentials
    let discoveredCredentials = [
      { username: "admin", password: "admin123", timeFound: "14:38:02", responseTime: "212ms" },
      { username: "admin", password: "password123", timeFound: "14:39:17", responseTime: "198ms" },
      { username: "user123", password: "letmein", timeFound: "14:41:33", responseTime: "223ms" },
      { username: "guest", password: "guest", timeFound: "14:42:55", responseTime: "187ms" },
      { username: "testuser", password: "test123", timeFound: "14:44:12", responseTime: "204ms" },
      { username: "demo", password: "demo2025", timeFound: "14:46:38", responseTime: "195ms" },
      { username: "john.doe", password: "jd1234", timeFound: "14:49:21", responseTime: "210ms" },
      { username: "support", password: "support2025", timeFound: "14:51:47", responseTime: "189ms" }
    ];
    
    // Terminal log management
    let showTerminal = false;
    let terminalLogs = [
      "[INFO] Starting brute force scan at 14:37:21",
      "[REQUEST] POST /auth - User: admin, Pass: admin",
      "[RESPONSE] Status: 401 Unauthorized",
      "[REQUEST] POST /auth - User: admin, Pass: admin123",
      "[RESPONSE] Status: 200 OK - Authentication successful",
      "[INFO] Credential found: admin:admin123",
      "[REQUEST] POST /auth - User: admin, Pass: password",
      "[RESPONSE] Status: 401 Unauthorized",
      "[REQUEST] POST /auth - User: admin, Pass: password123",
      "[RESPONSE] Status: 200 OK - Authentication successful",
      "[INFO] Credential found: admin:password123",
      // Additional log entries would continue here...
      "[INFO] Brute force scan completed at 14:52:45"
    ];
    //-----------------------------------------------------------------------------------------------
    
    
    // SRS 3.2.3.1-27a: Restart functionality
    function handleRestart() {
      // Clear results and navigate to configuration page
      goto('/bruteForce/configuration');    
    }
    
    // SRS 3.2.3.1-27b: Export functionality
    function handleExport() {
      // Create export data
      const exportData = {
        scanSummary: scanResults,
        discoveredCredentials: discoveredCredentials,
        terminalLogs: terminalLogs
      };
      
      // Convert to JSON string
      const jsonData = JSON.stringify(exportData, null, 2);
      
      // Create a blob and download link
      const blob = new Blob([jsonData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      // Create download link and trigger click
      const a = document.createElement('a');
      a.href = url;
      a.download = `brute-force-results-${scanResults.scanId}.json`;
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
    
    // Export to CSV function (alternative export format)
    function exportToCsv() {
      // CSV header
      let csvContent = "Username,Password,Time Found,Response Time\n";
      
      // Add each credential as a row
      discoveredCredentials.forEach(cred => {
        csvContent += `${cred.username},${cred.password},${cred.timeFound},${cred.responseTime}\n`;
      });
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `credentials-${scanResults.scanId}.csv`;
      document.body.appendChild(a);
      a.click();
      
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 0);
    }
  </script>
  
  <style>
    .main {
      margin-left: 70px;
      padding: 40px;
      font-family: Arial, sans-serif;
      height: 100vh;
      overflow-y: auto;
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
  
    .summary-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 30px;
    }
  
    .summary-box {
      background-color: #f5f5f5;
      padding: 15px;
      border-radius: 5px;
    }
  
    .summary-label {
      font-size: 14px;
      color: #666;
    }
  
    .summary-value {
      font-size: 18px;
      font-weight: bold;
      margin-top: 5px;
    }
  
    .actions {
      display: flex;
      gap: 15px;
      margin: 30px 0;
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
  
    .restart-button {
      background-color: #4682B4;
    }
  
    .export-button {
      background-color: #228B22;
    }
  
    .export-csv-button {
      background-color: #9370DB;
    }
  
    .terminal-button {
      background-color: #333;
    }
  
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
    }
  
    th {
      background-color: #f0f0f0;
      text-align: left;
      padding: 12px;
      font-weight: bold;
      border-bottom: 2px solid #ddd;
    }
  
    td {
      padding: 10px 12px;
      border-bottom: 1px solid #ddd;
    }
  
    tr:nth-child(even) {
      background-color: #f9f9f9;
    }
  
    tr:hover {
      background-color: #f1f1f1;
    }
  
    .success-count {
      font-size: 24px;
      font-weight: bold;
      color: #228B22;
      margin-bottom: 15px;
    }
  </style>
  
  <div class="main">
    <h2>Brute Force Scan Results</h2>
  
    <!-- Scan Success Summary -->
    <div class="section">
      <div class="success-count">
        {scanResults.successfulAttempts} Credentials Discovered
      </div>
    </div>
  
    <!-- Scan Summary Section -->
    <div class="section">
      <h3>Scan Summary</h3>
      <div class="summary-container">
        <div class="summary-box">
          <div class="summary-label">Scan ID</div>
          <div class="summary-value">{scanResults.scanId}</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">Target URL</div>
          <div class="summary-value">{scanResults.targetUrl}</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">Start Time</div>
          <div class="summary-value">{scanResults.startTime}</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">End Time</div>
          <div class="summary-value">{scanResults.endTime}</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">Duration</div>
          <div class="summary-value">{scanResults.duration}</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">Total Attempts</div>
          <div class="summary-value">{scanResults.totalAttempts.toLocaleString()}</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">Successful Attempts</div>
          <div class="summary-value">{scanResults.successfulAttempts}</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">Completion</div>
          <div class="summary-value">{scanResults.completionPercentage}%</div>
        </div>
      </div>
    </div>
  
    <!-- Action Buttons -->
    <div class="actions">
      <!-- SRS 3.2.3.1-27a: Restart button -->
      <button 
        class="restart-button" 
        on:click={handleRestart}
      >
        Restart
      </button>
      
      <!-- SRS 3.2.3.1-27b: Export buttons -->
      <button 
        class="export-button" 
        on:click={handleExport}
      >
        Export JSON
      </button>
      
      <button 
        class="export-csv-button" 
        on:click={exportToCsv}
      >
        Export CSV
      </button>
      
      <!-- SRS 3.2.3.1-27c: Show Terminal button -->
      <button 
        class="terminal-button" 
        on:click={toggleTerminal}
      >
        {showTerminal ? "Hide Terminal" : "Show Terminal"}
      </button>
    </div>
  
    <!-- Discovered Credentials Section -->
    <div class="section">
      <h3>Discovered Credentials</h3>
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Password</th>
            <th>Time Found</th>
            <th>Response Time</th>
          </tr>
        </thead>
        <tbody>
          {#each discoveredCredentials as credential}
            <tr>
              <td>{credential.username}</td>
              <td>{credential.password}</td>
              <td>{credential.timeFound}</td>
              <td>{credential.responseTime}</td>
            </tr>
          {/each}
        </tbody>
      </table>
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