<template>
  <div class="space-y-10 max-w-5xl mx-auto">
    <!-- Annual Goal Section -->
    <section>
      <div v-if="statusError" class="mb-6">
        <UAlert
          color="red"
          variant="soft"
          icon="i-heroicons-exclamation-triangle-20-solid"
          title="Backend Connection Failed"
          :description="statusError.data?.detail || 'Could not connect to the Garmin Dashboard API. Ensure the backend server is running.'"
        />
      </div>

      <RunGoalProgress 
        :goal="goalStatus?.goal || 104"
        :actual="goalStatus?.actual || 0"
        :target-to-date="goalStatus?.expected_to_date || 0"
        :percent="goalStatus?.progress_percent || 0"
        :status="goalStatus?.status || 'behind'"
        :year="goalStatus?.year || 2026"
        :loading="statusLoading"
        @refresh="refreshData"
      />
    </section>

    <!-- Weekly Performance Section -->
    <section>
      <WeeklySummary />
    </section>

    <!-- Placeholder for Health Trends Line Plot -->
    <section class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-8 shadow-sm">
      <div class="flex items-center gap-3 mb-6">
        <UIcon name="i-heroicons-chart-bar-20-solid" class="w-6 h-6 text-primary-500" />
        <h2 class="text-xl font-semibold">Health Stats Progress (Yearly)</h2>
      </div>
      <div class="h-64 flex flex-col items-center justify-center border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg">
        <p class="text-gray-400 font-medium">Line plot visualization coming soon...</p>
        <p class="text-gray-400 text-sm italic">Tracking RHR and Sleep improvements over time</p>
      </div>
    </section>
  </div>
</template>

<script setup>
// Configure backend API URL
const config = useRuntimeConfig()
const apiBase = 'http://localhost:8000'

// Fetch goal status
const { 
  data: goalStatus, 
  pending: statusLoading, 
  error: statusError,
  refresh: refreshGoal 
} = await useFetch(`${apiBase}/goal-status`, {
  query: { year: 2026 },
  immediate: true
})

const refreshData = async () => {
  await refreshGoal()
}
</script>
