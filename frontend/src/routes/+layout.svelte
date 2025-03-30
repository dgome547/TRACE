<script>
    let icon1Default = "/T1.webp";
    let icon1Hover = "/T1-h.webp";
    let icon1Src = icon1Default;
  
    let icon2Default = "/T2.webp";
    let icon2Hover = "/T2-h.webp";
    let icon2Src = icon2Default;
  
    let icon3Default = "/T3.webp";
    let icon3Hover = "/T3-h.webp";
    let icon3Src = icon3Default;
  
    let icon4Default = "/T4.webp";
    let icon4Hover = "/T4-h.webp";
    let icon4Src = icon4Default;
  
    let settingDefault = "/settings-gear.webp";
    let settingHover = "/settings-gear-h.webp";
    let settingSrc = settingDefault;
  
    function onIconClick(icon) {
      console.log(`Clicked: ${icon}`);
    }
  
    function handleMouseOver(icon) {
      if (icon === 1) icon1Src = icon1Hover;
      if (icon === 2) icon2Src = icon2Hover;
      if (icon === 3) icon3Src = icon3Hover;
      if (icon === 4) icon4Src = icon4Hover;
      if (icon === 'setting') settingSrc = settingHover;
    }
  
    function handleMouseOut(icon) {
      if (icon === 1) icon1Src = icon1Default;
      if (icon === 2) icon2Src = icon2Default;
      if (icon === 3) icon3Src = icon3Default;
      if (icon === 4) icon4Src = icon4Default;
      if (icon === 'setting') settingSrc = settingDefault;
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
      width: 120px;
      height: 40px;
      margin-bottom: 30px;
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
  
    .icons img, .settings {
      width: 50px;
      height: 50px;
      cursor: pointer;
    }
  
    .settings {
        width: 50px;
        height: 50px;
        cursor: pointer;
        position: absolute;
        bottom: 40px
      
    }
  
    .main {
      flex-grow: 1;
      padding: 20px;
      overflow-y: auto;
    }
  </style>
  
  <div class="layout">
    <aside class="sidebar">
      <img src="/trace-logo.png" alt="Logo" class="logo" on:click={() => onIconClick('logo')} />
      <div class="icons">
        <img src={icon1Src} alt="Icon 1" on:click={() => onIconClick(1)} on:mouseover={() => handleMouseOver(1)} on:mouseout={() => handleMouseOut(1)} />
        <img src={icon2Src} alt="Icon 2" on:click={() => onIconClick(2)} on:mouseover={() => handleMouseOver(2)} on:mouseout={() => handleMouseOut(2)} />
        <img src={icon3Src} alt="Icon 3" on:click={() => onIconClick(3)} on:mouseover={() => handleMouseOver(3)} on:mouseout={() => handleMouseOut(3)} />
        <img src={icon4Src} alt="Icon 4" on:click={() => onIconClick(4)} on:mouseover={() => handleMouseOver(4)} on:mouseout={() => handleMouseOut(4)} />
      </div>
      <img src={settingSrc} alt="Settings" class="settings" on:click={() => onIconClick('setting')} on:mouseover={() => handleMouseOver('setting')} on:mouseout={() => handleMouseOut('setting')} />
    </aside>
  
    <div class="main">
      <slot />
    </div>
  </div>