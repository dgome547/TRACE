<script>
  import Slider from "$lib/components/Slider.svelte";
  import Button from "$lib/components/Button.svelte";
  import FileUploader from "$lib/components/FileUploader.svelte";

  let allowNumbers = false;
  let allowSymbols = false;
  let allowUppercase = false;
  let allowLowercase = false;

  let useWordlist = false;
  let wordlistPath = '';

  let usernameOptions = {
    characters: false,
    numbers: true,
    symbols: true,
    length: 12
  };
  let passwordOptions = {
    characters: true,
    numbers: false,
    symbols: false,
    length: 12
  };

  let generatedCredentials = [];

  function handleUpload() {
    const file = event.target.files[0];
    if (file) {
      wordlistPath = file.name; // or file.path (only works in Electron)
      console.log("Selected file:", file);
    }
  }
  
  function handleWordlist(file) {
    wordlistPath = file.name;
    console.log("Wordlist selected:", file);
  }

  async function handleGenerate() {
    try {
      const res = await fetch('/api/ml/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wordlistPath,
          usernameOptions,
          passwordOptions
        })
      });

      if (!res.ok) {
        throw new Error("Failed to generate credentials");
      }

      const data = await res.json();
      generatedCredentials = data.credentials;
      alert("Credentials generated!");
    } catch (err) {
      console.error("Generation error:", err);
      alert("Failed to generate credentials.");
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

  .section {
    margin-bottom: 40px;
  }

  label {
    font-weight: bold;
    display: block;
    margin-bottom: 5px;
  }

  input[type="text"], input[type="number"] {
    width: 400px;
    padding: 10px;
    font-size: 14px;
    margin-bottom: 10px;
  }

  .toggle-group {
    display: flex;
    flex-direction: column;
    margin-top: 10px;
    margin-bottom: 20px;
  }

  .dual-section {
    display: flex;
    gap: 100px;
  }

  button {
    background-color: var(--primary);
    border: none;
    border-radius: 5px;
    padding: 12px 25px;
    font-size: 16px;
    cursor: pointer;
    margin-top: 30px;
  }

  .upload-btn {
    margin-top: 10px;
  }
</style>

<div class="main">
  <h2>AI Generator</h2>

  <!-- Configuration Section -->
  <div class="section">
    <label>Word List *</label>
    <FileUploader
      label="Upload Wordlist"
      accept=".txt,.csv"
      onFileSelect={handleWordlist}
    />
  </div>

  <!-- Username & Password Settings -->
  <div class="dual-section">
    <div>
      <label>Username</label>
      <div class="toggle-group">
        <Slider label="Characters" bind:checked={usernameOptions.characters} />
        <Slider label="Numbers" bind:checked={usernameOptions.numbers} />
        <Slider label="Symbols" bind:checked={usernameOptions.symbols} />
        <input type="number" min="1" bind:value={usernameOptions.length} placeholder="Length" />
      </div>
    </div>

    <div>
      <label>Password</label>
      <div class="toggle-group">
        <Slider label="Characters" bind:checked={passwordOptions.characters} />
        <Slider label="Numbers" bind:checked={passwordOptions.numbers} />
        <Slider label="Symbols" bind:checked={passwordOptions.symbols} />
        <input type="number" min="1" bind:value={passwordOptions.length} placeholder="Length" />
      </div>
    </div>
  </div>

  <Button label="Generate" on:click={handleGenerate} />
</div>