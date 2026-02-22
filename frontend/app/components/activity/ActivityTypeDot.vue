<template>
  <div class="activity-type-dot" :style="{ background: getActivityColor(type) }"></div>
</template>

<script setup>
const { getActivityColor } = useActivityUtils()
defineProps({
  type: String
})
</script>

<style scoped>
.activity-type-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>
