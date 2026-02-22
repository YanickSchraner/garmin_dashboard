<template>
  <div class="app-card" :class="{ 'no-overflow': !allowOverflow }">
    <div v-if="$slots.header || label" class="app-card-head">
      <slot name="header">
        <span class="app-card-label">{{ label }}</span>
        <span v-if="subLabel" class="app-card-sub">{{ subLabel }}</span>
      </slot>
    </div>
    <div class="app-card-body" :style="bodyStyle">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  subLabel: String,
  bodyStyle: [Object, String],
  allowOverflow: { type: Boolean, default: false }
})
</script>

<style scoped>
.app-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
}

.no-overflow {
  overflow: hidden;
}

.app-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--raised);
}

.app-card-label {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.2em;
  color: var(--muted-light);
  text-transform: uppercase;
}

.app-card-sub {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.12em;
}

.app-card-body { padding: 6px 0; }
</style>
