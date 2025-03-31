<script>
  import '../app.css';
  
    function onIconClick(icon) {
      console.log(`Clicked: ${icon}`);
    }

  </script>
  
  <style>
    .layout {
      display: flex;
      height: 100vh;
    }
  
    /* f2f2f2 */

    .sidebar {
        width: 70px;
        min-width: 70px;
        height: 95vh;
        background-color: #f2f2f2;
        border-top-right-radius: 40px;
        border-bottom-right-radius: 40px;
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px 0;
        position: relative;
    }
  
    .logo {
      width: 2%;
      height: 20px;
      margin-bottom: 30px;
    }

    .icon-button {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background-color: transparent;
      border: none;
      cursor: pointer;
      display: flex;
      justify-content: center;
      align-items:  center;
      padding: 0;
      background-size: cover;
      background-position: center;
      transition: background-image 0.2s ease-in-out;
    }

    .icon-button svg {
      width: 30px;
      height: 30px;
      filter: brightness(0) saturate(100%);
      color: #666;
      transition: color 0.2s ease;
    }

    .icon-button:hover svg {
      filter: brightness(0) saturate(100%) sepia(100%) hue-rotate(200deg) saturate(600%) brightness(1.2);
    }

  
    .icons {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
    }
  

  
    .settings {
        cursor: pointer;
        position: absolute;
        bottom: 40px
      
    }

    .settings:hover svg {
      color: #ff9800;
    }
  
    .main {
      flex-grow: 1;
      padding: 20px;
      overflow-y: auto;
    }
  </style>

  
  
  <div class="layout">
    <aside class="sidebar">
      <img src="/trace-logo.png" alt="logo" on:click={() => onIconClick('logo')} />

      <div class="icons">
        <button class="icon-button" aria-label="Icon 1">
          <img src="/T1.svg" alt="Icon 1" />
        </button>
        <button class="icon-button" aria-label="Icon 2">
          <img src="/T2.svg" alt="Icon 1" />
        </button>
        <button class="icon-button" aria-label="Icon 3">
          <img src="/T3.svg" alt="Icon 1" />
        </button>
        <button class="icon-button" aria-label="Icon 4">
          <img src="/T4.svg" alt="Icon 1" />
        </button>
        <button class="icon-button" aria-label="Settings">
          <img src="/SettingsGear.svg" alt="Settings" />
        </button>
    </aside>
  
    <div class="main">
      <p style="color: gray;">Layout loaded</p>
      <slot />
    </div>
  </div>