<template>
  <div class="shimmer" :style="{ height, width, borderRadius: radius }"></div>
</template>

<script setup>
defineProps({
  height: { type: String, default: '14px' },
  width: { type: String, default: '100%' },
  radius: { type: String, default: '2px' }
})
</script>

<style scoped>
.shimmer {
  background: linear-gradient(90deg, var(--raised) 25%, var(--border) 50%, var(--raised) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
