<script setup>
import { RouterView } from 'vue-router'
import ToastNotification from './components/ToastNotification.vue'
</script>

<template>
  <ToastNotification />
  <RouterView />
</template>

<style>
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}

#app {
  width: 100%;
}
</style>
