<script>
  let csvFile = null;
  let wordlistFile = null;
  let credentials = [];

  async function handleGenerate() {
    const formData = new FormData();
    formData.append("csv_file", csvFile);
    formData.append("wordlist", wordlistFile);

    const res = await fetch("/api/ml/generate", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    if (data.error) {
      alert("Error: " + data.error);
    } else {
      credentials = data.credentials;
    }
  }
</script>

<h1>Generate Credentials</h1>

<form on:submit|preventDefault={handleGenerate}>
  <div>
    <label>CSV File (URLs):</label>
    <input type="file" accept=".csv" on:change={(e) => csvFile = e.target.files[0]} required />
  </div>

  <div>
    <label>Wordlist File (.txt):</label>
    <input type="file" accept=".txt" on:change={(e) => wordlistFile = e.target.files[0]} required />
  </div>

  <button type="submit">Generate</button>
</form>

{#if credentials.length}
  <h2>Generated Credentials</h2>
  <ul>
    {#each credentials as cred}
      <li><strong>{cred.username}</strong> — {cred.password}</li>
    {/each}
  </ul>
{/if}
