<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()

const stats = ref([
  {
    name: 'Total Departments',
    value: '...',
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    color: 'bg-emerald-600',
  },
  {
    name: 'Active Doctors',
    value: '...',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'bg-teal-600',
  },
  {
    name: 'Active Nurses',
    value: '...',
    icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    color: 'bg-emerald-500',
  },
  {
    name: 'Pending Apps',
    value: '...',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'bg-teal-500',
  },
])

const recentApplications = ref<any[]>([])
const recentAppointments = ref<any[]>([])
const isLoading = ref(true)

const loadStats = async () => {
  isLoading.value = true
  try {
    const [deptRes, docRes, nurseRes, appRes, apptRes] = await Promise.all([
      api.get('/departments'),
      api.get('/doctors/'),
      api.get('/nurses/'),
      api.get('/applications'),
      api.get('/appointments'),
    ])

    if (stats.value[0]) stats.value[0].value = (deptRes.data.data?.length || 0).toString()
    if (stats.value[1]) stats.value[1].value = (docRes.data.data?.length || 0).toString()
    if (stats.value[2]) stats.value[2].value = (nurseRes.data.data?.length || 0).toString()

    const allApps = appRes.data.data || []
    const pendingApps = allApps.filter((a: any) => a.status === 'pending').length
    if (stats.value[3]) stats.value[3].value = pendingApps.toString()

    // Recent activity — last 6 applications sorted newest first
    recentApplications.value = allApps
      .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 6)

    // Recent appointments
    recentAppointments.value = (apptRes.data.data || [])
      .sort(
        (a: any, b: any) =>
          new Date(b.created_at || b.appointment_date).getTime() -
          new Date(a.created_at || a.appointment_date).getTime(),
      )
      .slice(0, 5)
  } catch (error) {
    notification.error('Failed to load dashboard statistics')
    stats.value.forEach((s) => (s.value = 'N/A'))
  } finally {
    isLoading.value = false
  }
}

const getAppStatusColor = (status: string) => {
  switch (status) {
    case 'pending':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
    case 'approved':
      return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
    case 'rejected':
      return 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'
    default:
      return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
  }
}

const getRoleColor = (role: string) => {
  switch (role) {
    case 'doctor':
      return 'text-indigo-600 dark:text-indigo-400'
    case 'nurse':
      return 'text-teal-600 dark:text-teal-400'
    case 'patient':
      return 'text-emerald-600 dark:text-emerald-400'
    default:
      return 'text-gray-500 dark:text-slate-400'
  }
}

const normalizeDate = (dateString: string | null | undefined): string => {
  return dateString || ''
}

const formatDate = (ds: string) => {
  if (!ds) return '—'
  return new Date(normalizeDate(ds)).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const formatTime = (ds: string) => {
  if (!ds) return '—'
  return new Date(normalizeDate(ds)).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(loadStats)
</script>

<template>
  <PortalBase role="admin" title="Admin Overview" :stats="stats">
    <template #main>
      <!-- Recent Applications Activity -->
      <div class="flex items-center justify-between mb-8">
        <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
          <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
          Recent Applications
        </h3>
        <RouterLink
          to="/applications/management"
          class="text-xs font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest hover:underline"
        >
          View All
        </RouterLink>
      </div>

      <div v-if="isLoading" class="flex items-center justify-center py-16">
        <div
          class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
        ></div>
      </div>

      <div
        v-else-if="recentApplications.length === 0"
        class="flex flex-col items-center justify-center py-12 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border-2 border-dashed border-gray-100 dark:border-slate-800 overflow-hidden"
      >
        <div
          class="w-16 h-16 bg-white dark:bg-slate-900 rounded-2xl shadow-sm flex items-center justify-center mb-4 text-gray-300 dark:text-slate-700"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-8 w-8"
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
        <p class="text-sm font-bold text-gray-500 dark:text-slate-400">No applications yet</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="app in recentApplications"
          :key="app.id"
          class="flex items-center justify-between p-4 bg-gray-50 dark:bg-slate-800/40 rounded-2xl border border-gray-100 dark:border-slate-800 hover:border-emerald-500/20 transition-all"
        >
          <div class="flex items-center gap-4">
            <div
              class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center font-black text-emerald-600 text-sm"
            >
              {{ (app.patient_full_name || app.full_name || '?').charAt(0).toUpperCase() }}
            </div>
            <div>
              <p class="text-sm font-black text-gray-900 dark:text-white">
                {{ app.patient_full_name || 'Staff Application' }}
              </p>
              <p class="text-[10px] font-black uppercase tracking-widest mt-0.5">
                <span :class="getRoleColor(app.role_applied)">{{ app.role_applied }}</span>
                <span class="text-gray-400 mx-1">•</span>
                <span class="text-gray-400">{{ formatDate(app.created_at) }}</span>
              </p>
            </div>
          </div>
          <span
            :class="`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${getAppStatusColor(app.status)}`"
          >
            {{ app.status }}
          </span>
        </div>
      </div>

    </template>

    <template #sidebar>
      <!-- Quick Actions -->
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-8 shadow-premium"
      >
        <h3
          class="text-base font-black text-gray-900 dark:text-white mb-6 uppercase tracking-widest"
        >
          Quick Actions
        </h3>
        <div class="space-y-3">
          <RouterLink
            to="/admin/departments"
            class="flex items-center gap-3 p-4 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-800 hover:border-emerald-500/30 hover:bg-emerald-50/30 dark:hover:bg-emerald-900/10 transition-all group"
          >
            <div
              class="w-9 h-9 bg-emerald-100 dark:bg-emerald-900/30 rounded-xl flex items-center justify-center text-emerald-600 group-hover:scale-110 transition-transform"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5" />
              </svg>
            </div>
            <span class="text-sm font-black text-gray-700 dark:text-slate-300"
              >Manage Departments</span
            >
          </RouterLink>
          <RouterLink
            to="/admin/users"
            class="flex items-center gap-3 p-4 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-800 hover:border-emerald-500/30 hover:bg-emerald-50/30 dark:hover:bg-emerald-900/10 transition-all group"
          >
            <div
              class="w-9 h-9 bg-teal-100 dark:bg-teal-900/30 rounded-xl flex items-center justify-center text-teal-600 group-hover:scale-110 transition-transform"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
            <span class="text-sm font-black text-gray-700 dark:text-slate-300">Manage Users</span>
          </RouterLink>
          <RouterLink
            to="/applications/management"
            class="flex items-center gap-3 p-4 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-800 hover:border-amber-500/30 hover:bg-amber-50/30 dark:hover:bg-amber-900/10 transition-all group"
          >
            <div
              class="w-9 h-9 bg-amber-100 dark:bg-amber-900/30 rounded-xl flex items-center justify-center text-amber-600 group-hover:scale-110 transition-transform"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <span class="text-sm font-black text-gray-700 dark:text-slate-300"
              >Review Applications</span
            >
          </RouterLink>
          <RouterLink
            to="/admin/medicines"
            class="flex items-center gap-3 p-4 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-800 hover:border-indigo-500/30 hover:bg-indigo-50/30 dark:hover:bg-indigo-900/10 transition-all group"
          >
            <div
              class="w-9 h-9 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center text-indigo-600 group-hover:scale-110 transition-transform"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
                />
              </svg>
            </div>
            <span class="text-sm font-black text-gray-700 dark:text-slate-300"
              >Medicine Inventory</span
            >
          </RouterLink>
          <RouterLink
            to="/admin/orders"
            class="flex items-center gap-3 p-4 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-800 hover:border-rose-500/30 hover:bg-rose-50/30 dark:hover:bg-rose-900/10 transition-all group"
          >
            <div
              class="w-9 h-9 bg-rose-100 dark:bg-rose-900/30 rounded-xl flex items-center justify-center text-rose-600 group-hover:scale-110 transition-transform"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
            </div>
            <span class="text-sm font-black text-gray-700 dark:text-slate-300"
              >Pharmacy Orders</span
            >
          </RouterLink>
        </div>
      </div>

      <!-- Recent Appointments -->
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-8 shadow-premium mt-8"
      >
        <h3
          class="text-base font-black text-gray-900 dark:text-white mb-6 uppercase tracking-widest flex items-center gap-3"
        >
          <span class="h-1.5 w-4 bg-teal-600 rounded-full"></span>
          Recent Appointments
        </h3>
        <div v-if="isLoading" class="flex justify-center py-8">
          <div
            class="animate-spin rounded-full h-6 w-6 border-[3px] border-teal-600 border-t-transparent"
          ></div>
        </div>
        <div v-else-if="recentAppointments.length === 0" class="text-center py-6">
          <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">No appointments</p>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="apt in recentAppointments"
            :key="apt.id"
            class="p-4 bg-gray-50 dark:bg-slate-800/40 rounded-2xl border border-gray-100 dark:border-slate-800"
          >
            <div class="flex items-center justify-between mb-1">
              <p class="text-xs font-black text-gray-900 dark:text-white">
                {{ apt.patient_name || 'Unknown Patient' }}
              </p>
              <span
                :class="`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-widest ${
                  apt.status === 'confirmed'
                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                    : apt.status === 'pending'
                      ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                      : apt.status === 'completed'
                        ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400'
                        : 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'
                }`"
                >{{ apt.status }}</span
              >
            </div>
            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">
              {{ formatDate(apt.appointment_date) }} {{ formatTime(apt.appointment_date) }}
            </p>
          </div>
        </div>
      </div>
    </template>
  </PortalBase>
</template>
