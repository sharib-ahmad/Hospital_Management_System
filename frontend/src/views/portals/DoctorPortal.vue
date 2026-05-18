<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()
const appointments = ref<any[]>([])
const isLoading = ref(true)

const stats = ref([
  {
    name: "Today's Appointments",
    value: '0',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    color: 'bg-emerald-600',
  },
  {
    name: 'Total Patients',
    value: '0',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    color: 'bg-teal-600',
  },
  {
    name: 'Pending Applications',
    value: '0',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'bg-emerald-500',
  },
  {
    name: 'Completed Today',
    value: '0',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'bg-teal-500',
  },
])

const loadData = async () => {
  isLoading.value = true
  try {
    const [appRes, appointRes] = await Promise.all([
      api.get('/applications'),
      api.get('/appointments'),
    ])

    const pendingApps = (appRes.data.data || []).filter((a: any) => a.status === 'pending').length
    stats.value[2].value = pendingApps.toString()

    appointments.value = appointRes.data.data || []

    // Calculate stats from appointments
    const today = new Date().toDateString()
    const todayAppointments = appointments.value.filter(
      (a) => new Date(a.appointment_date).toDateString() === today,
    )
    stats.value[0].value = todayAppointments.length.toString()

    const completedToday = todayAppointments.filter((a) => a.status === 'completed').length
    stats.value[3].value = completedToday.toString()

    // Unique patients
    const uniquePatients = new Set(appointments.value.map((a) => a.patient_id)).size
    stats.value[1].value = uniquePatients.toString()
  } catch (error) {
    notification.error('Failed to load dashboard data')
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

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
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
  <PortalBase role="doctor" title="Doctor Dashboard" :stats="stats">
    <template #main>
      <div class="flex items-center justify-between mb-10">
        <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
          <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
          Quick Overview
        </h3>
        <RouterLink
          to="/doctor/appointments"
          class="text-xs font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest hover:underline"
          >View Full Schedule</RouterLink
        >
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
        <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
          No upcoming consultations
        </h4>
        <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium">
          When patients book appointments, they will appear here for your review.
        </p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="apt in appointments.slice(0, 5)"
          :key="apt.id"
          class="group bg-gray-50 dark:bg-slate-800/50 p-6 rounded-3xl border border-gray-100 dark:border-slate-800 hover:border-emerald-500/30 transition-all duration-300"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div
                class="w-12 h-12 rounded-2xl bg-white dark:bg-slate-900 flex items-center justify-center shadow-sm text-emerald-600 font-bold border border-gray-100 dark:border-slate-800"
              >
                {{ apt.patient_name?.charAt(0) || 'P' }}
              </div>
              <div>
                <h4 class="font-black text-gray-900 dark:text-white">{{ apt.patient_name }}</h4>
                <p class="text-[10px] text-gray-500 font-black uppercase tracking-widest">
                  {{ formatDate(apt.appointment_date) }}
                </p>
              </div>
            </div>
            <span
              :class="`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${getStatusColor(apt.status)}`"
            >
              {{ apt.status }}
            </span>
          </div>
        </div>

        <div class="pt-6 text-center">
          <RouterLink
            to="/doctor/appointments"
            class="inline-flex items-center gap-2 text-[10px] font-black text-gray-400 hover:text-emerald-600 uppercase tracking-widest transition-colors group"
          >
            Manage all appointments
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4 group-hover:translate-x-1 transition-transform"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="3"
            >
              <path d="M9 5l7 7-7 7" />
            </svg>
          </RouterLink>
        </div>
      </div>
    </template>
  </PortalBase>
</template>
