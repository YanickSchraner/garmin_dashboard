<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-semibold">Weekly Performance</h2>
      <UBadge color="gray" variant="solid">Week 8</UBadge>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <UCard class="bg-blue-50/50 dark:bg-blue-900/10 border-blue-100 dark:border-blue-900/30">
        <div class="flex flex-col items-center gap-2 py-2">
          <UIcon name="i-heroicons-moon-20-solid" class="w-8 h-8 text-blue-500" />
          <h3 class="text-xs font-medium text-blue-600 dark:text-blue-400 uppercase">Sleep Quality</h3>
          <p class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">7h 45m</p>
          <span class="text-[10px] text-blue-500 font-semibold">+15m from last week</span>
        </div>
      </UCard>

      <UCard class="bg-red-50/50 dark:bg-red-900/10 border-red-100 dark:border-red-900/30">
        <div class="flex flex-col items-center gap-2 py-2">
          <UIcon name="i-heroicons-heart-20-solid" class="w-8 h-8 text-red-500" />
          <h3 class="text-xs font-medium text-red-600 dark:text-red-400 uppercase">Avg RHR</h3>
          <p class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">52 bpm</p>
          <span class="text-[10px] text-green-600 font-semibold">-2 bpm (Improved)</span>
        </div>
      </UCard>

      <UCard class="bg-green-50/50 dark:bg-green-900/10 border-green-100 dark:border-green-900/30">
        <div class="flex flex-col items-center gap-2 py-2">
          <UIcon name="i-heroicons-bolt-20-solid" class="w-8 h-8 text-green-500" />
          <h3 class="text-xs font-medium text-green-600 dark:text-green-400 uppercase">Trainings</h3>
          <p class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">3 sessions</p>
          <span class="text-[10px] text-green-600 font-semibold">Goal reached</span>
        </div>
      </UCard>

      <UCard class="bg-indigo-50/50 dark:bg-indigo-900/10 border-indigo-100 dark:border-indigo-900/30">
        <div class="flex flex-col items-center gap-2 py-2">
          <UIcon name="i-heroicons-fire-20-solid" class="w-8 h-8 text-indigo-500" />
          <h3 class="text-xs font-medium text-indigo-600 dark:text-indigo-400 uppercase">Total Dist</h3>
          <p class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">28.4 km</p>
          <span class="text-[10px] text-indigo-500 font-semibold">Keep it up!</span>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
// Weekly summary component
</script>
