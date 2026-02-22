<template>
  <button :class="['app-btn', variant]" v-bind="$attrs">
    <span v-if="iconLeft" class="btn-icon-left">{{ iconLeft }}</span>
    <slot />
    <span v-if="iconRight" class="btn-icon-right">{{ iconRight }}</span>
  </button>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'outline' }, // 'outline', 'ghost'
  iconLeft: String,
  iconRight: String
})
</script>

<style scoped>
.app-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  background: transparent;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
  flex-shrink: 0;
  padding: 6px 12px;
}

.outline {
  color: var(--muted-light);
  border: 1px solid var(--border-light);
}

.outline:hover { 
  border-color: var(--accent); 
  color: var(--accent); 
}

.btn-icon-right {
  transition: transform 0.2s;
}

.app-btn:hover .btn-icon-right {
  transform: translateX(3px);
}
</style>
