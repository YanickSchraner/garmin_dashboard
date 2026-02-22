<template>
  <div class="stat-block">
    <span class="stat-label">{{ label }}</span>
    <span class="stat-value">
      <slot>{{ value }}<span v-if="unit" class="stat-unit">{{ unit }}</span></slot>
    </span>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number],
  unit: String
})
</script>

<style scoped>
.stat-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px 20px;
  transition: background 0.15s;
}

.stat-block:hover { background: var(--raised); }

.stat-label {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--muted);
  text-transform: uppercase;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--text);
  letter-spacing: 0.03em;
  line-height: 1;
}

.stat-unit {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted-light);
  letter-spacing: 0.05em;
  margin-left: 2px;
}
</style>
