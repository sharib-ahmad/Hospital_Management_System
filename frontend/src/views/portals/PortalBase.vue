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
    <main>
      <div class="mb-12">
        <div class="flex items-center gap-3 mb-2">
          <span
            class="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest border border-emerald-100 dark:border-emerald-500/20"
          >
            {{ role }}
          </span>
        </div>
        <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">
          {{ title }}
        </h1>
        <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
          Manage your daily operations and monitor real-time hospital analytics.
        </p>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
        <div
          v-for="stat in stats"
          :key="stat.name"
          class="group bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-gray-100 dark:border-slate-800 shadow-premium hover:shadow-premium-xl transition-all duration-500 hover:-translate-y-1"
        >
          <div class="flex items-start justify-between mb-6">
            <div
              :class="`w-14 h-14 rounded-2xl flex items-center justify-center ${stat.color} shadow-lg shadow-current/20 group-hover:rotate-6 transition-transform`"
            >
              <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                  :d="stat.icon"
                />
              </svg>
            </div>
            <div class="flex items-center gap-1 text-emerald-500 font-bold text-xs">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z"
                  clip-rule="evenodd"
                ></path>
              </svg>
              12%
            </div>
          </div>
          <div>
            <p
              class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
            >
              {{ stat.name }}
            </p>
            <p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter">
              {{ stat.value }}
            </p>
          </div>
        </div>
      </div>

      <!-- Main Dashboard Area -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
        <div
          class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-10 min-h-[500px] shadow-premium"
        >
          <slot name="main">
            <div class="flex items-center justify-between mb-10">
              <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
                <span class="h-1.5 w-6 bg-indigo-600 rounded-full"></span>
                Recent Activity
              </h3>
              <button
                class="text-xs font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest hover:underline"
              >
                View All History
              </button>
            </div>

            <div
              class="flex flex-col items-center justify-center h-full text-center py-20 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border-2 border-dashed border-gray-100 dark:border-slate-800"
            >
              <div
                class="w-20 h-20 bg-white dark:bg-slate-900 rounded-3xl shadow-premium flex items-center justify-center mb-6 text-gray-300 dark:text-slate-700"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-10 w-10"
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
              <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
                No activity data yet
              </h4>
              <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium">
                When users interact with the system, their actions will appear here in real-time.
              </p>
            </div>
          </slot>
        </div>

        <div class="space-y-10">
          <slot name="sidebar">
            <div
              class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-8 shadow-premium"
            >
              <h3
                class="text-lg font-black text-gray-900 dark:text-white mb-6 uppercase tracking-widest"
              >
                Upcoming Events
              </h3>
              <div
                class="flex items-center gap-4 p-4 rounded-2xl bg-indigo-50/50 dark:bg-indigo-900/10 border border-indigo-100/50 dark:border-indigo-500/10"
              >
                <div
                  class="w-10 h-10 rounded-xl bg-indigo-600 flex flex-col items-center justify-center text-white font-bold leading-none"
                >
                  <span class="text-[10px]">MAY</span>
                  <span class="text-sm">04</span>
                </div>
                <div>
                  <p class="text-xs font-black text-gray-900 dark:text-white">
                    Staff Coordination Meet
                  </p>
                  <p class="text-[10px] text-gray-500 font-bold uppercase tracking-tighter">
                    10:00 AM • Main Hall
                  </p>
                </div>
              </div>
              <p
                class="text-gray-400 dark:text-slate-600 text-[10px] font-black uppercase tracking-[0.2em] mt-8 text-center"
              >
                Your schedule is light today
              </p>
            </div>

            <div
              class="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-[2.5rem] p-8 text-white shadow-xl shadow-indigo-500/30"
            >
              <h3 class="text-xl font-black mb-4 tracking-tight">Need Assistance?</h3>
              <p class="text-indigo-100 text-sm mb-8 font-medium leading-relaxed">
                Access the clinical help desk or system documentation for advanced orchestration
                guides.
              </p>
              <button
                class="w-full py-4 bg-white text-indigo-600 rounded-2xl text-xs font-black uppercase tracking-widest shadow-lg hover:-translate-y-1 transition-all"
              >
                Open Help Desk
              </button>
            </div>
          </slot>
        </div>
      </div>
    </main>
  </DashboardLayout>
</template>
