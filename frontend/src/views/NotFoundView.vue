<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const getHomeRoute = () => {
  if (!auth.isAuthenticated) return { name: 'landing' }
  return { name: `${auth.user?.role}-portal` }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center p-6">
    <div class="max-w-md w-full text-center">
      <div class="mb-8 relative">
        <div
          class="text-[120px] font-black text-blue-600/10 dark:text-blue-400/10 leading-none select-none"
        >
          404
        </div>
        <div class="absolute inset-0 flex items-center justify-center">
          <div
            class="w-24 h-24 bg-blue-100 dark:bg-blue-900/30 rounded-3xl flex items-center justify-center text-blue-600 dark:text-blue-400"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-12 w-12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        </div>
      </div>

      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Page Not Found</h1>
      <p class="text-gray-600 dark:text-slate-400 mb-8">
        Oops! The page you are looking for doesn't exist or has been moved. Please check the URL or
        return to safety.
      </p>

      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <RouterLink
          :to="getHomeRoute()"
          class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-2xl shadow-lg shadow-blue-500/25 transition-all"
        >
          Return Home
        </RouterLink>
        <button
          @click="$router.back()"
          class="px-8 py-3 bg-white dark:bg-slate-800 text-gray-700 dark:text-white font-bold rounded-2xl border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700 transition-all"
        >
          Go Back
        </button>
      </div>

      <div
        class="mt-12 text-xs text-gray-400 dark:text-slate-500 uppercase tracking-widest font-bold"
      >
        MediFlow Hospital Management System
      </div>
    </div>
  </div>
</template>
