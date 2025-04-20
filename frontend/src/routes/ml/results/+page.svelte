<script>
// Import Svelte lifecycle and utilities
import { onMount } from 'svelte';
import { goto } from '$app/navigation';
import { page } from '$app/stores';
import { get } from 'svelte/store';

// Reactive variables populated from navigation state
let credentials = [];
let runtime = 0;

// Get the navigation state passed from the previous page (launch)
$: {
  const state = get(page).state ?? {};
  credentials = state.credentials ?? [];
  runtime = Number(state.runtime ?? 0); 
}

// Compute counts based on received credentials
let usernamesGenerated = credentials.length;
let passwordsGenerated = credentials.filter(c => c.password).length;

// Navigate back to the launch page to run generation again
function reGenerate() {
  goto('/ml/launch');
}

// Placeholder for saving credentials to a wordlist (to be implemented)
function saveWordList() {
  alert('Save to wordlist functionality coming soon!');
}
</script>

<div class="main">
  <h2>AI Generator</h2>

  <!-- Display summary statistics -->
  <div class="status-metrics">
    <div class="status-box">
      <p>Running Time</p>
      <span>{runtime.toFixed(3)}</span>
    </div>
    <div class="status-box">
      <p>Generated Usernames</p>
      <span>{usernamesGenerated}</span>
    </div>
    <div class="status-box">
      <p>Generated Passwords</p>
      <span>{passwordsGenerated}</span>
    </div>
  </div>

  <!-- Table showing each generated credential pair -->
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Usernames</th>
        <th>Passwords</th>
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

  <!-- Re-Generate and Save Word List buttons aligned to corners -->
  <div class="button-container">
    <div class="left-buttons">
      <button on:click={reGenerate}>Re-Generate</button>
    </div>
    <div class="right-buttons">
      <button on:click={saveWordList}>Save Word List</button>
    </div>
  </div>
</div>

<style>
/* Layout and font */
.main {
  padding: 20px;
  padding-left: 30px;
  font-family: Arial, sans-serif;
  height: 100vh;
  position: relative;
}

/* Metrics display */
.status-metrics {
  display: flex;
  justify-content: space-around;
  padding: 10px;
  margin-bottom: 10px;
}

.status-box {
  text-align: center;
  font-size: 16px;
  padding: 10px;
}

.status-box span {
  font-weight: bold;
  font-size: 20px;
}

/* Table layout */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  border: 1px solid var(--border);
  padding: 8px;
  text-align: left;
}

th {
  background-color: var(--primary);
  color: var(--text);
}

/* Button container layout */
.button-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: fixed;
  bottom: 20px;
  left: 30px;
  right: 30px;
  padding: 10px 20px;
}

.left-buttons,
.right-buttons {
  display: flex;
  gap: 10px;
}

.button-container button {
  padding: 10px 20px;
  margin: 5px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background-color: var(--primary);
}

.button-container button:first-of-type {
  margin-left: 70px;
}
</style>