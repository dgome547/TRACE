<script>
	import { goto } from "$app/navigation";

    // Mock data for results
    const runningTime = 143.940;
    const processedRequests = 532;
    const filteredRequests = 82;
    const requestsPerSec = 0.532;
    
    // Mock data for table--------------------------------------------------
    // Table data from the image
    const tableData = [
      { id: 45, response: 200, lines: 0, word: 1, chars: 30, payload: "auto", length: 0.541, error: false },
      { id: 46, response: 200, lines: 0, word: 1, chars: 30, payload: "root", length: 0.526, error: false },
      { id: 47, response: 200, lines: 0, word: 1, chars: 30, payload: "guest", length: 0.468, error: false },
      { id: 48, response: 200, lines: 0, word: 109, chars: 1491, payload: "info", length: 0.552, error: false },
      { id: 54, response: 200, lines: 0, word: 1, chars: 30, payload: "foobar", length: 0.543, error: false },
      { id: 55, response: 200, lines: 0, word: 1, chars: 30, payload: "root", length: 0.561, error: false },
      { id: 56, response: 200, lines: 0, word: 1, chars: 30, payload: "info", length: 0.527, error: false },
      // Adding some examples with errors to demonstrate the highlighting feature
      { id: 57, response: 500, lines: 0, word: 1, chars: 45, payload: "'; DROP TABLE users;--", length: 0.612, error: true },
      { id: 58, response: 404, lines: 0, word: 12, chars: 340, payload: "/admin", length: 0.382, error: true },
      { id: 59, response: 403, lines: 0, word: 15, chars: 280, payload: "../../../etc/passwd", length: 0.471, error: true }
    ];
    //---------------------------------------------------------------------
    
    
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
  
    // Function to determine if a row should be highlighted based on response code
    function isHighlightedRow(row) {
      // Highlight server errors (5xx) and some client errors (4xx)
      return row.response >= 400 || row.error === true;
    }
    
    // Function to get highlight color based on response code
    function getHighlightColor(row) {
      if (row.response >= 500) {
        return '#ffdddd'; // Red background for server errors
      } else if (row.response >= 400) {
        return '#fff3cd'; // Yellow background for client errors
      } else if (row.error === true) {
        return '#ffdddd'; // Red background for other errors
      }
      return 'transparent';
    }
  
    //TODO-----------------------------------------------
    function handleExport() {
      alert('Exporting results...');
      // Logic for exporting results would go here
    }
  
    function handleRestart() {
        goto('/fuzzer/running');
        // Logic for restarting scan would go here
    }
  
    function handleShowTerminal() {
      alert('Showing terminal...');
      // Logic for showing terminal would go here
    }
    //---------------------------------------------------
  </script>
  
  <div class="parameter-fuzzing-container">  
    <div class="main-content">
      <header>
        <h1>Parameter Fuzzing</h1>
        <div class="subtext">Results</div>
        
        <!-- Progress indicator -->
        <div class="steps-container">
          <div class="step completed">
            <div class="step-circle">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <span>Configuration</span>
          </div>
          <div class="connector completed"></div>
          <div class="step completed">
            <div class="step-circle">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <span>Running</span>
          </div>
          <div class="connector completed"></div>
          <div class="step active">
            <div class="step-circle">
              •
            </div>
            <span>Results</span>
          </div>
        </div>
      </header>
      
      <div class="metrics-container">
        <div class="metric">
          <h3>Running Time</h3>
          <div class="value">{runningTime}</div>
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
              <tr style="background-color: {getHighlightColor(row)}">
                <td>{row.id}</td>
                <td>
                  {row.response}
                  {#if row.response >= 400}
                    <span class="response-error">
                      {row.response === 500 ? 'Internal Server Error' : 
                       row.response === 404 ? 'Not Found' : 
                       row.response === 403 ? 'Forbidden' : ''}
                    </span>
                  {/if}
                </td>
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
        <button class="btn" on:click={handleRestart} title="Run the scan again">Restart</button>
        <button class="btn" on:click={handleExport} title="Export results">
          Export
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
        </button>
        <div class="spacer"></div>
        <button class="btn" on:click={handleShowTerminal} title="Show terminal output">Show Terminal</button>
      </div>
    </div>
  </div>
  
  <style>
    @import './results.css';
  </style>