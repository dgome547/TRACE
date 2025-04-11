<script>
  let csvFile = null;
  let wordlistFile = null;
  let csvPath = '';
  let wordlistPath = '';
  let credentials = [];
  let isLoading = false;

  async function handleGenerate() {
    if (!csvFile && !csvPath || !wordlistFile && !wordlistPath) {
      alert("Please provide both files or paths.");
      return;
    }

    isLoading = true;

    const formData = new FormData();
    if (csvFile) formData.append("csv_file", csvFile);
    formData.append("csv_path", csvPath);

    if (wordlistFile) formData.append("wordlist", wordlistFile);
    formData.append("wordlist_path", wordlistPath);

    try {
      const res = await fetch('http://localhost:8000/api/ml/generate', {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(`Server error ${res.status}: ${err}`);
      }

      const data = await res.json();
      if (data.error) {
        alert("Backend Error: " + data.error);
      } else {
        credentials = data.credentials;
      }
    } catch (error) {
      alert("Failed to generate credentials.\n\n" + error.message);
    } finally {
      isLoading = false;
    }
  }

  function downloadCSV() {
    if (!credentials.length) return;

    const header = "ID,Username,Password\n";
    const rows = credentials
      .map((cred, index) => `${index + 1},${cred.username},${cred.password}`)
      .join("\n");
    const blob = new Blob([header + rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "generated_credentials.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
</script>

<style>
  .page-title {
    position: absolute;
    top: 20px;
    left: 90px;
    font-size: 24px;
    font-weight: bold;
  }

  .center-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 100px;
    text-align: center;
  }

  h2 {
    font-size: 22px;
    margin-bottom: 20px;
  }

  form {
    width: 400px;
    text-align: left;
  }

  label {
    font-weight: bold;
    display: block;
    margin: 12px 0 4px;
  }

  input[type="file"],
  input[type="text"] {
    width: 100%;
    padding: 8px;
    font-size: 14px;
    margin-bottom: 16px;
  }

  button {
    padding: 10px 20px;
    background: #0070f3;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    margin-top: 12px;
    margin-right: 12px;
  }

  table {
    margin-top: 20px;
    width: 80%;
    max-width: 700px;
    border-collapse: collapse;
  }

  th, td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: center;
  }

  th {
    background-color: #f0f0f0;
  }
</style>

<div class="page-title">AI Generator</div>

<div class="center-container">
  <h2>Configuration</h2>

  <form on:submit|preventDefault={handleGenerate}>
    <label for="csv-path">CSV Path (optional)</label>
    <input id="csv-path" type="text" bind:value={csvPath} placeholder="e.g. temp/web_text.csv" />

    <label for="csv">Upload CSV File</label>
    <input id="csv" type="file" accept=".csv" on:change={e => csvFile = e.target.files[0]} />

    <label for="wordlist-path">Wordlist Path (optional)</label>
    <input id="wordlist-path" type="text" bind:value={wordlistPath} placeholder="e.g. temp/wordlist.txt" />

    <label for="wordlist">Upload Wordlist (.txt)</label>
    <input id="wordlist" type="file" accept=".txt" on:change={e => wordlistFile = e.target.files[0]} />

    <button type="submit" disabled={isLoading}>
      {isLoading ? 'Generating...' : 'Generate'}
    </button>
  </form>

  {#if isLoading}
    <p>Generating credentials, please wait...</p>
  {/if}

  {#if credentials.length}
    <h2>Generated Credentials</h2>

    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Password</th>
        </tr>
      </thead>
      <tbody>
        {#each credentials as cred, i}
          <tr>
            <td>{i + 1}</td>
            <td>{cred.username}</td>
            <td>{cred.password}</td>
          </tr>
        {/each}
      </tbody>
    </table>

    <button on:click={downloadCSV} style="margin-top: 16px;">
    Download CSV
    </button>
  {/if}
</div>
