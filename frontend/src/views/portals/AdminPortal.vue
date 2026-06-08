<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'
import { Chart } from 'chart.js/auto'
import UpcomingEvents from '../../components/UpcomingEvents.vue'

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

const adminAnalyticsData = ref<any>(null)
const isLoadingAnalytics = ref(false)

const revenueCanvasRef = ref<HTMLCanvasElement | null>(null)
const deptVolumeCanvasRef = ref<HTMLCanvasElement | null>(null)

let revenueChart: Chart | null = null
let deptVolumeChart: Chart | null = null

const fetchAdminAnalytics = async () => {
  isLoadingAnalytics.value = true
  try {
    const res = await api.get('/analytics/admin')
    adminAnalyticsData.value = res.data.data
  } catch (err) {
    console.error('Failed to load admin analytics', err)
  } finally {
    isLoadingAnalytics.value = false
    if (adminAnalyticsData.value) {
      setTimeout(() => {
        renderAdminCharts()
      }, 50)
    }
  }
}

const renderAdminCharts = () => {
  const isDark = document.documentElement.classList.contains('dark')
  const textColor = isDark ? '#94a3b8' : '#475569'
  const gridColor = isDark ? 'rgba(71, 85, 105, 0.4)' : 'rgba(203, 213, 225, 0.9)'

  // 1. Revenue Chart
  if (revenueCanvasRef.value) {
    if (revenueChart) revenueChart.destroy()
    const rev = adminAnalyticsData.value.revenue
    revenueChart = new Chart(revenueCanvasRef.value, {
      type: 'doughnut',
      data: {
        labels: ['Consultation', 'Pharmacy Store'],
        datasets: [
          {
            data: [rev.consultation, rev.pharmacy],
            backgroundColor: ['#10b981', '#6366f1'],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: textColor, padding: 15 },
          },
        },
      },
    })
  }

  // 2. Department Volume Chart
  if (deptVolumeCanvasRef.value) {
    if (deptVolumeChart) deptVolumeChart.destroy()
    deptVolumeChart = new Chart(deptVolumeCanvasRef.value, {
      type: 'bar',
      data: {
        labels: adminAnalyticsData.value.department_volume.labels,
        datasets: [
          {
            label: 'Appointments',
            data: adminAnalyticsData.value.department_volume.data,
            backgroundColor: '#3b82f6',
            borderRadius: 8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
        },
        scales: {
          x: { ticks: { color: textColor }, grid: { display: false } },
          y: { ticks: { color: textColor }, grid: { color: gridColor } },
        },
      },
    })
  }
}

onBeforeUnmount(() => {
  if (revenueChart) revenueChart.destroy()
  if (deptVolumeChart) deptVolumeChart.destroy()
})

onMounted(async () => {
  await loadStats()
  await fetchAdminAnalytics()
})
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

      <!-- Analytics Charts Panel -->
      <div class="h-px bg-gray-100 dark:bg-slate-800/80 my-8"></div>

      <div class="flex items-center justify-between mb-8">
        <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
          <span class="h-1.5 w-6 bg-blue-600 rounded-full"></span>
          Hospital Performance Analytics
        </h3>
      </div>

      <div
        v-if="isLoadingAnalytics"
        class="flex flex-col items-center justify-center py-16 space-y-4"
      >
        <div
          class="animate-spin rounded-full h-10 w-10 border-[3px] border-blue-600 border-t-transparent"
        ></div>
        <p class="text-xs text-gray-400 dark:text-slate-500 uppercase tracking-widest font-black">
          Generating analytics...
        </p>
      </div>

      <div v-else-if="adminAnalyticsData" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Revenue split -->
        <div
          class="bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-[2rem] p-6 shadow-premium relative"
        >
          <h4
            class="text-xs font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-6"
          >
            Hospital Revenue Split
          </h4>
          <div class="h-64 relative">
            <canvas ref="revenueCanvasRef"></canvas>
          </div>
        </div>

        <!-- Department volume -->
        <div
          class="bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-[2rem] p-6 shadow-premium relative"
        >
          <h4
            class="text-xs font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-6"
          >
            Patient Volume by Department
          </h4>
          <div class="h-64 relative">
            <canvas ref="deptVolumeCanvasRef"></canvas>
          </div>
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

      <!-- Upcoming Events -->
      <UpcomingEvents class="mt-8" />
    </template>
  </PortalBase>
</template>
