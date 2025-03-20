<script>
    import { onMount } from 'svelte';
    import { goto } from "$app/navigation";

    
    let urlTree = [
      { url: "https://example.com", children: [
        { url: "https://example.com/login", children: [] },
        { url: "https://example.com/about", children: [] },
        { url: "https://example.com/contact", children: [] }
      ]}
    ];
    
    let credentials = [];
  
    // Generate simulated credentials
    function generateCredentials(url) {
      const randomString = (length) => Array.from({ length }, () => Math.random().toString(36)[2]).join('');
      const username = randomString(8);
      const password = randomString(12);
      return { url, username, password };
    }
  
    function traverseAndGenerate(tree) {
      credentials = [];
      function traverse(node) {
        if (!node) return;
        credentials.push(generateCredentials(node.url));
        node.children.forEach(child => traverse(child));
      }
      tree.forEach(node => traverse(node));
    }
  
    onMount(() => {
      traverseAndGenerate(urlTree);
    });
  </script>
  
  <section>
    <div class="card">
      <h2>Simulated ML Algorithm - Credential Generator</h2>
  
      <button on:click={() => traverseAndGenerate(urlTree)}>Regenerate Credentials</button>
      <button>Restart crawler</button>
      <button on:click={goto('/admin')}>Exit</button>
      
      <div class="results">
        <h3>Generated Credentials</h3>
        {#if credentials.length > 0}
          <ul>
            {#each credentials as cred}
              <li>
                <strong>URL:</strong> {cred.url}<br>
                <strong>Username:</strong> {cred.username}<br>
                <strong>Password:</strong> {cred.password}<br><br>
              </li>
            {/each}
          </ul>
        {/if}
      </div>
      <h5>Data saved to results.csv under TRACE Folder</h5>
    </div>
  </section>
  
  <style>
    section {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: #f0f0f0;
    }
  
    .card {
      background: white;
      padding: 2rem;
      border-radius: 1rem;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      width: 35rem;
      max-width: 90vw;
    }
  
    h2 {
      text-align: center;
      margin-bottom: 1rem;
    }
  
    .results {
      margin-top: 1rem;
      background: #e0f7fa;
      padding: 1rem;
      border-radius: 0.5rem;
    }
  
    button {
      background: #007bff;
      color: white;
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 0.5rem;
      cursor: pointer;
    }
    
    button:hover {
      background: #0056b3;
    }
  </style>
  