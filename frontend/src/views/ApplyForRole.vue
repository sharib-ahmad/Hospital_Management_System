<script setup lang="ts">
import { ref } from 'vue'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import ApplicationForm from '../components/ApplicationForm.vue'

type ApplicationRole = 'patient' | 'doctor' | 'nurse' | null

const selectedRole = ref<ApplicationRole>(null)
const step = ref<'select' | 'form' | 'success'>('select')

const selectRole = (role: ApplicationRole) => {
  selectedRole.value = role
  step.value = 'form'
}

const handleSuccess = () => {
  step.value = 'success'
}

const roles = [
  {
    id: 'patient' as const,
    title: 'Patient',
    description: 'Register as a patient to book appointments and track your health records.',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  },
  {
    id: 'doctor' as const,
    title: 'Doctor',
    description: 'Apply as a doctor to manage patient consultations and your own schedule.',
    icon: 'M22 12h-4l-3 9L9 3l-3 9H2',
    color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  },
  {
    id: 'nurse' as const,
    title: 'Nurse',
    description: 'Register as a nurse to assist in patient care and vitals management.',
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  },
]
</script>

<template>
  <DashboardLayout>
    <div class="max-w-4xl mx-auto">
      <div v-if="step === 'select'" class="space-y-8">
        <div class="text-center">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Apply for a Role</h1>
          <p class="text-gray-600 dark:text-slate-400 mt-2">
            Choose the role that best fits your needs in the MediFlow ecosystem.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            v-for="role in roles"
            :key="role.id"
            @click="selectRole(role.id)"
            class="group cursor-pointer bg-white dark:bg-slate-800 p-8 rounded-3xl border-2 border-transparent hover:border-blue-500 dark:hover:border-blue-400 shadow-sm hover:shadow-xl transition-all duration-300 text-center"
          >
            <div
              :class="role.color"
              class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform"
            >
              <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  :d="role.icon"
                />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">{{ role.title }}</h3>
            <p class="text-sm text-gray-600 dark:text-slate-400 leading-relaxed">
              {{ role.description }}
            </p>
            <div
              class="mt-6 inline-flex items-center text-blue-600 dark:text-blue-400 font-bold group-hover:gap-2 transition-all"
            >
              Apply Now
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 ml-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="step === 'form' && selectedRole" class="space-y-8">
        <button
          @click="step = 'select'"
          class="inline-flex items-center text-sm font-medium text-gray-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 mr-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to selection
        </button>

        <div
          class="bg-white dark:bg-slate-800 rounded-3xl border border-gray-200 dark:border-slate-700 shadow-xl overflow-hidden"
        >
          <div
            class="p-8 border-b border-gray-100 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-700/50"
          >
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white capitalize">
              {{ selectedRole }} Application
            </h2>
            <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
              Please provide the following details to complete your registration.
            </p>
          </div>
          <div class="p-8">
            <ApplicationForm :role="selectedRole" @success="handleSuccess" />
          </div>
        </div>
      </div>

      <div v-else-if="step === 'success'" class="text-center py-12">
        <div
          class="w-20 h-20 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center mx-auto mb-6"
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
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Application Submitted!
        </h2>
        <p class="text-gray-600 dark:text-slate-400 mb-8 max-w-md mx-auto leading-relaxed">
          Your application has been successfully received and is currently under review by our
          medical board. We'll notify you once a decision is made.
        </p>
        <RouterLink
          :to="{ name: 'user-portal' }"
          class="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-all shadow-lg hover:shadow-blue-200"
        >
          Back to Portal
        </RouterLink>
      </div>
    </div>
  </DashboardLayout>
</template>
