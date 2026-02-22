<template>
  <div class="space-y-8">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">Annual Goal: 104 Runs</h2>
          <UBadge color="primary" variant="solid">Year 2026</UBadge>
        </div>
      </template>

      <div class="space-y-4">
        <div class="flex justify-between items-end mb-2">
          <div>
            <span class="text-4xl font-bold text-primary-600">0</span>
            <span class="text-gray-500 text-lg ml-1">/ 104 runs</span>
          </div>
          <div class="text-right">
            <div class="text-sm font-medium text-gray-400">0% complete</div>
          </div>
        </div>
        <UProgress :value="0" color="primary" />
        <p class="text-sm text-gray-500 italic">
          Start your engines! Fetching data from Garmin soon...
        </p>
      </div>
    </UCard>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <UCard class="bg-blue-50 dark:bg-blue-900/20">
        <div class="flex items-center space-x-4">
          <UIcon name="i-heroicons-moon-20-solid" class="w-8 h-8 text-blue-500" />
          <div>
            <h3 class="text-sm font-medium text-blue-600 dark:text-blue-400">Last Night Sleep</h3>
            <p class="text-2xl font-bold">--h --m</p>
          </div>
        </div>
      </UCard>

      <UCard class="bg-red-50 dark:bg-red-900/20">
        <div class="flex items-center space-x-4">
          <UIcon name="i-heroicons-heart-20-solid" class="w-8 h-8 text-red-500" />
          <div>
            <h3 class="text-sm font-medium text-red-600 dark:text-red-400">Resting Heart Rate</h3>
            <p class="text-2xl font-bold">-- bpm</p>
          </div>
        </div>
      </UCard>

      <UCard class="bg-green-50 dark:bg-green-900/20">
        <div class="flex items-center space-x-4">
          <UIcon name="i-heroicons-bolt-20-solid" class="w-8 h-8 text-green-500" />
          <div>
            <h3 class="text-sm font-medium text-green-600 dark:text-green-400">Weekly Trainings</h3>
            <p class="text-2xl font-bold">0 sessions</p>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  title: 'Dashboard'
})
</script>
