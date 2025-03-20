<!-- src/routes/crawler/+page.svelte -->
<script>
  let url = '';
  let depthLimit = 1;
  let timeout = 5000;
  let loading = false;
  let results = null;
  let error = null;

  async function startCrawling() {
    // Reset previous results and errors
    results = null;
    error = null;
    loading = true;
    
    try {
      const response = await fetch('http://localhost:5173/backend/app/webcrawler.py', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url,
          depthLimit,
          timeout
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to start crawler');
      }
      
      results = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<section>
  <div class="card">
    <h2>Crawler Configuration</h2>
    <label for="crawler-url">URL</label>
    <input
      id="crawler-url"
      type="text"
      bind:value={url}
      placeholder="https://example.com"
    />
    <label for="crawler-depth">Depth Limit</label>
    <input
      id="crawler-depth"
      type="number"
      bind:value={depthLimit}
    />
    <label for="crawler-timeout">Timeout (ms)</label>
    <input
      id="crawler-timeout"
      type="number"
      bind:value={timeout}
    />
    <button on:click={startCrawling} disabled={loading}>
      {loading ? 'Crawling...' : 'Start Crawler'}
    </button>
    
    {#if error}
      <div class="error">
        <p>Error: {error}</p>
      </div>
    {/if}
    
    {#if results}
      <div class="results">
        <h3>Crawler Results</h3>
        <p>Pages visited: {results.pages_visited}</p>
        <p>Links found: {results.links_found}</p>
        
        {#if results.data && results.data.length > 0}
          <div class="pages-list">
            <h4>Pages crawled:</h4>
            <ul>
              {#each results.data as page}
                <li>
                  <a href={page.url} target="_blank">{page.title || page.url}</a>
                  {#if page.status === "error"}
                    <span class="error-text">Error: {page.error}</span>
                  {/if}
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</section>

<style>
  /* Full-page container styling */
  section {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: #f8fafc; /* Light gray background */
  }
  /* Card (island) styling */
  .card {
    background: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    width: 30rem;
    max-width: 90vw;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  /* Heading */
  h2 {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }
  /* Labels */
  label {
    font-weight: 600;
  }
  /* Inputs */
  input {
    border: 1px solid #ccc;
    border-radius: 0.5rem;
    padding: 0.5rem;
  }
  /* Button */
  button {
    background: #007bff;
    color: white;
    border: none;
    border-radius: 0.5rem;
    padding: 0.75rem;
    cursor: pointer;
    transition: background 0.2s;
  }
  button:hover:not([disabled]) {
    background: #0056b3;
  }
  button[disabled] {
    background: #cccccc;
    cursor: not-allowed;
  }
  /* Error message */
  .error {
    background: #ffe6e6;
    color: #d32f2f;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #d32f2f;
  }
  /* Results section */
  .results {
    margin-top: 1rem;
    padding: 1rem;
    background: #f0f8ff;
    border-radius: 0.5rem;
  }
  .results h3 {
    margin-top: 0;
    font-size: 1.2rem;
    font-weight: 600;
  }
  .pages-list {
    max-height: 300px;
    overflow-y: auto;
    margin-top: 1rem;
  }
  .error-text {
    color: #d32f2f;
    font-size: 0.9rem;
    margin-left: 0.5rem;
  }
</style>