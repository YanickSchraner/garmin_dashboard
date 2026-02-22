<template>
  <div class="activity-badge" :style="{ color: getActivityColor(type), borderColor: getActivityColor(type) + '40' }">
    {{ formatActivityType(type) }}
  </div>
</template>

<script setup>
const { getActivityColor, formatActivityType } = useActivityUtils()

defineProps({
  type: String
})
</script>

<style scoped>
.activity-badge {
  display: inline-flex;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  border: 1px solid;
  padding: 2px 7px;
  border-radius: 2px;
  white-space: nowrap;
}
</style>
