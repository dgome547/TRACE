<script>
  export let label = "Upload File";
  export let accept = ".txt,.csv";
  export let onFileSelect = () => {};

  let selectedFileNames = [];

  function handleChange(event) {
    const files = Array.from(event.target.files);
    if (files.length > 0) {
      selectedFileNames = files.map(file => file.name);
      onFileSelect(files);
    }
  }

  function triggerInput() {
    document.getElementById("file-input").click();
  }

  function clearFiles() {
    selectedFileNames = [];
    document.getElementById("file-input").value = "";
    onFileSelect([]);
  }
</script>

<style>
  .upload-container {
    border: 2px dashed #9BC2CB;
    padding: 20px;
    width: 100%;
    text-align: center;
    cursor: pointer;
    border-radius: 8px;
    margin-bottom: 20px;
  }

  .upload-container:hover {
    background-color: #f0f8ff;
  }

  input[type="file"] {
    display: none;
  }

  .file-name {
    font-size: 14px;
    margin-top: 10px;
    color: #444;
  }

  .clear-btn {
    margin-top: 10px;
    background-color: #f87171;
    color: white;
    border: none;
    padding: 5px 12px;
    border-radius: 4px;
    cursor: pointer;
  }
</style>

<div>
  <label>{label}</label>
  <div class="upload-container" on:click={triggerInput}>
    <p>📂 Click to upload</p>
    {#if selectedFileNames.length}
      <div class="file-name">
        {#each selectedFileNames as name}
          {name}<br />
        {/each}
      </div>
      <button type="button" class="clear-btn" on:click|stopPropagation={clearFiles}> Clear Uploaded</button>
    {/if}
  </div>
  <input id="file-input" type="file" accept={accept} multiple on:change={handleChange} />
</div>