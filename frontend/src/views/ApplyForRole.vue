<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import ApplicationForm from '../components/ApplicationForm.vue'
import { useAuthStore } from '../stores/auth'
import api from '../utils/axios'
import { useNotificationStore } from '../stores/notification'

const auth = useAuthStore()
const router = useRouter()
const notification = useNotificationStore()

const selectedRole = ref<string | null>(null)
const hasApplied = ref(false)
const applicationStatus = ref<string | null>(null)
const isLoading = ref(true)

const roles = [
  {
    id: 'doctor',
    title: 'Medical Doctor',
    description: 'Provide advanced clinical care, manage patient consultations and treatments.',
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
    color: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400',
  },
  {
    id: 'nurse',
    title: 'Healthcare Nurse',
    description: 'Monitor vitals, assist doctors, and provide primary patient care.',
    icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    color: 'bg-teal-50 text-teal-600 dark:bg-teal-900/30 dark:text-teal-400',
  },
]

const checkStatus = async () => {
  try {
    const response = await api.get('/applications')
    const apps = response.data.data || []
    if (apps.length > 0) {
      // If they have a pending professional application, show status
      const profApp = apps.find((a: any) => a.role_applied !== 'patient')
      if (profApp) {
        hasApplied.value = true
        applicationStatus.value = profApp.status
      }
    }
  } catch (error) {
    console.error('Failed to fetch applications')
  } finally {
    isLoading.value = false
  }
}

onMounted(checkStatus)

const selectRole = (roleId: string) => {
  selectedRole.value = roleId
}

const handleSuccess = () => {
  hasApplied.value = true
  applicationStatus.value = 'pending'
  selectedRole.value = null
}
</script>

<template>
  <DashboardLayout>
    <div v-if="isLoading" class="flex flex-col items-center justify-center min-h-[400px]">
      <div
        class="animate-spin rounded-full h-12 w-12 border-[3px] border-emerald-600 border-t-transparent"
      ></div>
    </div>

    <div v-else-if="hasApplied" class="max-w-2xl mx-auto py-12">
      <div
        class="glass p-12 rounded-[3rem] text-center border border-white/40 dark:border-white/5 shadow-premium animate-in fade-in slide-in-from-bottom-4 duration-700"
      >
        <div
          class="w-24 h-24 bg-emerald-50 dark:bg-emerald-900/30 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-sm"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-12 w-12 text-emerald-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h2 class="text-3xl font-black text-gray-900 dark:text-white mb-4 tracking-tight">
          Application Submitted!
        </h2>
        <p class="text-gray-500 dark:text-slate-400 mb-8 font-medium">
          Your application is currently
          <span class="font-black text-emerald-600 uppercase tracking-widest">{{
            applicationStatus
          }}</span
          >. Our administration team is reviewing your profile.
        </p>
        <button
          @click="router.push('/user')"
          class="px-10 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/25 hover:-translate-y-1 transition-all active:scale-95 uppercase tracking-widest text-xs"
        >
          Return to Hub
        </button>
      </div>
    </div>

    <div v-else-if="!selectedRole" class="animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div class="mb-12">
        <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none">
          Choose Your Path
        </h1>
        <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
          Select the role you'd like to perform within the MediFlow ecosystem.
        </p>
      </div>

      <div class="grid md:grid-cols-2 gap-10 max-w-4xl mx-auto">
        <div
          v-for="role in roles"
          :key="role.id"
          @click="selectRole(role.id)"
          class="group glass p-10 rounded-[2.5rem] border border-white/40 dark:border-white/5 hover:border-emerald-500/50 dark:hover:border-emerald-400/50 shadow-premium hover:shadow-premium-xl transition-all duration-500 cursor-pointer flex flex-col items-center text-center"
        >
          <div
            :class="`w-20 h-20 rounded-3xl flex items-center justify-center mb-10 group-hover:scale-110 transition-transform ${role.color}`"
          >
            <svg class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                :d="role.icon"
              />
            </svg>
          </div>
          <h3 class="text-2xl font-black text-gray-900 dark:text-white mb-4 tracking-tight">
            {{ role.title }}
          </h3>
          <p class="text-gray-500 dark:text-slate-400 text-sm font-medium leading-relaxed mb-10">
            {{ role.description }}
          </p>
          <div class="mt-auto">
            <span
              class="inline-flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-black uppercase text-[10px] tracking-[0.2em] group-hover:gap-4 transition-all"
            >
              Apply Now
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="3"
              >
                <path d="M9 5l7 7-7 7" />
              </svg>
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <button
        @click="selectedRole = null"
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
        Change Role
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
              Role Details
            </h2>
            <p class="text-xs text-gray-500 mt-1 uppercase font-black tracking-widest">
              Applying as {{ selectedRole }}
            </p>
          </div>
        </div>

        <ApplicationForm :role="selectedRole" @success="handleSuccess" />
      </div>
    </div>
  </DashboardLayout>
</template>
