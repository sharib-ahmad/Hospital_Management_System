<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import { useNotificationStore } from '../stores/notification'
import api from '../utils/axios'

interface Application {
  id: number
  user_id: string
  role_applied: string
  status: string
  reason: string
  created_at: string
  // Role specific details
  specialization?: string
  experience_years?: number
  license_number?: string
  department_id?: string
}

const notification = useNotificationStore()
const applications = ref<Application[]>([])
const isLoading = ref(false)
const filterStatus = ref('pending')

const loadApplications = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/applications')
    applications.value = response.data.data || []
  } catch (error) {
    notification.error('Failed to load applications')
  } finally {
    isLoading.value = false
  }
}

const approveApplication = async (id: number) => {
  try {
    await api.post(`/applications/${id}/approve`)
    notification.success('Application approved successfully')
    loadApplications()
  } catch (error: any) {
    notification.error(error.response?.data?.message || 'Failed to approve application')
  }
}

const rejectApplication = async (id: number) => {
  const reason = prompt('Please enter rejection reason:')
  if (reason === null) return

  try {
    await api.post(`/applications/${id}/reject`, { reason })
    notification.success('Application rejected')
    loadApplications()
  } catch (error: any) {
    notification.error(error.response?.data?.message || 'Failed to reject application')
  }
}

onMounted(loadApplications)
</script>

<template>
  <DashboardLayout>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Application Management</h1>
      <p class="text-gray-600 dark:text-slate-400 mt-1">Review and process role applications.</p>
    </div>

    <div
      class="bg-white dark:bg-slate-800 rounded-3xl border border-gray-200 dark:border-slate-700 shadow-sm overflow-hidden"
    >
      <div
        class="p-6 border-b border-gray-100 dark:border-slate-700 flex justify-between items-center"
      >
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Recent Applications</h2>
        <button
          @click="loadApplications"
          class="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </button>
      </div>

      <div v-if="isLoading" class="p-12 text-center">
        <div
          class="animate-spin inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mb-4"
        ></div>
        <p class="text-gray-500">Loading applications...</p>
      </div>

      <div v-else-if="applications.length === 0" class="p-12 text-center">
        <p class="text-gray-500">No applications found.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left">
          <thead
            class="bg-gray-50 dark:bg-slate-700/50 text-gray-500 dark:text-slate-400 text-xs uppercase font-bold"
          >
            <tr>
              <th class="px-6 py-4">Role</th>
              <th class="px-6 py-4">Details</th>
              <th class="px-6 py-4">Status</th>
              <th class="px-6 py-4">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-slate-700">
            <tr
              v-for="app in applications"
              :key="app.id"
              class="hover:bg-gray-50 dark:hover:bg-slate-700/30 transition-colors"
            >
              <td class="px-6 py-4">
                <span
                  class="px-3 py-1 rounded-full text-xs font-bold capitalize"
                  :class="{
                    'bg-green-100 text-green-700': app.role_applied === 'patient',
                    'bg-blue-100 text-blue-700': app.role_applied === 'doctor',
                    'bg-purple-100 text-purple-700': app.role_applied === 'nurse',
                  }"
                >
                  {{ app.role_applied }}
                </span>
              </td>
              <td class="px-6 py-4">
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate max-w-xs">
                  {{ app.reason }}
                </p>
                <p class="text-xs text-gray-500" v-if="app.specialization">
                  {{ app.specialization }} • {{ app.experience_years }}yrs exp
                </p>
              </td>
              <td class="px-6 py-4">
                <span
                  class="text-xs font-medium capitalize"
                  :class="{
                    'text-yellow-600': app.status === 'pending',
                    'text-green-600': app.status === 'approved',
                    'text-red-600': app.status === 'rejected',
                  }"
                >
                  {{ app.status }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div v-if="app.status === 'pending'" class="flex gap-2">
                  <button
                    @click="approveApplication(app.id)"
                    class="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-xs font-bold rounded-lg transition-colors"
                  >
                    Approve
                  </button>
                  <button
                    @click="rejectApplication(app.id)"
                    class="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-lg transition-colors"
                  >
                    Reject
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </DashboardLayout>
</template>
