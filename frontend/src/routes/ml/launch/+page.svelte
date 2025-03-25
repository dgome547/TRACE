<script>
  import Slider from "$lib/components/Slider.svelte";
  import Button from "$lib/components/Button.svelte";

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

  function handleUpload() {
    alert("Upload wordlist not implemented yet.");
  }

  function handleGenerate() {
    alert("🔐 Generate credentials not implemented yet.");
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
    background-color: #9BC2CB;
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
    <input type="text" bind:value={wordlistPath} placeholder="/home/user/wordlist.txt" />
    <br />
    <button class="upload-btn" on:click={handleUpload}>📤 Upload Wordlist</button>
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