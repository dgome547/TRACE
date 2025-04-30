<script>
    export let size = 30; // diameter in px
    export let color = '#69aeb4';
  </script>
  
  <style>
    .loader {
      position: relative;
      display: inline-block;
    }
  
    .outer-ring {
      border-radius: 50%;
      border-style: solid;
      position: absolute;
      top: 0;
      left: 0;
    }
  
    .inner-circle {
      border-radius: 50%;
      position: absolute;
      animation: shrink 2s infinite cubic-bezier(0.4, 0, 0.2, 1);
    }
  
    @keyframes shrink {
      0% {
        transform: scale(1);
        opacity: 1;
      }
      50% {
        transform: scale(0.5);
        opacity: 0.6;
      }
      100% {
        transform: scale(0);
        opacity: 0.4;
      }
    }
  </style>
  
  <div
    class="loader"
    style="width: {size}px; height: {size}px;"
  >
    <div
      class="outer-ring"
      style="
        width: {size}px;
        height: {size}px;
        border: 3px solid {color};
      "
    ></div>
  
    <div
      class="inner-circle"
      style="
        width: {size / 2}px;
        height: {size / 2}px;
        background-color: {color};
        top: 35%;
        left: 35%;
        transform: translate(-50%, -50%);
      "
    ></div>
  </div>