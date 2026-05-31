<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()
const appointments = ref<any[]>([])
const isLoading = ref(true)

const loadData = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/appointments')
    appointments.value = res.data.data || []
  } catch (error) {
    notification.error('Failed to load appointments')
  } finally {
    isLoading.value = false
  }
}

const updateStatus = async (appointmentId: string, status: string) => {
  try {
    await api.put(`/appointments/${appointmentId}`, { status })
    notification.success(`Appointment ${status} successfully`)
    loadData()
  } catch (error) {
    notification.error('Failed to update appointment status')
  }
}

const normalizeDate = (dateString: string | null | undefined): string => {
  return dateString || ''
}

const formatDate = (dateString: string) => {
  const date = new Date(normalizeDate(dateString))
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
    case 'confirmed':
      return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
    case 'cancelled':
      return 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'
    case 'completed':
      return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400'
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'
  }
}

onMounted(loadData)
</script>

<template>
  <DashboardLayout>
    <div class="mb-12">
      <div class="flex items-center gap-3 mb-2">
        <span
          class="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest border border-emerald-100 dark:border-emerald-500/20"
        >
          Clinical Operations
        </span>
      </div>
      <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">
        Appointment Management
      </h1>
      <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
        Review, confirm, and manage your patient consultation schedule.
      </p>
    </div>

    <div
      class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-10 shadow-premium"
    >
      <div class="flex items-center justify-between mb-10">
        <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
          <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
          Scheduled Consultations
        </h3>
        <button
          @click="loadData"
          class="text-xs font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest hover:underline"
        >
          Refresh List
        </button>
      </div>

      <div v-if="isLoading" class="flex items-center justify-center py-20">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600"></div>
      </div>

      <div
        v-else-if="appointments.length === 0"
        class="flex flex-col items-center justify-center py-20 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border-2 border-dashed border-gray-100 dark:border-slate-800"
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
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
        <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">No appointments found</h4>
        <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium">
          Your schedule is currently empty. New appointments will appear here.
        </p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="apt in appointments"
          :key="apt.id"
          class="group bg-gray-50 dark:bg-slate-800/50 p-8 rounded-[2rem] border border-gray-100 dark:border-slate-800 hover:border-emerald-500/30 transition-all duration-300 shadow-sm hover:shadow-premium"
        >
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-4">
              <div
                class="w-14 h-14 rounded-2xl bg-white dark:bg-slate-900 flex items-center justify-center shadow-sm text-emerald-600 font-black text-xl border border-gray-100 dark:border-slate-800"
              >
                {{ apt.patient_name?.charAt(0) || 'P' }}
              </div>
              <div>
                <h4 class="text-lg font-black text-gray-900 dark:text-white leading-tight">
                  {{ apt.patient_name }}
                </h4>
                <p
                  class="text-[10px] text-emerald-600 dark:text-emerald-400 font-black uppercase tracking-widest mt-0.5"
                >
                  Patient ID: {{ apt.patient_id?.substring(0, 8) }}...
                </p>
              </div>
            </div>
            <span
              :class="`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest ${getStatusColor(apt.status)}`"
            >
              {{ apt.status }}
            </span>
          </div>

          <div class="space-y-4 mb-8">
            <div class="flex items-center gap-3 text-gray-500 dark:text-slate-400">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <span class="text-xs font-bold uppercase tracking-wider">{{
                formatDate(apt.appointment_date)
              }}</span>
            </div>
            <div
              v-if="apt.reason"
              class="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-gray-100 dark:border-slate-800"
            >
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">
                Reason for visit
              </p>
              <p
                class="text-xs text-gray-600 dark:text-slate-300 font-medium leading-relaxed italic"
              >
                "{{ apt.reason }}"
              </p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <template v-if="apt.status === 'pending'">
              <button
                @click="updateStatus(apt.id, 'confirmed')"
                class="flex-1 py-3 bg-emerald-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-600/20 active:scale-95"
              >
                Confirm
              </button>
              <button
                @click="updateStatus(apt.id, 'cancelled')"
                class="flex-1 py-3 bg-rose-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-rose-700 transition-all shadow-lg shadow-rose-600/20 active:scale-95"
              >
                Cancel
              </button>
            </template>

            <button
              v-if="apt.status === 'confirmed'"
              @click="updateStatus(apt.id, 'completed')"
              class="w-full py-3 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-600/20 active:scale-95"
            >
              Mark as Completed
            </button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
