<template>
  <div class="te-bar" :style="{ width }">
    <div 
      class="te-fill" 
      :style="{ 
        width: Math.min((value / 5 * 100), 100) + '%', 
        backgroundColor: color || getTEColor(value) 
      }"
    ></div>
  </div>
</template>

<script setup>
const { getTEColor } = useActivityUtils()

defineProps({
  value: { type: Number, required: true },
  color: String,
  width: { type: String, default: '80px' }
})
</script>

<style scoped>
.te-bar {
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.te-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s ease;
}
</style>
