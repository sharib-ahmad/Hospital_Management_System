<script setup lang="ts">
import ThemeToggle from '../components/ThemeToggle.vue'
</script>

<template>
  <div
    class="min-h-screen bg-[#f8fafc] dark:bg-[#06141b] flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-500 relative overflow-hidden"
  >
    <!-- Background Decorative Elements -->
    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 pointer-events-none">
      <div
        class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-200/20 dark:bg-emerald-600/10 rounded-full blur-[100px] animate-pulse"
      ></div>
      <div
        class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-teal-200/20 dark:bg-teal-600/10 rounded-full blur-[100px] animate-pulse transition-delay-2000"
      ></div>
    </div>

    <div class="absolute top-6 right-6">
      <ThemeToggle />
    </div>
    <div class="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
      <RouterLink
        :to="{ name: 'landing' }"
        class="flex justify-center items-center gap-3 mb-10 group"
      >
        <div
          class="w-12 h-12 bg-emerald-600 rounded-2xl flex items-center justify-center shadow-xl shadow-emerald-500/20 group-hover:rotate-6 transition-transform"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-7 w-7 text-white"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m12 14 4-4" />
            <path d="M3.34 19a10 10 0 1 1 17.32 0" />
          </svg>
        </div>
        <span class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter"
          >MediFlow <span class="text-emerald-600">HMS</span></span
        >
      </RouterLink>
    </div>

    <main class="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
      <div
        class="glass py-10 px-4 shadow-premium-xl sm:rounded-[2rem] sm:px-10 border border-white/40 dark:border-white/5 animate-in fade-in slide-in-from-bottom-4 duration-700"
      >
        <slot></slot>
      </div>
    </main>
  </div>
</template>
