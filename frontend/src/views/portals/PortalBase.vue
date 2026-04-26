<script setup lang="ts">
import DashboardLayout from '../../layouts/DashboardLayout.vue'
defineProps<{
  role: string
  title: string
  stats: Array<{ name: string; value: string; icon: string; color: string }>
}>()
</script>

<template>
  <DashboardLayout>
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ title }}</h1>
      <p class="text-gray-500 dark:text-slate-400">
        Welcome to your personalized {{ role }} portal.
      </p>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div
        v-for="stat in stats"
        :key="stat.name"
        class="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-gray-100 dark:border-slate-700 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-center gap-4">
          <div :class="`w-12 h-12 rounded-xl flex items-center justify-center ${stat.color}`">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                :d="stat.icon"
              />
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-500 dark:text-slate-400">{{ stat.name }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stat.value }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Placeholder Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div
        class="lg:col-span-2 bg-white dark:bg-slate-800 rounded-2xl border border-gray-100 dark:border-slate-700 p-6 min-h-[400px]"
      >
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Recent Activity</h3>
        <div class="flex flex-col items-center justify-center h-full text-center py-12">
          <div
            class="w-16 h-16 bg-gray-50 dark:bg-slate-700/50 rounded-full flex items-center justify-center mb-4"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-8 w-8 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-12 0 9 9 0 0112 0z"
              />
            </svg>
          </div>
          <p class="text-gray-500 dark:text-slate-400">No recent activity to show yet.</p>
        </div>
      </div>
      <div
        class="bg-white dark:bg-slate-800 rounded-2xl border border-gray-100 dark:border-slate-700 p-6"
      >
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Upcoming Events</h3>
        <p class="text-gray-500 dark:text-slate-400 text-sm">Your schedule is currently empty.</p>
      </div>
    </div>
  </DashboardLayout>
</template>
