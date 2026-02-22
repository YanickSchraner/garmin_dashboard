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

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
      <!-- Recent Activities List -->
      <section class="lg:col-span-2">
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-semibold">Recent Activities</h2>
              <UButton variant="link" color="primary" size="sm">View All</UButton>
            </div>
          </template>

          <UTable 
            :rows="activities || []" 
            :columns="activityColumns" 
            :loading="activitiesLoading"
          >
            <template #activityName-data="{ row }">
              <div class="flex items-center gap-2">
                <UIcon 
                  :name="getActivityIcon(row.activityType?.typeKey)" 
                  class="w-4 h-4 text-primary-500" 
                />
                <span class="font-medium text-gray-900 dark:text-white">{{ row.activityName }}</span>
              </div>
            </template>
            <template #startTimeLocal-data="{ row }">
              <span class="text-gray-500 text-xs">{{ formatDate(row.startTimeLocal) }}</span>
            </template>
            <template #distance-data="{ row }">
              <span class="font-semibold">{{ (row.distance / 1000).toFixed(2) }} km</span>
            </template>
          </UTable>

          <div v-if="!activitiesLoading && (!activities || activities.length === 0)" class="py-10 text-center text-gray-400 italic">
            No recent activities found. Time to lace up those shoes!
          </div>
        </UCard>
      </section>

      <!-- Health Trends Sidebar -->
      <section class="space-y-8">
        <UCard class="bg-gradient-to-br from-primary-50 to-white dark:from-gray-800 dark:to-gray-900 border-primary-100 dark:border-gray-700">
          <div class="flex items-center gap-3 mb-4">
            <UIcon name="i-heroicons-fire-20-solid" class="w-6 h-6 text-primary-500" />
            <h2 class="text-lg font-semibold">Health Trends</h2>
          </div>
          <div class="space-y-4">
            <div>
              <p class="text-xs text-gray-500 uppercase font-bold tracking-wider mb-1">RHR Improvement</p>
              <div class="flex items-baseline gap-2">
                <span class="text-2xl font-bold">-4 bpm</span>
                <span class="text-xs text-green-600 font-medium">this year</span>
              </div>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase font-bold tracking-wider mb-1">Avg Sleep</p>
              <div class="flex items-baseline gap-2">
                <span class="text-2xl font-bold">7h 12m</span>
                <span class="text-xs text-blue-600 font-medium">+18m vs 2025</span>
              </div>
            </div>
          </div>
        </UCard>

        <UCard>
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-4 italic text-center">"Consistency is the key to progress."</h3>
          <p class="text-xs text-gray-500 text-center">You are currently {{ goalStatus?.status === 'ahead' ? 'ahead of' : 'working towards' }} your 104-run goal. Keep moving!</p>
        </UCard>
      </section>
    </div>
  </div>
</template>

<script setup>
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

// Fetch recent activities
const {
  data: activities,
  pending: activitiesLoading,
  refresh: refreshActivities
} = await useFetch(`${apiBase}/activities`, {
  query: { 
    start_date: '2026-02-01', 
    end_date: '2026-02-22' 
  },
  immediate: true
})

const activityColumns = [
  { key: 'activityName', label: 'Activity' },
  { key: 'startTimeLocal', label: 'Date' },
  { key: 'distance', label: 'Distance' }
]

const getActivityIcon = (type) => {
  if (type === 'running') return 'i-heroicons-bolt-20-solid'
  if (type === 'cycling') return 'i-heroicons-map-20-solid'
  return 'i-heroicons-user-20-solid'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const refreshData = async () => {
  await Promise.all([refreshGoal(), refreshActivities()])
}
</script>
