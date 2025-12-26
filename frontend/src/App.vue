<template>
  <router-view />
</template>

<script setup lang="ts">
// App root component
</script>

<style>
:root {
  --color-primary-1: #e3f2ff;
  --color-primary-2: #c5e0ff;
  --color-primary-3: #96c2ff;
  --color-primary-4: #64a0ff;
  --color-primary-5: #3b82f6;
  --color-primary-6: #2563eb;
  --color-primary-7: #1d4ed8;
  --color-primary-8: #1e40af;
  --color-primary-9: #1e3a8a;
  --color-primary-10: #172554;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  width: 100%;
  height: 100%;
}

body {
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--color-bg-1);
  color: var(--color-text-1);
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>
