<script>
    import { goto } from '$app/navigation';
  import Slider from "$lib/components/Slider.svelte";
  import Button from "$lib/components/Button.svelte"; // Maybe Remove
  import FileUploader from "$lib/components/FileUploader.svelte";

  

  let useWordlist = false;
  let wordlistPath = '';
  let uploadedFiles = [];


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

  let generatedCredentials = [];

  function handleUpload() {
    const file = event.target.files[0];
    if (file) {
      wordlistPath = file.name; 
      console.log("Selected file:", file);
    }
  }

  function logPayloadAndTestRequest() {
  console.log("📦 Payload being sent:", {
    wordlistPath,
    usernameOptions,
    passwordOptions
  });
}
  
function handleWordlist(files) {
  // Array of File objects
  uploadedFiles = files; 
  console.log("Uploaded files:", uploadedFiles);
}

async function handleGenerate() {
  const formData = new FormData();

  // [SRS 35.1 Optimized Aspects] The system shall validate user input 
  if (!usernameOptions.characters || !passwordOptions.characters) {
    alert("Username and password options must have 'characters' enabled.");
    return;
  }

  // [SRS 35.1 Optimized Aspects] Validate that length values are positive integers and within reasonable range
  if (!Number.isInteger(usernameOptions.length) || usernameOptions.length <= 0 || usernameOptions.length > 16) {
    alert("Username length must be a positive integer between 1 and 16.");
    return;
  }
  if (!Number.isInteger(passwordOptions.length) || passwordOptions.length <= 0 || passwordOptions.length > 16) {
    alert("Password length must be a positive integer between 1 and 16.");
    return;
  }

  formData.append("usernameOptions", JSON.stringify(usernameOptions));
  formData.append("passwordOptions", JSON.stringify(passwordOptions));

  for (let file of uploadedFiles) {
    formData.append("files", file);
  }

  try {
    const start = performance.now();
    const res = await fetch("http://localhost:8000/api/ml/generate", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Failed to generate credentials");

    const data = await res.json();
    const end = performance.now();

    const runtime = ((end - start) / 1000).toFixed(3); // seconds

    goto("/ml/results", {
      state: {
        credentials: data.credentials,
        runtime
      }
    });

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

  <!-- [SRS 35.7] Generate button placed bottom-left -->
  <button class="app-button" on:click={handleGenerate}>Generate</button>
</div>