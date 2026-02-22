<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-trophy-20-solid" class="w-5 h-5 text-yellow-500" />
          <h2 class="text-xl font-semibold">Annual Goal: {{ goal }} Runs</h2>
        </div>
        <UBadge color="primary" variant="subtle">{{ year }} Progress</UBadge>
      </div>
    </template>

    <div class="space-y-6">
      <div class="flex justify-between items-end">
        <div class="flex flex-col">
          <span class="text-sm font-medium text-gray-500 uppercase tracking-wider">Actual vs Target</span>
          <div class="flex items-baseline gap-2">
            <span class="text-5xl font-extrabold text-primary-600 tracking-tight">{{ actual }}</span>
            <span class="text-gray-400 text-xl">/ {{ goal }}</span>
          </div>
        </div>
        <div class="text-right">
          <div class="text-2xl font-bold" :class="statusColor">
            {{ statusText }}
          </div>
          <div class="text-sm font-medium text-gray-400">
            Target: {{ targetToDate }} to be on track
          </div>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between text-sm font-medium">
          <span>{{ percent }}% Complete</span>
          <span class="text-gray-400">{{ goal - actual }} runs left</span>
        </div>
        <UProgress :value="percent" color="primary" size="lg" />
      </div>

      <div class="pt-4 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center">
        <div class="flex items-center gap-1.5 text-sm text-gray-500">
          <UIcon name="i-heroicons-calendar-days-20-solid" class="w-4 h-4" />
          <span>Sunday, Feb 22</span>
        </div>
        <UButton 
          variant="ghost" 
          color="gray" 
          icon="i-heroicons-arrow-path-20-solid"
          size="sm"
          :loading="loading"
          @click="$emit('refresh')"
        >
          Sync Garmin
        </UButton>
      </div>
    </div>
  </UCard>
</template>

<script setup>
const props = defineProps({
  goal: { type: Number, default: 104 },
  actual: { type: Number, default: 0 },
  targetToDate: { type: Number, default: 0 },
  percent: { type: Number, default: 0 },
  status: { type: String, default: 'behind' },
  year: { type: Number, default: 2026 },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['refresh'])

const statusText = computed(() => {
  if (props.status === 'ahead') return 'Ahead of Schedule'
  if (props.actual >= props.targetToDate) return 'On Track'
  return 'Behind Schedule'
})

const statusColor = computed(() => {
  if (props.status === 'ahead') return 'text-green-600 dark:text-green-400'
  if (props.actual >= props.targetToDate) return 'text-primary-600 dark:text-primary-400'
  return 'text-orange-600 dark:text-orange-400'
})
</script>
