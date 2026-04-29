<script setup lang="ts">
import ThemeToggle from '../components/ThemeToggle.vue'
</script>

<template>
  <div
    class="min-h-screen bg-gray-50 dark:bg-slate-900 flex flex-col justify-center py-8 px-4 sm:py-12 sm:px-6 lg:px-8 transition-colors duration-300"
  >
    <div class="absolute top-4 right-4">
      <ThemeToggle />
    </div>
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <RouterLink
        :to="{ name: 'landing' }"
        class="flex justify-center items-center gap-2 mb-6 group"
      >
        <div
          class="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg group-hover:bg-blue-700 transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6 text-white"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m12 14 4-4" />
            <path d="M3.34 19a10 10 0 1 1 17.32 0" />
          </svg>
        </div>
        <span class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight"
          >MediFlow <span class="text-blue-600">HMS</span></span
        >
      </RouterLink>
    </div>

    <main class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div
        class="bg-white dark:bg-slate-800 py-8 px-4 shadow-xl shadow-blue-100/50 dark:shadow-none sm:rounded-2xl sm:px-10 border border-gray-100 dark:border-slate-700"
      >
        <slot></slot>
      </div>
    </main>
  </div>
</template>
