<template>
  <div class="space-y-10 max-w-5xl mx-auto">
    <!-- Annual Goal Section -->
    <section>
      <RunGoalProgress 
        :goal="104"
        :actual="0"
        :target-to-date="15.4"
        :percent="0"
        status="behind"
        :year="2026"
        :loading="false"
        @refresh="onRefresh"
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
const onRefresh = () => {
  console.log('Refreshing Garmin data...')
}
</script>
