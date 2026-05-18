<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
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
  department_name?: string
  // User profile details
  full_name?: string
  username?: string
  email?: string
  address?: string
  phone_number?: string
  pincode?: string
}

const notification = useNotificationStore()
const applications = ref<Application[]>([])
const isLoading = ref(false)
const selectedApplication = ref<Application | null>(null)
const isModalOpen = ref(false)
const rejectionReason = ref('')
const isProcessing = ref(false)

// Filters
const filters = ref({
  role: '',
  status: '',
  search: '',
})

// Pagination
const currentPage = ref(1)
const itemsPerPage = 10

const statsSummary = computed(() => {
  const roles = ['doctor', 'nurse', 'patient']
  const statuses = ['pending', 'approved', 'rejected']

  const summary: Record<string, any> = {}

  roles.forEach((role) => {
    summary[role] = {
      total: applications.value.filter((a) => a.role_applied === role).length,
      pending: applications.value.filter((a) => a.role_applied === role && a.status === 'pending')
        .length,
      approved: applications.value.filter((a) => a.role_applied === role && a.status === 'approved')
        .length,
      rejected: applications.value.filter((a) => a.role_applied === role && a.status === 'rejected')
        .length,
    }
  })

  return summary
})

const filteredApplications = computed(() => {
  return applications.value.filter((app) => {
    // Role filter
    const matchRole = !filters.value.role || app.role_applied === filters.value.role

    // Status filter
    const matchStatus = !filters.value.status || app.status === filters.value.status

    // Search filter (username, email, or full name)
    const searchLower = filters.value.search.toLowerCase()
    const matchSearch =
      !filters.value.search ||
      app.username?.toLowerCase().includes(searchLower) ||
      app.email?.toLowerCase().includes(searchLower) ||
      app.full_name?.toLowerCase().includes(searchLower)

    return matchRole && matchStatus && matchSearch
  })
})

const totalPages = computed(() => Math.ceil(filteredApplications.value.length / itemsPerPage))

const paginatedApplications = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredApplications.value.slice(start, end)
})

// Reset to page 1 when filters change
watch(
  filters,
  () => {
    currentPage.value = 1
  },
  { deep: true },
)

watch(isModalOpen, (newValue) => {
  if (newValue) {
    document.body.classList.add('overflow-hidden')
  } else {
    document.body.classList.remove('overflow-hidden')
  }
})

onUnmounted(() => {
  document.body.classList.remove('overflow-hidden')
})

const loadApplications = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/applications')
    applications.value = response.data.data || []
    console.log('Loaded applications:', applications.value)
  } catch (error) {
    notification.error('Failed to load applications')
  } finally {
    isLoading.value = false
  }
}

const openDetails = (app: Application) => {
  selectedApplication.value = app
  isModalOpen.value = true
}

const closeDetails = () => {
  isModalOpen.value = false
  selectedApplication.value = null
  rejectionReason.value = ''
}

const approveApplication = async (id: number) => {
  isProcessing.value = true
  try {
    await api.post(`/applications/${id}/approve`)
    notification.success('Application approved successfully')
    closeDetails()
    loadApplications()
  } catch (error: any) {
    notification.error(error.response?.data?.message || 'Failed to approve application')
  } finally {
    isProcessing.value = false
  }
}

const rejectApplication = async (id: number) => {
  if (!rejectionReason.value) {
    notification.error('Please provide a reason for rejection')
    return
  }

  isProcessing.value = true
  try {
    await api.post(`/applications/${id}/reject`, { reason: rejectionReason.value })
    notification.success('Application rejected')
    closeDetails()
    loadApplications()
  } catch (error: any) {
    notification.error(error.response?.data?.message || 'Failed to reject application')
  } finally {
    isProcessing.value = false
  }
}

onMounted(loadApplications)
</script>

<template>
  <DashboardLayout>
    <div class="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
      <div>
        <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none">
          Application Management
        </h1>
        <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
          Review and process role applications for doctors, nurses, and patients.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-4">
        <!-- Search Bar -->
        <div class="relative group">
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search username or email..."
            class="pl-12 pr-6 py-3.5 w-64 bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-2xl text-sm font-bold focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all dark:text-white shadow-premium"
          />
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-emerald-500 transition-colors"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>

        <!-- Role Filter -->
        <select
          v-model="filters.role"
          class="px-6 py-3.5 bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-2xl text-sm font-bold focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all dark:text-white shadow-premium cursor-pointer"
        >
          <option value="">All Roles</option>
          <option value="doctor">Doctors</option>
          <option value="nurse">Nurses</option>
          <option value="patient">Patients</option>
        </select>

        <!-- Status Filter -->
        <select
          v-model="filters.status"
          class="px-6 py-3.5 bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-2xl text-sm font-bold focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all dark:text-white shadow-premium cursor-pointer"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>
    </div>

    <!-- Stats Summary Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
      <div
        v-for="(data, role) in statsSummary"
        :key="role"
        class="bg-white dark:bg-slate-900 rounded-[2rem] border border-gray-100 dark:border-slate-800 p-6 shadow-premium group hover:-translate-y-1 transition-all duration-300"
      >
        <div class="flex items-center justify-between mb-4">
          <h3
            class="text-xs font-black uppercase tracking-[0.2em]"
            :class="{
              'text-teal-600': role === 'doctor',
              'text-emerald-600': role === 'nurse',
              'text-indigo-600': role === 'patient',
            }"
          >
            {{ role }}s
          </h3>
          <span
            class="text-[10px] font-black text-gray-400 bg-gray-50 dark:bg-slate-800 px-2 py-1 rounded-lg uppercase"
            >{{ data.total }} Total</span
          >
        </div>

        <div class="grid grid-cols-3 gap-2 text-center">
          <div class="flex flex-col">
            <span class="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-1"
              >Pending</span
            >
            <span class="text-lg font-black text-amber-500">{{ data.pending }}</span>
          </div>
          <div class="flex flex-col border-x border-gray-50 dark:border-slate-800 px-2">
            <span class="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-1"
              >Approved</span
            >
            <span class="text-lg font-black text-emerald-500">{{ data.approved }}</span>
          </div>
          <div class="flex flex-col">
            <span class="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-1"
              >Rejected</span
            >
            <span class="text-lg font-black text-rose-500">{{ data.rejected }}</span>
          </div>
        </div>
      </div>
    </div>

    <div
      class="glass rounded-[2.5rem] border border-white/40 dark:border-white/5 shadow-premium overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-700"
    >
      <div
        class="p-8 border-b border-gray-100 dark:border-white/5 flex justify-between items-center"
      >
        <h2 class="text-xl font-black text-gray-900 dark:text-white tracking-tight">
          Recent Applications
        </h2>
        <button
          @click="loadApplications"
          class="p-2.5 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 rounded-xl transition-all active:scale-95"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </button>
      </div>

      <div v-if="isLoading" class="p-20 text-center">
        <div
          class="animate-spin inline-block w-10 h-10 border-[3px] border-emerald-600 border-t-transparent rounded-full mb-6"
        ></div>
        <p class="text-sm font-bold text-gray-400 uppercase tracking-widest">Loading Records...</p>
      </div>

      <div v-else-if="applications.length === 0" class="p-20 text-center">
        <div
          class="w-20 h-20 bg-gray-50 dark:bg-slate-800 rounded-3xl flex items-center justify-center mx-auto mb-6 text-gray-300"
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <p class="text-lg font-bold text-gray-900 dark:text-white">No applications found.</p>
        <p class="text-sm text-gray-500">Wait for new users to apply for roles.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead
            class="bg-gray-50/50 dark:bg-slate-800/50 text-gray-400 dark:text-slate-500 text-[10px] uppercase font-black tracking-[0.2em]"
          >
            <tr>
              <th class="px-8 py-5">Applicant</th>
              <th class="px-8 py-5">Role Applied</th>
              <th class="px-8 py-5">Status</th>
              <th class="px-8 py-5 text-right">Orchestration</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-white/5">
            <tr
              v-for="app in paginatedApplications"
              :key="app.id"
              class="hover:bg-emerald-50/30 dark:hover:bg-emerald-900/10 transition-colors cursor-pointer group"
              @click="openDetails(app)"
            >
              <td class="px-8 py-6">
                <div class="flex items-center gap-4">
                  <div
                    class="h-10 w-10 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 font-black text-sm shadow-sm border border-emerald-200/50 dark:border-emerald-500/20 group-hover:scale-110 transition-transform"
                  >
                    {{ app.full_name?.charAt(0) || app.username?.charAt(0) }}
                  </div>
                  <div>
                    <p class="text-sm font-black text-gray-900 dark:text-white leading-tight">
                      {{ app.full_name || app.username }}
                    </p>
                    <p class="text-xs text-gray-500 mt-0.5">@{{ app.username }}</p>
                  </div>
                </div>
              </td>
              <td class="px-8 py-6">
                <span
                  class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border"
                  :class="{
                    'bg-emerald-50 text-emerald-700 border-emerald-100/50 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-500/20':
                      app.role_applied === 'patient',
                    'bg-teal-50 text-teal-700 border-teal-100/50 dark:bg-teal-900/20 dark:text-teal-400 dark:border-teal-500/20':
                      app.role_applied === 'doctor',
                    'bg-emerald-500 text-white border-emerald-600': app.role_applied === 'nurse',
                  }"
                >
                  {{ app.role_applied }}
                </span>
              </td>
              <td class="px-8 py-6">
                <span
                  class="inline-flex items-center gap-2 text-[10px] font-black uppercase tracking-widest"
                  :class="{
                    'text-yellow-600': app.status === 'pending',
                    'text-green-600': app.status === 'approved',
                    'text-red-600': app.status === 'rejected',
                  }"
                >
                  <span
                    class="h-2 w-2 rounded-full shadow-sm"
                    :class="{
                      'bg-yellow-500 animate-pulse': app.status === 'pending',
                      'bg-green-500': app.status === 'approved',
                      'bg-red-500': app.status === 'rejected',
                    }"
                  ></span>
                  {{ app.status }}
                </span>
              </td>
              <td class="px-8 py-6 text-right">
                <button
                  class="text-emerald-600 dark:text-emerald-400 text-xs font-black uppercase tracking-[0.15em] hover:underline flex items-center gap-1 ml-auto"
                >
                  Details
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-3 w-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="3"
                  >
                    <path d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Controls -->
      <div
        v-if="totalPages > 1"
        class="p-8 border-t border-gray-100 dark:border-white/5 flex flex-col sm:flex-row items-center justify-between gap-6 bg-gray-50/30 dark:bg-slate-800/30"
      >
        <div class="text-xs font-black text-gray-400 uppercase tracking-widest">
          Showing
          <span class="text-emerald-600">{{ (currentPage - 1) * itemsPerPage + 1 }}</span> to
          <span class="text-emerald-600">{{
            Math.min(currentPage * itemsPerPage, filteredApplications.length)
          }}</span>
          of <span class="text-emerald-600">{{ filteredApplications.length }}</span> entries
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="p-2.5 bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-xl text-gray-400 hover:text-emerald-600 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm active:scale-95"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="3"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div
            class="flex items-center gap-1 px-4 py-2 bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-xl shadow-sm"
          >
            <span class="text-xs font-black text-emerald-600">{{ currentPage }}</span>
            <span class="text-[10px] font-black text-gray-300 uppercase tracking-widest mx-1"
              >of</span
            >
            <span class="text-xs font-black text-gray-400">{{ totalPages }}</span>
          </div>

          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="p-2.5 bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-xl text-gray-400 hover:text-emerald-600 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm active:scale-95"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="3"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Application Details Modal -->
    <div
      v-if="isModalOpen && selectedApplication"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-md"
      @click.self="closeDetails"
    >
      <div
        class="glass w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl rounded-[2.5rem] flex flex-col animate-in fade-in zoom-in-95 duration-300"
      >
        <div
          class="p-8 border-b border-gray-100 dark:border-white/5 flex justify-between items-center"
        >
          <div>
            <h3
              class="text-2xl font-black text-gray-900 dark:text-white tracking-tight leading-none"
            >
              Application Profile
            </h3>
            <p class="text-xs text-gray-500 mt-1 uppercase font-black tracking-widest">
              Reference ID: #APP-{{ selectedApplication.id }}
            </p>
          </div>
          <button
            @click="closeDetails"
            class="p-2 text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-800 rounded-xl transition-all"
          >
            <svg
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-8 overflow-y-auto flex-1">
          <!-- Applicant Info -->
          <div class="grid grid-cols-2 gap-8 mb-10">
            <div>
              <label
                class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                >Full Name</label
              >
              <p class="text-gray-900 dark:text-white font-bold text-lg leading-tight">
                {{ selectedApplication.full_name }}
              </p>
            </div>
            <div>
              <label
                class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                >User Handle</label
              >
              <p class="text-emerald-600 dark:text-emerald-400 font-black text-lg leading-tight">
                @{{ selectedApplication.username }}
              </p>
            </div>
            <div>
              <label
                class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                >Email Address</label
              >
              <p class="text-gray-900 dark:text-white font-bold">
                {{ selectedApplication.email }}
              </p>
            </div>
            <div>
              <label
                class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                >Phone Contact</label
              >
              <p class="text-gray-900 dark:text-white font-bold">
                {{ selectedApplication.phone_number }}
              </p>
            </div>
            <div class="col-span-2">
              <label
                class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                >Residential Address</label
              >
              <p class="text-gray-900 dark:text-white font-bold">
                {{ selectedApplication.address }}, {{ selectedApplication.pincode }}
              </p>
            </div>
          </div>

          <!-- Application Info -->
          <div
            class="bg-emerald-50/50 dark:bg-emerald-900/10 rounded-3xl p-8 mb-10 border border-emerald-100 dark:border-emerald-500/10"
          >
            <h4
              class="text-xs font-black text-gray-900 dark:text-white mb-6 flex items-center gap-3 uppercase tracking-widest"
            >
              <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
              Clinical Credentials
            </h4>
            <div class="grid grid-cols-2 gap-8">
              <div>
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Role Applied</label
                >
                <span
                  class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border"
                  :class="{
                    'bg-emerald-100 text-emerald-700 border-emerald-200/50':
                      selectedApplication.role_applied === 'patient',
                    'bg-teal-100 text-teal-700 border-teal-200/50':
                      selectedApplication.role_applied === 'doctor',
                    'bg-emerald-500 text-white border-emerald-600':
                      selectedApplication.role_applied === 'nurse',
                  }"
                >
                  {{ selectedApplication.role_applied }}
                </span>
              </div>
              <div>
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Submission Date</label
                >
                <p class="text-gray-900 dark:text-white font-bold">
                  {{ new Date(selectedApplication.created_at).toLocaleDateString() }}
                </p>
              </div>
              <div v-if="selectedApplication.specialization">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Specialization</label
                >
                <p class="text-gray-900 dark:text-white font-bold">
                  {{ selectedApplication.specialization }}
                </p>
              </div>
              <div v-if="selectedApplication.experience_years !== undefined">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Experience</label
                >
                <p class="text-gray-900 dark:text-white font-bold">
                  {{ selectedApplication.experience_years }} Years
                </p>
              </div>
              <div v-if="selectedApplication.license_number">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Medical License</label
                >
                <p
                  class="text-emerald-600 dark:text-emerald-400 font-black tracking-widest font-mono"
                >
                  {{ selectedApplication.license_number }}
                </p>
              </div>
              <div v-if="selectedApplication.department_id">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Department</label
                >
                <p class="text-gray-900 dark:text-white font-bold">
                  {{ selectedApplication.department_name || selectedApplication.department_id }}
                </p>
              </div>
              <div class="col-span-2">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Professional Statement</label
                >
                <p class="text-gray-900 dark:text-white text-sm leading-relaxed font-medium">
                  {{ selectedApplication.reason }}
                </p>
              </div>
            </div>
          </div>

          <!-- Rejection Reason Input -->
          <div v-if="selectedApplication.status === 'pending'" class="mt-4">
            <label
              class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-3"
              >Rejection Rationale (Mandatory for rejection)</label
            >
            <textarea
              v-model="rejectionReason"
              rows="3"
              class="w-full bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-2xl p-4 text-sm focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all dark:text-white"
              placeholder="Provide clinical or administrative grounds for rejection..."
            ></textarea>
          </div>
        </div>

        <div
          class="p-8 border-t border-gray-100 dark:border-white/5 bg-gray-50 dark:bg-slate-900/30 flex justify-end gap-4"
        >
          <button
            @click="closeDetails"
            class="px-8 py-3 text-xs font-black text-gray-400 hover:text-gray-900 dark:hover:text-white uppercase tracking-widest transition-colors"
          >
            Cancel
          </button>

          <template v-if="selectedApplication.status === 'pending'">
            <button
              @click="rejectApplication(selectedApplication.id)"
              :disabled="isProcessing"
              class="px-8 py-3 bg-red-50 text-red-600 hover:bg-red-100 text-xs font-black rounded-2xl transition-all disabled:opacity-50 uppercase tracking-widest"
            >
              Reject
            </button>
            <button
              @click="approveApplication(selectedApplication.id)"
              :disabled="isProcessing"
              class="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-black rounded-2xl shadow-xl shadow-emerald-500/25 transition-all disabled:opacity-50 flex items-center gap-2 uppercase tracking-widest active:scale-95"
            >
              <span
                v-if="isProcessing"
                class="h-3 w-3 border-2 border-white/30 border-t-white animate-spin rounded-full"
              ></span>
              {{ isProcessing ? 'Processing...' : 'Approve Application' }}
            </button>
          </template>
          <div
            v-else
            class="text-xs font-black uppercase tracking-widest italic"
            :class="selectedApplication.status === 'approved' ? 'text-green-600' : 'text-red-600'"
          >
            Application {{ selectedApplication.status }}
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
