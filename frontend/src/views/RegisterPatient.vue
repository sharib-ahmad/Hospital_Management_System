<script setup lang="ts">
import { useRouter } from 'vue-router'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import ApplicationForm from '../components/ApplicationForm.vue'

const router = useRouter()

const handleSuccess = () => {
  router.push('/user')
}
</script>

<template>
  <DashboardLayout>
    <div class="max-w-3xl mx-auto py-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <button
        @click="router.push('/user')"
        class="inline-flex items-center gap-2 text-[10px] font-black text-gray-400 hover:text-emerald-600 uppercase tracking-widest mb-8 transition-colors group"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4 group-hover:-translate-x-1 transition-transform"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="3"
        >
          <path d="M15 19l-7-7 7-7" />
        </svg>
        Back to Dashboard
      </button>

      <div
        class="glass p-10 sm:p-12 rounded-[3rem] border border-white/40 dark:border-white/5 shadow-premium"
      >
        <div class="flex items-center gap-4 mb-10">
          <div
            class="w-14 h-14 rounded-2xl bg-emerald-600 flex items-center justify-center text-white"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-7 w-7"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
          </div>
          <div>
            <h2
              class="text-3xl font-black text-gray-900 dark:text-white tracking-tight leading-none"
            >
              Patient Registration
            </h2>
            <p class="text-xs text-gray-500 mt-1 uppercase font-black tracking-widest">
              Register yourself or a family member
            </p>
          </div>
        </div>

        <ApplicationForm role="patient" @success="handleSuccess" />
      </div>
    </div>
  </DashboardLayout>
</template>
