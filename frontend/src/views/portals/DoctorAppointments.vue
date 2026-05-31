<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()
const appointments = ref<any[]>([])
const isLoading = ref(true)
const viewMode = ref<'grid' | 'list'>('grid')
const recentlyUpdatedId = ref<string | null>(null)

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
    recentlyUpdatedId.value = appointmentId
    setTimeout(() => {
      recentlyUpdatedId.value = null
    }, 2200)
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

const getFeeDisplay = (apt: any) => {
  if (apt.appointment_type === 'vitals_check') return 'Vitals Screening — No Charge'
  if (apt.consultation_fee != null && apt.consultation_fee > 0)
    return `$${Number(apt.consultation_fee).toFixed(2)}`
  return null
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
      <!-- Header row -->
      <div class="flex items-center justify-between mb-10 flex-wrap gap-4">
        <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
          <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
          Scheduled Consultations
          <span
            v-if="!isLoading && appointments.length"
            class="ml-1 text-xs bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 px-2 py-0.5 rounded-full font-black"
          >
            {{ appointments.length }}
          </span>
        </h3>

        <div class="flex items-center gap-3">
          <!-- View toggle -->
          <div
            class="flex items-center p-1 bg-gray-100 dark:bg-slate-800 rounded-xl border border-gray-200/50 dark:border-slate-700/50"
          >
            <button
              @click="viewMode = 'grid'"
              :class="`p-1.5 rounded-lg transition-all ${
                viewMode === 'grid'
                  ? 'bg-white dark:bg-slate-900 text-emerald-600 shadow-sm'
                  : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
              }`"
              title="Grid view"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                />
              </svg>
            </button>
            <button
              @click="viewMode = 'list'"
              :class="`p-1.5 rounded-lg transition-all ${
                viewMode === 'list'
                  ? 'bg-white dark:bg-slate-900 text-emerald-600 shadow-sm'
                  : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
              }`"
              title="List view"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M4 6h16M4 10h16M4 14h16M4 18h16"
                />
              </svg>
            </button>
          </div>

          <button
            @click="loadData"
            class="text-xs font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest hover:underline"
          >
            Refresh
          </button>
        </div>
      </div>

      <!-- ── Skeleton Loading State ──────────────────────────────── -->
      <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="i in 4"
          :key="i"
          class="bg-gray-50 dark:bg-slate-800/40 p-8 rounded-[2rem] border border-gray-100 dark:border-slate-800"
        >
          <div class="flex items-center gap-4 mb-6">
            <div class="skeleton w-14 h-14 rounded-2xl"></div>
            <div class="flex-1 space-y-2">
              <div class="skeleton h-4 w-3/4"></div>
              <div class="skeleton h-3 w-1/2"></div>
            </div>
            <div class="skeleton h-6 w-20 rounded-lg"></div>
          </div>
          <div class="space-y-3 mb-6">
            <div class="skeleton h-3 w-2/3"></div>
            <div class="skeleton h-12 w-full rounded-xl"></div>
          </div>
          <div class="skeleton h-11 w-full rounded-xl"></div>
        </div>
      </div>

      <!-- ── Empty State ─────────────────────────────────────────── -->
      <div
        v-else-if="appointments.length === 0"
        class="flex flex-col items-center justify-center py-20 bg-gray-50/50 dark:bg-slate-800/30 rounded-[2.5rem] border-2 border-dashed border-gray-100 dark:border-slate-800 text-center px-6"
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
          Your schedule is currently empty. New appointments will appear here when patients book.
        </p>
      </div>

      <!-- ── GRID VIEW ───────────────────────────────────────────── -->
      <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="apt in appointments"
          :key="apt.id"
          :class="`card-animate group bg-gray-50 dark:bg-slate-800/50 p-8 rounded-[2rem] border transition-all duration-300 shadow-sm hover:shadow-premium ${
            recentlyUpdatedId === apt.id
              ? 'success-pulse border-emerald-400 dark:border-emerald-500'
              : 'border-gray-100 dark:border-slate-800 hover:border-emerald-500/30'
          }`"
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
                  {{
                    apt.appointment_type === 'vitals_check' ? 'Vitals Screening' : 'Consultation'
                  }}
                </p>
              </div>
            </div>
            <div class="flex flex-col items-end gap-1.5 flex-shrink-0">
              <span
                :class="`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest ${getStatusColor(apt.status)}`"
              >
                {{ apt.status }}
              </span>
              <span
                v-if="!apt.vitals_checked && apt.appointment_type !== 'vitals_check'"
                class="px-2.5 py-0.5 bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 rounded-lg text-[9px] font-bold uppercase tracking-wider border border-amber-200/30 dark:border-amber-500/10 flex items-center gap-1"
              >
                <span class="h-1 w-1 bg-amber-500 rounded-full animate-pulse"></span>
                Awaiting Vitals
              </span>
              <span
                v-else-if="apt.vitals_checked"
                class="px-2.5 py-0.5 bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 rounded-lg text-[9px] font-bold uppercase tracking-wider border border-emerald-200/30 dark:border-emerald-500/10 flex items-center gap-1"
              >
                <span class="h-1 w-1 bg-emerald-500 rounded-full"></span>
                Vitals Captured
              </span>
            </div>
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
            <!-- Consultation Fee -->
            <div
              v-if="getFeeDisplay(apt)"
              class="flex items-center gap-2 text-gray-500 dark:text-slate-400"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span
                :class="`text-xs font-bold uppercase tracking-wider ${
                  apt.appointment_type === 'vitals_check' ? 'text-teal-600 dark:text-teal-400' : ''
                }`"
              >
                {{ getFeeDisplay(apt) }}
              </span>
            </div>
            <!-- Reason for visit -->
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
              :disabled="!apt.vitals_checked"
              :class="`w-full py-3 text-white rounded-xl text-[10px] font-black uppercase tracking-widest transition-all active:scale-95 flex items-center justify-center gap-2 ${
                apt.vitals_checked
                  ? 'bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-600/20'
                  : 'bg-slate-400 dark:bg-slate-700 opacity-60 cursor-not-allowed shadow-none'
              }`"
            >
              <svg
                v-if="!apt.vitals_checked"
                xmlns="http://www.w3.org/2000/svg"
                class="h-3.5 w-3.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="3"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
              <span>{{
                apt.vitals_checked ? 'Mark as Completed' : 'Locked — Awaiting Vitals'
              }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- ── LIST VIEW ───────────────────────────────────────────── -->
      <div v-else class="space-y-2">
        <div
          v-for="apt in appointments"
          :key="apt.id"
          :class="`card-animate flex items-center justify-between gap-4 px-6 py-4 rounded-2xl border transition-all duration-200 hover:shadow-sm ${
            recentlyUpdatedId === apt.id
              ? 'success-pulse bg-emerald-50/50 dark:bg-emerald-900/10 border-emerald-300 dark:border-emerald-700'
              : 'bg-gray-50 dark:bg-slate-800/40 border-gray-100 dark:border-slate-800 hover:border-emerald-500/20'
          }`"
        >
          <!-- Avatar + name -->
          <div class="flex items-center gap-3 min-w-0 flex-1">
            <div
              class="w-10 h-10 rounded-xl bg-white dark:bg-slate-900 flex items-center justify-center shadow-sm text-emerald-600 font-black border border-gray-100 dark:border-slate-800 flex-shrink-0"
            >
              {{ apt.patient_name?.charAt(0) || 'P' }}
            </div>
            <div class="min-w-0">
              <h4 class="font-black text-gray-900 dark:text-white text-sm truncate">
                {{ apt.patient_name }}
              </h4>
              <p
                class="text-[10px] text-gray-400 dark:text-slate-500 font-bold uppercase tracking-wider truncate"
              >
                {{ formatDate(apt.appointment_date) }}
                <span v-if="apt.reason"> · "{{ apt.reason }}"</span>
              </p>
            </div>
          </div>

          <!-- Type + fee badge -->
          <div class="hidden md:flex flex-col items-end gap-1 flex-shrink-0 w-40">
            <span
              :class="`text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full ${
                apt.appointment_type === 'vitals_check'
                  ? 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400'
                  : 'bg-gray-100 text-gray-600 dark:bg-slate-800 dark:text-slate-400'
              }`"
            >
              {{ apt.appointment_type === 'vitals_check' ? 'Vitals Only' : 'Consultation' }}
            </span>
            <span
              v-if="getFeeDisplay(apt)"
              class="text-[10px] font-bold text-gray-400 dark:text-slate-500"
            >
              {{ getFeeDisplay(apt) }}
            </span>
          </div>

          <!-- Vitals badge -->
          <div class="flex-shrink-0">
            <span
              v-if="!apt.vitals_checked && apt.appointment_type !== 'vitals_check'"
              class="px-2.5 py-1 bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 rounded-lg text-[9px] font-bold uppercase tracking-wider flex items-center gap-1"
            >
              <span class="h-1 w-1 bg-amber-500 rounded-full animate-pulse"></span>
              Vitals
            </span>
            <span
              v-else-if="apt.vitals_checked"
              class="px-2.5 py-1 bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 rounded-lg text-[9px] font-bold uppercase tracking-wider flex items-center gap-1"
            >
              <span class="h-1 w-1 bg-emerald-500 rounded-full"></span>
              Ready
            </span>
          </div>

          <!-- Status badge -->
          <span
            :class="`flex-shrink-0 px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest ${getStatusColor(apt.status)}`"
          >
            {{ apt.status }}
          </span>

          <!-- Actions -->
          <div class="flex items-center gap-2 flex-shrink-0">
            <template v-if="apt.status === 'pending'">
              <button
                @click="updateStatus(apt.id, 'confirmed')"
                class="px-3 py-2 bg-emerald-600 text-white rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-emerald-700 transition-all"
              >
                Confirm
              </button>
              <button
                @click="updateStatus(apt.id, 'cancelled')"
                class="px-3 py-2 bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-rose-600 hover:text-white transition-all"
              >
                Cancel
              </button>
            </template>
            <button
              v-if="apt.status === 'confirmed'"
              @click="updateStatus(apt.id, 'completed')"
              :disabled="!apt.vitals_checked"
              :class="`px-3 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 ${
                apt.vitals_checked
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                  : 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
              }`"
            >
              <svg
                v-if="!apt.vitals_checked"
                xmlns="http://www.w3.org/2000/svg"
                class="h-3 w-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="3"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
              Complete
            </button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
