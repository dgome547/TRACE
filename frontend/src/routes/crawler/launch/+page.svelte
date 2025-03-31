<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
  
    let isLoading = false;
    
    // Form fields
    let targetUrl = '';
    let crawlDepth = 1;
    let pageLimit = 50;
    let urlPatterns = '';
    let userAgent = 'Mozilla/5.0';
    let requestDelay = 1000;
    let proxy = '';

  
    async function startCrawler() {
      isLoading = true;
      
    const formData = {
      targetUrl,
      crawlDepth,
      pageLimit,
      urlPatterns,
      userAgent,
      requestDelay,
      proxy
    };

    try {
      fetch('http://127.0.0.1:5000/api/crawler', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      }).catch(err => {
        console.error("Background error:", err);
      });
    } catch (error) {
      console.error("Error initiating crawler:", error);
    }

    // Redirect immediately
    goto('/crawler/execution');
  }
</script>
  
  <style>
    /* Main content area: leave room for the fixed sidebar */
    .main-content {
      margin-left: 70px; /* Same as sidebar width */
      padding: 20px;
      width: calc(100% - 70px);
      overflow-y: auto;
    }
  
    .ToolName {
      margin-bottom: 20px;
    }
  
    .crawler-form {
      max-width: 500px;
      margin: 0 auto;
    }
  
    .crawler-form label {
      font-weight: bold;
    }
  
    .crawler-form input {
      padding: 0.5rem;
      font-size: 1rem;
      border: 1px solid var(--border);
      border-radius: 4px;
      width: 100%;
      box-sizing: border-box;
      margin-bottom: 1rem;
    }
  
    .submit-button {
      position: fixed;
      bottom: 20px; /* Adjust bottom margin as needed */
      left: 100px;   /* Adjust left margin as needed */
      height: 20px;
      width: 100px; /* Increase this value for a longer button */
      padding: 1rem; /* Adjust padding for height/vertical spacing */
      background-color: var(--primary); /* Your desired background color */
      color: var(--text);
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      display: flex;                /* Enables Flexbox */
      justify-content: center;      /* Centers content horizontally */
      align-items: center;          /* Centers content vertically */
      text-align: center;           /* Ensures text alignment is centered */
    }
    .spinner {
      border: 3px solid #f3f3f3;
      border-top: 3px solid #333;
      border-radius: 50%;
      width: 18px;
      height: 18px;
      animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  
    /* .submit-button:hover {
      background-color: #E14E2A;
    } */
  
    /* Responsive: stack vertically on small screens */
    @media (max-width: 600px) {
      .main-content {
        margin-left: 0;
        width: 100%;
      }
    }
  </style>

  
    <!-- Main content area -->
    <div class="main-content">
      <div class="ToolName">
        <h2>Crawler</h2>
        
      </div>
  
      <form on:submit|preventDefault={startCrawler} class="crawler-form">
        <div>
          <label for="targetUrl">Target URL</label><br />
          <input
            id="targetUrl"
            type="text"
            bind:value={targetUrl}
            placeholder="https://example.com"
            required
          />
        </div>
    
        <div>
          <label for="crawlDepth">Crawl Depth</label><br />
          <input
            id="crawlDepth"
            type="number"
            min="1"
            bind:value={crawlDepth}
            required
          />
        </div>
    
        <div>
          <label for="pageLimit">Limit on Number of Pages</label><br />
          <input
            id="pageLimit"
            type="number"
            min="1"
            bind:value={pageLimit}
            required
          />
        </div>
    
        <div>
          <label for="urlPatterns">URL Patterns</label><br />
          <input
            id="urlPatterns"
            type="text"
            bind:value={urlPatterns}
            placeholder="https://example.com/.*"
          />
        </div>
    
        <div>
          <label for="userAgent">User Agent String</label><br />
          <input
            id="userAgent"
            type="text"
            bind:value={userAgent}
          />
        </div>
    
        <div>
          <label for="requestDelay">Request Delay (ms)</label><br />
          <input
            id="requestDelay"
            type="number"
            min="0"
            bind:value={requestDelay}
          />
        </div>
    
        <div>
          <label for="proxy">Proxy</label><br />
          <input
            id="proxy"
            type="text"
            bind:value={proxy}
            placeholder="127.0.0.1:8080"
          />
        </div>
    
        <button type="submit" class="submit-button" disabled={isLoading}>
          {#if isLoading}
            <span class="spinner"></span>
          {:else}
            Start
          {/if}
        </button>
      </form>
    </div>
  