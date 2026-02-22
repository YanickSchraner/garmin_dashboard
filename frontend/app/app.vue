<template>
  <UApp>
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 py-4 shadow-sm">
        <div class="container mx-auto px-4 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-primary-600 dark:text-primary-400">Garmin Dashboard</h1>
          <UColorModeButton />
        </div>
      </header>

      <main class="flex-1 container mx-auto px-4 py-8">
        <NuxtPage />
      </main>

      <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-4 text-center text-gray-500 text-sm">
        &copy; 2026 Garmin Custom Dashboard
      </footer>
    </div>
  </UApp>
</template>

<script setup>
// Global layout
</script>
