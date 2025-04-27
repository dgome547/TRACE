<script>
  import { goto } from '$app/navigation';
  import Slider from "$lib/components/Slider.svelte";
  import FileUploader from "$lib/components/FileUploader.svelte";

  let uploadedFiles = [];
  let numToGenerate = 10;

  let usernameOptions = {
    characters: true,
    numbers: false,
    symbols: false,
    length: 12
  };

  let passwordOptions = {
    characters: true,
    numbers: false,
    symbols: false,
    length: 12
  };

  let isLoading = false;

  function handleWordlist(files) {
    uploadedFiles = files;
    console.log("Uploaded wordlist files:", uploadedFiles);
  }

  async function startGenerator() {
    isLoading = true;

    const formData = new FormData();

    // Validation: Make sure inputs are correct
    if (!usernameOptions.characters || !passwordOptions.characters) {
      alert("Username and Password must have 'characters' enabled.");
      return;
    }
    if (!Number.isInteger(usernameOptions.length) || usernameOptions.length <= 0 || usernameOptions.length > 16) {
      alert("Username length must be between 1 and 16.");
      return;
    }
    if (!Number.isInteger(passwordOptions.length) || passwordOptions.length <= 0 || passwordOptions.length > 16) {
      alert("Password length must be between 1 and 16.");
      return;
    }

    // Append options
    formData.append("username_length", usernameOptions.length.toString());
    formData.append("password_length", passwordOptions.length.toString());
    formData.append("use_username_chars", usernameOptions.characters.toString());
    formData.append("use_username_nums", usernameOptions.numbers.toString());
    formData.append("use_username_symbols", usernameOptions.symbols.toString());
    formData.append("use_password_chars", passwordOptions.characters.toString());
    formData.append("use_password_nums", passwordOptions.numbers.toString());
    formData.append("use_password_symbols", passwordOptions.symbols.toString());
    formData.append("num_to_generate", numToGenerate.toString());

    // Attach the uploaded wordlist file
    for (let file of uploadedFiles) {
      formData.append("files", file);
    }

    try {
      const res = await fetch("http://localhost:5000/api/ml/generate", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Failed to generate credentials.");

      const data = await res.json();

      goto("/ml/results", {
        state: {
          credentials: data.credentials,
          runtime: data.runtime_seconds
        }
      });

    } catch (err) {
      console.error("Generation error:", err);
      alert("Failed to generate credentials.");
    } finally {
      isLoading = false;
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

  /* [SRS 35.2] The toggles for Characters, Numbers, and Symbols shall have distinct, visible states to indicate activation.  */
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
  <!-- [SRS 35.1] Section title labeled as “AI Generator” -->
  <h2>AI Generator</h2>
  
  <!-- [SRS 35.2] Sub text labeled as “Configuration” -->
  <p>Configuration:</p>

  <!-- Configuration Section -->
  <div class="section">
    <!-- [SRS 35.3] File Upload UI and file path logic -->
    <!-- Includes Upload Wordlist button with file icon and hidden file path -->
    <label>Word List *</label>
    <FileUploader
      label="Upload Wordlist"
      accept=".txt,.csv"
      onFileSelect={handleWordlist}
    />
  </div>

  <!-- Username & Password Settings -->
  <div class="dual-section">
    <!-- [SRS 35.5] Toggles for characters, numbers, symbols for usernames  -->
    <div>
      <label>Username</label>
      <div class="toggle-group">
        <!-- [SRS 35.5a] Toggles for characters  -->
        <Slider label="Characters" bind:checked={usernameOptions.characters} />
        <!-- [SRS 35.5b] Toggles for numbers -->
        <Slider label="Numbers   " bind:checked={usernameOptions.numbers} />
        <!-- [SRS 35.5c] Toggles for symbols -->
        <Slider label="Symbols   " bind:checked={usernameOptions.symbols} />
        <!-- [SRS 35.6] Input box to specify username/password length -->
        <input type="number" min="1" bind:value={usernameOptions.length} placeholder="Length" />
      </div>
    </div>

    <!-- [SRS 35.5] Toggles for characters, numbers, symbols for passwords -->
    <div>
      <label>Password</label>
      <div class="toggle-group">
        <!-- [SRS 35.5a] Toggles for characters  -->
        <Slider label="Characters" bind:checked={passwordOptions.characters} />
        <!-- [SRS 35.5b] Toggles for numbers -->
        <Slider label="Numbers" bind:checked={passwordOptions.numbers} />
        <!-- [SRS 35.5c] Toggles for symbols -->
        <Slider label="Symbols" bind:checked={passwordOptions.symbols} />
        <!-- [SRS 35.6] Input box to specify username length -->
        <input type="number" min="1" bind:value={passwordOptions.length} placeholder="Length" />
      </div>
    </div>
  </div>

  <label>Number of Credentials to Generate</label>
  <input type="number" min="1" bind:value={numToGenerate} placeholder="e.g., 10" />

  <!-- [SRS 35.7] Generate button placed bottom-left -->
  <button class="app-button" on:click={startGenerator}>Generate</button>
</div>

