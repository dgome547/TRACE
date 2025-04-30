<script>
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import { configStore } from '$lib/stores/configStore'; // New store for config data

  // Form data
  let targetURL = '';
  let wordListFile = null;
  let topLevelDirectory = '';
  let hideStatus = '';
  let showOnlyStatus = '';
  let filterByLength = '';
  let additionalParams = '';
  
  // Validation states
  let errors = {
    targetURL: false,
    wordList: false
  };
  let isLoading = false;
  
  // Component state
  let isStartEnabled = false;
  let activeTab = 'Configuration';
  let tabs = ['Configuration', 'Running', 'Results'];
  
  // Check if form is valid
  function validateForm() {
    errors.targetURL = !targetURL;
    errors.wordList = !wordListFile;
    
    isStartEnabled = targetURL && wordListFile;
    return isStartEnabled;
  }
  
  // Handle start button click - modified to pass config to results page
  async function handleStart() {
    if (!validateForm()) {
      alert("Please fill out all required fields.");
      return;
    }

    // Create config object
    const configData = {
      target_url: targetURL,
      wordlist_file: wordListFile,
      max_concurrent_requests: 5,
      request_timeout: 5,
      output_format: "json",
      hide_status: hideStatus,
      show_only_status: showOnlyStatus,
      top_level_directory: topLevelDirectory,
      filter_by_content_length: filterByLength,
      additional_parameters: additionalParams
    };
    
    // Save config to store
    configStore.set(configData);
    
    // Navigate to results page
    isLoading = true;
    goto('/bruteForce/results');
  }
  
  // Handle wordlist upload
  function handleUpload() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.txt,.list,.dict';
    
    fileInput.onchange = (e) => {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        wordListFile = file;
        validateForm();
      }
    };
    
    fileInput.click();
  }
  
  // Set active tab
  function setActiveTab(tab) {
    activeTab = tab;
  }
  
  onMount(() => {
    validateForm();
  });
</script>

<div class="app-container">
  <!-- Main content -->
  <div class="main-content">
    <div class="header">
      <h1>Brute Force</h1>
    </div>

    <div class="content">
      <h2>Configuration</h2>
      
      <div class="form-group">
        <label for="target-url">Target URL *</label>
        <input 
          type="text" 
          id="target-url" 
          bind:value={targetURL} 
          placeholder="EX: https://juice-shop.herokuapp.com" 
          class={errors.targetURL ? 'error' : ''}
          on:input={validateForm}
        />
        {#if errors.targetURL}
          <div class="error-message">Target URL is required</div>
        {/if}
      </div>
      
      <div class="form-group">
        <label for="word-list">Word List *</label>
        <div class="input-with-button">
          <input 
            type="text" 
            id="word-list" 
            value={wordListFile?.name || ''} 
            readonly
            class={errors.wordList ? 'error' : ''}
          />
          <button class="upload-btn" on:click={handleUpload}>Upload Wordlist</button>
        </div>
        {#if errors.wordList}
          <div class="error-message">Word List is required</div>
        {/if}
      </div>
      
      <div class="form-group">
        <label for="top-level-dir">Top-Level Directory</label>
        <input 
          type="text" 
          id="top-level-dir" 
          bind:value={topLevelDirectory} 
          placeholder="/"
        />
      </div>
      
      <div class="form-group">
        <label for="hide-status">Hide Status Code (separate using commas)</label>
        <input 
          type="text" 
          id="hide-status" 
          bind:value={hideStatus} 
          placeholder="404, 403, etc."
        />
      </div>
      
      <div class="form-group">
        <label for="show-status">Show Only Status Code (separate using commas)</label>
        <input 
          type="text" 
          id="show-status" 
          bind:value={showOnlyStatus} 
          placeholder="200, 500, etc."
        />
      </div>
      
      <div class="form-group">
        <label for="filter-length">Filter by Content Length</label>
        <input 
          type="text" 
          id="filter-length" 
          bind:value={filterByLength} 
          placeholder=">100, <500, etc."
        />
      </div>
      
      <div class="form-group">
        <label for="additional-params">Additional Parameters (if applicable)</label>
        <input 
          type="text" 
          id="additional-params" 
          bind:value={additionalParams} 
          placeholder="NULL"
        />
      </div>
      
      <div class="button-container">
        <button class="start-btn" class:disabled={!isStartEnabled} on:click={handleStart}>
          Start
        </button>
      </div>
    </div>
    {#if isLoading}
      <p>Preparing scan... Redirecting to results page</p>
    {/if}
  </div>
</div>

<style>
  /* Styles remain the same */
  :root {
    --primary-color: #7FBFB6;
    --bg-color: #f5f5f5;
    --sidebar-bg: #ffffff;
    --input-bg: #ffffff;
    --error-color: #ff4757;
    --text-color: #333;
    --disabled-color: #ccc;
  }

  .app-container {
    display: flex;
    height: 100vh;
    background-color: var(--bg-color);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  }

  .main-content {
    flex: 1;
    padding: 20px 40px;
    overflow-y: auto;
  }

  .header {
    margin-bottom: 20px;
  }

  h1 {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
    color: var(--text-color);
  }

  h2 {
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 20px;
    color: var(--text-color);
  }

  .content {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  }

  .form-group {
    margin-bottom: 20px;
  }

  label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    color: #666;
  }

  input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    background-color: var(--input-bg);
  }

  input.error {
    border-color: var(--error-color);
  }

  .error-message {
    color: var(--error-color);
    font-size: 12px;
    margin-top: 4px;
  }

  .input-with-button {
    display: flex;
    gap: 10px;
  }

  .input-with-button input {
    flex: 1;
  }

  .upload-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0 16px;
    cursor: pointer;
    font-size: 14px;
    white-space: nowrap;
  }

  .button-container {
    margin-top: 30px;
    display: flex;
    justify-content: flex-start;
  }

  .start-btn {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 30px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .start-btn:hover {
    opacity: 0.9;
  }

  .start-btn.disabled {
    background-color: var(--disabled-color);
    cursor: not-allowed;
  }
</style>