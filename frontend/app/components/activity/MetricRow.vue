<template>
  <div class="metric-row">
    <span class="metric-name">{{ label }}</span>
    <div class="metric-right">
      <span class="metric-val" :class="{ 'metric-val--accent': accent }">
        <slot>{{ value }}<span v-if="unit" class="metric-unit"> {{ unit }}</span></slot>
      </span>
      <slot name="after-val" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number],
  unit: String,
  accent: Boolean
})
</script>

<style scoped>
.metric-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border);
  gap: 12px;
}

.metric-row:last-child { border-bottom: none; }

.metric-name {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--muted-light);
  flex-shrink: 0;
}

.metric-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.metric-val {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--text);
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.metric-val--accent { color: var(--accent); }

.metric-unit {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--muted-light);
  letter-spacing: 0.1em;
}
</style>
