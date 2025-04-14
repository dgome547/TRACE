<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    
    // Configuration variables
    let targetUrl = '';
    let wordListPath = '';
    let cookies = '';
    let hideStatusCodes = '';
    let showStatusCodes = '';
    let contentLengthFilter = '';
    let additionalParams = '';
    
    // HTTP method selection
    let httpMethod = 'GET';
    
    // Reference to file input element
    let fileInput;
    
    // Handle wordlist file upload
    function handleWordlistUpload() {
      fileInput.click();
    }
    
    function onFileSelected(event) {
      const file = event.target.files[0];
      if (file) {
        wordListPath = file.name;
        // In a real app, you'd handle the file upload to server here
      }
    }
    
    // Start fuzzing process
    function startFuzzing() {
      // Implementation would connect to backend service
        goto('/fuzzer/running');

    }
    
    // Handle form submission
    function handleSubmit(event) {
      event.preventDefault();
      // Validate and process the form data here
      startFuzzing();
    }
  </script>
  
  <style>
    .main-container {
      display: flex;
      width: 100%;
      height: 100vh;
      background-color: #f5f5f5;
    }
    
    .content-area {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
    }
    
    .title-container {
      margin-bottom: 30px;
    }
    
    h1 {
      font-size: 24px;
      margin: 0;
      padding: 0;
      font-weight: 500;
    }
    
    .progress-indicator {
      display: flex;
      justify-content: center;
      margin: 20px 0 30px;
    }
    
    .step {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100px;
      position: relative;
    }
    
    .step-circle {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      justify-content: center;
      align-items: center;
      margin-bottom: 5px;
    }
    
    .step.active .step-circle {
      background-color: #4CAF50;
      color: white;
    }
    
    .step.inactive .step-circle {
      background-color: #e0e0e0;
      color: #666;
    }
    
    .step-label {
      font-size: 12px;
      color: #666;
    }
    
    .step:not(:last-child)::after {
      content: "";
      position: absolute;
      top: 12px;
      right: -50%;
      width: 100%;
      height: 2px;
      background-color: #e0e0e0;
      z-index: 0;
    }
    
    .configuration-form {
      max-width: 600px;
      margin: 0 auto;
    }
    
    .form-section {
      margin-bottom: 15px;
    }
    
    .form-section label {
      display: block;
      font-size: 13px;
      margin-bottom: 5px;
      color: #333;
    }
    
    .form-section input[type="text"] {
      width: 100%;
      padding: 8px 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
    }
    
    .radio-group {
      display: flex;
      gap: 20px;
      margin-top: 5px;
    }
    
    .radio-option {
      display: flex;
      align-items: center;
    }
    
    .radio-option input {
      margin-right: 5px;
    }
    
    .wordlist-container {
      position: relative;
    }
    
    .wordlist-container input[type="text"] {
      width: calc(100% - 120px);
    }
    
    .upload-button {
      position: absolute;
      right: 0;
      bottom: 0;
      background-color: #2196F3;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 8px 15px;
      font-size: 12px;
      cursor: pointer;
    }
    
    .upload-button:hover {
      background-color: #0b7dda;
    }
    
    .hidden-file-input {
      display: none;
    }
    
    .start-button {
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 10px 20px;
      font-size: 14px;
      cursor: pointer;
      margin-top: 20px;
    }
    
    .start-button:hover {
      background-color: #45a049;
    }
    
    h2 {
      font-size: 18px;
      margin: 0 0 20px 0;
      color: #444;
      font-weight: normal;
    }
  </style>
  
  <div class="main-container">
    
    <div class="content-area">
      <!-- Title section -->
      <div class="title-container">
        <h1>Parameter Fuzzing</h1>
      </div>
      
      <!-- Progress indicator (as shown in Figure 11) -->
      <div class="progress-indicator">
        <div class="step active">
          <div class="step-circle">1</div>
          <div class="step-label">Configuration</div>
        </div>
        <div class="step inactive">
          <div class="step-circle">2</div>
          <div class="step-label">Running</div>
        </div>
        <div class="step inactive">
          <div class="step-circle">3</div>
          <div class="step-label">Results</div>
        </div>
      </div>
      
      <!-- Configuration form -->
      <div class="configuration-form">
        <h2>Configuration</h2>
        
        <!-- Target URL input -->
        <div class="form-section">
          <label for="target-url">Target URL *</label>
          <input 
            type="text" 
            id="target-url" 
            bind:value={targetUrl} 
            placeholder="https://example.com/api/endpoint"
          />
        </div>
        
        <!-- Word List input with upload button -->
        <div class="form-section wordlist-container">
          <label for="word-list">Word List *</label>
          <input 
            type="text" 
            id="word-list" 
            bind:value={wordListPath} 
            placeholder="/path/to/wordlist.txt"
          />
          <button class="upload-button" on:click={handleWordlistUpload}>
            Upload Wordlist
          </button>
          <input 
            type="file" 
            class="hidden-file-input" 
            bind:this={fileInput}
            on:change={onFileSelected}
            accept=".txt,.list,.dict"
          />
        </div>
        
        <!-- HTTP Method radio buttons -->
        <div class="form-section">
          <label>HTTP Method</label>
          <div class="radio-group">
            <div class="radio-option">
              <input type="radio" id="get" name="http-method" value="GET" bind:group={httpMethod} />
              <label for="get">GET</label>
            </div>
            <div class="radio-option">
              <input type="radio" id="put" name="http-method" value="PUT" bind:group={httpMethod} />
              <label for="put">PUT</label>
            </div>
            <div class="radio-option">
              <input type="radio" id="post" name="http-method" value="POST" bind:group={httpMethod} />
              <label for="post">POST</label>
            </div>
          </div>
        </div>
        
        <!-- Cookies input -->
        <div class="form-section">
          <label for="cookies">Cookies (if applicable)</label>
          <input 
            type="text" 
            id="cookies" 
            bind:value={cookies} 
            placeholder="NULL"
          />
        </div>
        
        <!-- Hide Status Codes input -->
        <div class="form-section">
          <label for="hide-status">Hide Status Code (separate using commas)</label>
          <input 
            type="text" 
            id="hide-status" 
            bind:value={hideStatusCodes} 
            placeholder="403, 404, etc."
          />
        </div>
        
        <!-- Show Status Codes input -->
        <div class="form-section">
          <label for="show-status">Show Only Status Code (separate using commas)</label>
          <input 
            type="text" 
            id="show-status" 
            bind:value={showStatusCodes} 
            placeholder="200, 500, etc."
          />
        </div>
        
        <!-- Filter by Content Length input -->
        <div class="form-section">
          <label for="content-length">Filter by Content Length</label>
          <input 
            type="text" 
            id="content-length" 
            bind:value={contentLengthFilter} 
            placeholder=">100, <500, etc."
          />
        </div>
        
        <!-- Additional Parameters input -->
        <div class="form-section">
          <label for="additional-params">Additional Parameters (if applicable)</label>
          <input 
            type="text" 
            id="additional-params" 
            bind:value={additionalParams} 
            placeholder="NULL"
          />
        </div>
        
        <!-- Start button -->
        <button class="start-button" on:click={startFuzzing}>
          Start
        </button>
      </div>
    </div>
  </div>