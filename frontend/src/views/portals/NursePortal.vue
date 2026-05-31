<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'
import FormField from '../../components/FormField.vue'

const notification = useNotificationStore()
const route = useRoute()

// ─── State ───────────────────────────────────────────────────────────────────
const isLoading = ref(true)
const activeTab = ref<'queue' | 'patients' | 'vitals' | 'profile'>('queue')

// Sync tab with route path
const syncTabWithRoute = () => {
  if (route.path === '/nurse/patients') {
    activeTab.value = 'patients'
  } else if (route.path === '/nurse/vitals') {
    activeTab.value = 'vitals'
  } else if (route.path === '/nurse/profile') {
    activeTab.value = 'profile'
  } else {
    activeTab.value = 'queue'
  }
}

// Watch for route changes
watch(
  () => route.path,
  () => {
    syncTabWithRoute()
  },
  { immediate: true },
)

const patients = ref<any[]>([])
const appointments = ref<any[]>([])
const departments = ref<any[]>([])
const nurseProfile = ref<any>(null)

// Vitals form
const vitalsPatientId = ref('')
const vitalsAppointmentId = ref('')
const vitalsSystolic = ref<number | ''>('')
const vitalsDiastolic = ref<number | ''>('')
const vitalsBloodSugar = ref<number | ''>('')
const vitalsPulse = ref<number | ''>('')
const vitalsTemp = ref<number | ''>('')
const vitalsRespiration = ref<number | ''>('')
const vitalsNotes = ref('')
const vitalsSubmitting = ref(false)
const lastRecordedVitals = ref<any>(null)
const recentlyRecordedPatientId = ref<string | null>(null)

// Referral section
const referToDoctor = ref(false)
const vitalsReferToDept = ref('')

// Patients tab search
const patientSearch = ref('')

// Profile edit modal
const showEditModal = ref(false)
const editShift = ref('')
const editIsAvailable = ref(true)
const editExperienceYears = ref<number | ''>('')
const editSubmitting = ref(false)

// ─── Stats ────────────────────────────────────────────────────────────────────
const stats = ref([
  {
    name: 'Awaiting Vitals',
    value: '0',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'bg-amber-500',
  },
  {
    name: 'Checkup Requests',
    value: '0',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'bg-teal-600',
  },
  {
    name: 'Total Patients',
    value: '0',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'bg-emerald-600',
  },
  {
    name: 'My Shift',
    value: '—',
    icon: 'M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2',
    color: 'bg-teal-500',
  },
])

// ─── Computed Queues ──────────────────────────────────────────────────────────
const awaitingVitalsQueue = computed(() => {
  return appointments.value.filter((a: any) => a.status === 'confirmed' && !a.vitals_checked)
})

const pendingCheckupRequests = computed(() => {
  return appointments.value.filter(
    (a: any) => a.appointment_type === 'vitals_check' && a.status === 'pending',
  )
})

const filteredPatients = computed(() => {
  const q = patientSearch.value.toLowerCase().trim()
  if (!q) return patients.value
  return patients.value.filter((p) => p.full_name?.toLowerCase().includes(q))
})

const isCurrentAppointmentVitalsCheck = computed(() => {
  if (!vitalsAppointmentId.value) return true
  const appt = appointments.value.find((a) => a.id === vitalsAppointmentId.value)
  return appt ? appt.appointment_type === 'vitals_check' : true
})

// ─── Data Loading ─────────────────────────────────────────────────────────────
const loadData = async () => {
  isLoading.value = true
  try {
    const [patientsRes, apptsRes, deptsRes, nurseRes] = await Promise.all([
      api.get('/patients/'),
      api.get('/appointments'),
      api.get('/departments'),
      api.get('/nurses/me'),
    ])

    patients.value = patientsRes.data.data || []
    appointments.value = apptsRes.data.data || []
    departments.value = deptsRes.data.data || []

    // Update stats values
    if (stats.value[0]) stats.value[0].value = awaitingVitalsQueue.value.length.toString()
    if (stats.value[1]) stats.value[1].value = pendingCheckupRequests.value.length.toString()
    if (stats.value[2]) stats.value[2].value = patients.value.length.toString()

    nurseProfile.value = nurseRes.data.data || nurseRes.data
    const shift = nurseProfile.value?.shift
    if (stats.value[3]) {
      stats.value[3].value = shift ? shift.charAt(0).toUpperCase() + shift.slice(1) : '—'
    }
  } catch (error) {
    notification.error('Failed to load dashboard data')
  } finally {
    isLoading.value = false
  }
}

// ─── Vitals ───────────────────────────────────────────────────────────────────
const switchToVitals = (patient: any) => {
  vitalsPatientId.value = patient.id
  vitalsAppointmentId.value = ''
  referToDoctor.value = false
  vitalsReferToDept.value = ''
  activeTab.value = 'vitals'
}

const switchToVitalsFromQueue = (appt: any) => {
  vitalsPatientId.value = appt.patient_id
  vitalsAppointmentId.value = appt.id
  referToDoctor.value = false
  vitalsReferToDept.value = ''
  activeTab.value = 'vitals'
}

const resetVitalsForm = () => {
  vitalsPatientId.value = ''
  vitalsAppointmentId.value = ''
  vitalsSystolic.value = ''
  vitalsDiastolic.value = ''
  vitalsBloodSugar.value = ''
  vitalsPulse.value = ''
  vitalsTemp.value = ''
  vitalsRespiration.value = ''
  vitalsNotes.value = ''
  referToDoctor.value = false
  vitalsReferToDept.value = ''
}

const handleVitalsSubmit = async () => {
  if (!vitalsPatientId.value) {
    notification.error('Please select a patient')
    return
  }
  vitalsSubmitting.value = true
  try {
    const payload = {
      patient_id: vitalsPatientId.value,
      systolic_bp: Number(vitalsSystolic.value),
      diastolic_bp: Number(vitalsDiastolic.value),
      blood_sugar: Number(vitalsBloodSugar.value),
      pulse_rate: Number(vitalsPulse.value),
      temperature: Number(vitalsTemp.value),
      respiration_rate: Number(vitalsRespiration.value),
      notes: vitalsNotes.value,
      appointment_id: vitalsAppointmentId.value || null,
      refer_to_department_id: referToDoctor.value ? vitalsReferToDept.value : null,
    }
    const res = await api.post('/vitals', payload)
    lastRecordedVitals.value = res.data.data || payload
    recentlyRecordedPatientId.value = vitalsPatientId.value
    setTimeout(() => {
      recentlyRecordedPatientId.value = null
    }, 2500)

    notification.success(res.data.message || 'Vitals recorded successfully')
    resetVitalsForm()
    await loadData()
  } catch (error: any) {
    const msg = error.response?.data?.message || 'Failed to record vitals'
    notification.error(msg)
  } finally {
    vitalsSubmitting.value = false
  }
}

// ─── Checkup Approvals ───────────────────────────────────────────────────────
const approveVitalsCheckup = async (apptId: string) => {
  try {
    await api.put(`/appointments/${apptId}`, { status: 'confirmed' })
    notification.success('Vitals checkup request approved')
    await loadData()
  } catch (error) {
    notification.error('Failed to approve checkup request')
  }
}

const rejectVitalsCheckup = async (apptId: string) => {
  try {
    await api.put(`/appointments/${apptId}`, { status: 'cancelled' })
    notification.success('Vitals checkup request declined')
    await loadData()
  } catch (error) {
    notification.error('Failed to decline checkup request')
  }
}

// ─── Profile Edit ─────────────────────────────────────────────────────────────
const openEditModal = () => {
  editShift.value = nurseProfile.value?.shift || ''
  editIsAvailable.value = nurseProfile.value?.is_available ?? true
  editExperienceYears.value = nurseProfile.value?.experience_years ?? ''
  showEditModal.value = true
}

const handleProfileUpdate = async () => {
  editSubmitting.value = true
  try {
    const payload = {
      shift: editShift.value,
      is_available: editIsAvailable.value,
      experience_years: Number(editExperienceYears.value),
    }
    const res = await api.put('/nurses/me', payload)
    nurseProfile.value = res.data.data || { ...nurseProfile.value, ...payload }
    if (stats.value[3]) {
      stats.value[3].value = editShift.value
        ? editShift.value.charAt(0).toUpperCase() + editShift.value.slice(1)
        : '—'
    }
    notification.success('Profile updated successfully')
    showEditModal.value = false
  } catch (error: any) {
    const msg = error.response?.data?.message || 'Failed to update profile'
    notification.error(msg)
  } finally {
    editSubmitting.value = false
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const getPatientName = (id: string) => {
  return patients.value.find((p) => p.id === id)?.full_name || 'Unknown Patient'
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

onMounted(loadData)
</script>

<template>
  <PortalBase role="nurse" title="Nurse Dashboard" :stats="stats">
    <template #main>
      <!-- Tab Bar -->
      <div
        class="flex items-center p-1.5 bg-gray-100 dark:bg-slate-800/50 rounded-2xl w-fit mb-8 border border-gray-200/50 dark:border-slate-700/50 flex-wrap gap-1"
      >
        <button
          @click="activeTab = 'queue'"
          :class="`px-5 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'queue'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Vitals Queue
          <span
            v-if="awaitingVitalsQueue.length"
            class="ml-1.5 text-[10px] bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400 px-1.5 py-0.5 rounded-full"
            >{{ awaitingVitalsQueue.length }}</span
          >
        </button>
        <button
          @click="activeTab = 'patients'"
          :class="`px-5 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'patients'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Patients
          <span
            v-if="patients.length"
            class="ml-1.5 text-[10px] bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 px-1.5 py-0.5 rounded-full"
            >{{ patients.length }}</span
          >
        </button>
        <button
          @click="activeTab = 'vitals'"
          :class="`px-5 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'vitals'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Record Vitals
        </button>
        <button
          @click="activeTab = 'profile'"
          :class="`px-5 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'profile'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          My Profile
        </button>
      </div>

      <!-- Global Loading Skeleton -->
      <div v-if="isLoading" class="space-y-10">
        <!-- Queue skeleton -->
        <div class="space-y-6">
          <div class="skeleton h-5 w-48 rounded-xl"></div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="i in 4"
              :key="i"
              class="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-gray-100 dark:border-slate-800"
            >
              <div class="flex items-center justify-between mb-4">
                <div class="skeleton h-5 w-28 rounded-full"></div>
                <div class="skeleton h-4 w-20"></div>
              </div>
              <div class="skeleton h-5 w-3/4 mb-2"></div>
              <div class="skeleton h-3 w-1/2 mb-6"></div>
              <div class="skeleton h-10 w-full rounded-xl"></div>
            </div>
          </div>
        </div>
        <!-- Requests skeleton -->
        <div class="space-y-4">
          <div class="skeleton h-5 w-40 rounded-xl"></div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="i in 2"
              :key="i"
              class="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-gray-100 dark:border-slate-800"
            >
              <div class="skeleton h-4 w-24 mb-3 rounded-full"></div>
              <div class="skeleton h-5 w-3/4 mb-2"></div>
              <div class="skeleton h-3 w-1/2 mb-6"></div>
              <div class="grid grid-cols-2 gap-3">
                <div class="skeleton h-10 rounded-xl"></div>
                <div class="skeleton h-10 rounded-xl"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── TAB 0: Vitals Queue & Requests ────────────────────────────── -->
      <div v-else-if="activeTab === 'queue'" class="space-y-10">
        <!-- Part A: Vitals Queue -->
        <div class="space-y-6">
          <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-amber-500 rounded-full"></span>
            Vitals Observation Queue
          </h3>

          <div
            v-if="awaitingVitalsQueue.length === 0"
            class="flex flex-col items-center justify-center py-12 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border border-gray-100 dark:border-slate-800"
          >
            <p class="text-gray-400 dark:text-slate-500 text-sm font-medium">
              No patients are currently in the queue awaiting vitals checks.
            </p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="appt in awaitingVitalsQueue"
              :key="appt.id"
              :class="`card-animate bg-white dark:bg-slate-900 p-6 rounded-3xl border shadow-premium flex flex-col justify-between ${
                recentlyRecordedPatientId === appt.patient_id
                  ? 'success-pulse border-emerald-400 dark:border-emerald-600'
                  : 'border-gray-100 dark:border-slate-800'
              }`"
            >
              <div>
                <div class="flex items-center justify-between mb-4">
                  <span
                    :class="`px-3 py-1 text-[10px] font-black uppercase tracking-widest rounded-full ${
                      appt.appointment_type === 'vitals_check'
                        ? 'bg-teal-50 text-teal-700 dark:bg-teal-950/40 dark:text-teal-400'
                        : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400'
                    }`"
                  >
                    {{
                      appt.appointment_type === 'vitals_check'
                        ? 'Vitals Screening'
                        : 'Physician Consultation'
                    }}
                  </span>
                  <span class="text-xs text-gray-400 dark:text-slate-500 font-bold">
                    {{ formatDate(appt.appointment_date) }}
                  </span>
                </div>
                <h4 class="text-lg font-black text-gray-900 dark:text-white">
                  {{ appt.patient_name || getPatientName(appt.patient_id) }}
                </h4>
                <p class="text-xs text-gray-500 dark:text-slate-400 mt-2 font-medium">
                  <strong>Clinician:</strong> {{ appt.doctor_name || 'Vitals Check Only' }}
                </p>
                <p class="text-xs text-gray-400 dark:text-slate-500 mt-1 italic">
                  "{{ appt.reason }}"
                </p>
              </div>

              <button
                @click="switchToVitalsFromQueue(appt)"
                class="w-full py-3 bg-amber-500 hover:bg-amber-600 text-white text-xs font-black uppercase tracking-widest rounded-xl shadow-lg shadow-amber-500/10 transition-all flex items-center justify-center gap-2 mt-6"
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
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Check Vitals Now
              </button>
            </div>
          </div>
        </div>

        <!-- Part B: Vitals Requests -->
        <div class="space-y-6">
          <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-teal-600 rounded-full"></span>
            Checkup Requests
          </h3>

          <div
            v-if="pendingCheckupRequests.length === 0"
            class="flex flex-col items-center justify-center py-12 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border border-gray-100 dark:border-slate-800"
          >
            <p class="text-gray-400 dark:text-slate-500 text-sm font-medium">
              No pending standalone vitals checkup requests found.
            </p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="req in pendingCheckupRequests"
              :key="req.id"
              class="card-animate bg-white dark:bg-slate-900 p-6 rounded-3xl border border-gray-100 dark:border-slate-800 shadow-premium flex flex-col justify-between"
            >
              <div>
                <div class="flex items-center justify-between mb-4">
                  <span
                    class="px-3 py-1 bg-teal-50 text-teal-700 dark:bg-teal-950/40 dark:text-teal-400 text-[10px] font-black uppercase tracking-widest rounded-full"
                  >
                    Pending Approval
                  </span>
                  <span class="text-xs text-gray-400 dark:text-slate-500 font-bold">
                    {{ formatDate(req.appointment_date) }}
                  </span>
                </div>
                <h4 class="text-lg font-black text-gray-900 dark:text-white">
                  {{ req.patient_name || getPatientName(req.patient_id) }}
                </h4>
                <p class="text-xs text-gray-400 dark:text-slate-500 mt-2 italic">
                  "{{ req.reason }}"
                </p>
              </div>

              <div class="grid grid-cols-2 gap-3 mt-6">
                <button
                  @click="rejectVitalsCheckup(req.id)"
                  class="py-3 bg-red-50 hover:bg-red-100 dark:bg-red-950/30 dark:hover:bg-red-950/50 text-red-600 dark:text-red-400 text-xs font-black uppercase tracking-widest rounded-xl transition-all"
                >
                  Decline
                </button>
                <button
                  @click="approveVitalsCheckup(req.id)"
                  class="py-3 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-black uppercase tracking-widest rounded-xl shadow-lg shadow-emerald-500/10 transition-all"
                >
                  Approve Checkup
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── TAB 1: Patients ──────────────────────────────────────────── -->
      <div v-else-if="activeTab === 'patients'" class="space-y-6">
        <div class="flex items-center justify-between flex-wrap gap-4 mb-2">
          <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
            All Patients
          </h3>
          <!-- Search -->
          <div class="relative">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-slate-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              v-model="patientSearch"
              type="text"
              placeholder="Search patients..."
              class="appearance-none pl-10 pr-4 py-2.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 w-64"
            />
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="filteredPatients.length === 0"
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
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
          <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
            {{ patientSearch ? 'No patients match your search' : 'No patients found' }}
          </h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium">
            Patient records will appear here once registered in the system.
          </p>
        </div>

        <!-- Patient Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="patient in filteredPatients"
            :key="patient.id"
            :class="`card-animate bg-white dark:bg-slate-900 p-6 rounded-3xl border shadow-premium group flex flex-col justify-between hover:-translate-y-1 transition-all duration-300 ${
              recentlyRecordedPatientId === patient.id
                ? 'success-pulse border-emerald-400 dark:border-emerald-600'
                : 'border-gray-100 dark:border-slate-800'
            }`"
          >
            <div>
              <div class="flex items-start justify-between mb-4">
                <div
                  class="w-12 h-12 bg-emerald-50 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center text-emerald-600 font-bold text-lg"
                >
                  {{ patient.full_name?.charAt(0) || 'P' }}
                </div>
                <span
                  class="px-3 py-1 bg-teal-100 dark:bg-teal-900/40 text-teal-700 dark:text-teal-400 text-[10px] font-black uppercase tracking-widest rounded-full"
                >
                  {{ patient.blood_group || 'N/A' }}
                </span>
              </div>
              <h4 class="text-lg font-black text-gray-900 dark:text-white">
                {{ patient.full_name }}
              </h4>
              <p class="text-[10px] text-gray-400 uppercase tracking-widest mb-2">
                {{ patient.gender }} • DOB: {{ patient.date_of_birth }}
              </p>
              <p
                v-if="patient.doctor_name"
                class="text-xs text-gray-500 dark:text-slate-400 font-medium mb-4 flex items-center gap-1.5"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-3.5 w-3.5 text-emerald-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
                Dr. {{ patient.doctor_name }}
              </p>
            </div>

            <button
              @click="switchToVitals(patient)"
              class="w-full py-3 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/10 transition-all flex items-center justify-center gap-2 mt-4"
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
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
              Record Vitals
            </button>
          </div>
        </div>
      </div>

      <!-- ── TAB 2: Record Vitals ────────────────────────────────────────── -->
      <div v-else-if="activeTab === 'vitals'" class="space-y-8">
        <div class="flex items-center gap-3 mb-2">
          <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-teal-600 rounded-full"></span>
            Record Patient Vitals
          </h3>
        </div>

        <!-- Success Summary after submit -->
        <Transition name="fade">
          <div
            v-if="lastRecordedVitals"
            class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-500/30 rounded-3xl p-6"
          >
            <div class="flex items-center gap-3 mb-4">
              <div
                class="w-9 h-9 bg-emerald-600 rounded-xl flex items-center justify-center shrink-0"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p
                  class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest"
                >
                  Last Recorded
                </p>
                <p class="text-sm font-black text-gray-900 dark:text-white">
                  {{ getPatientName(lastRecordedVitals.patient_id) }}
                </p>
              </div>
              <button
                @click="lastRecordedVitals = null"
                class="ml-auto text-gray-400 hover:text-gray-600 dark:hover:text-slate-300 transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div
                v-for="(item, idx) in [
                  { label: 'Systolic BP', value: lastRecordedVitals.systolic_bp, unit: 'mmHg' },
                  { label: 'Diastolic BP', value: lastRecordedVitals.diastolic_bp, unit: 'mmHg' },
                  { label: 'Blood Sugar', value: lastRecordedVitals.blood_sugar, unit: 'mg/dL' },
                  { label: 'Pulse Rate', value: lastRecordedVitals.pulse_rate, unit: 'bpm' },
                  { label: 'Temperature', value: lastRecordedVitals.temperature, unit: '°F' },
                  {
                    label: 'Respiration',
                    value: lastRecordedVitals.respiration_rate,
                    unit: '/min',
                  },
                ]"
                :key="idx"
                class="bg-white dark:bg-slate-900 rounded-2xl p-3 border border-emerald-100 dark:border-emerald-500/20"
              >
                <p
                  class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
                >
                  {{ item.label }}
                </p>
                <p class="text-lg font-black text-emerald-600 dark:text-emerald-400">
                  {{ item.value
                  }}<span class="text-xs font-bold text-gray-400 ml-1">{{ item.unit }}</span>
                </p>
              </div>
            </div>
          </div>
        </Transition>

        <!-- Vitals Form -->
        <form @submit.prevent="handleVitalsSubmit" class="space-y-6">
          <!-- Patient Selector -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
              Patient <span class="text-red-500 ml-0.5">*</span>
            </label>
            <select
              v-model="vitalsPatientId"
              required
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
            >
              <option value="" disabled>Select a patient…</option>
              <option v-for="p in patients" :key="p.id" :value="p.id">
                {{ p.full_name }}
              </option>
            </select>
          </div>

          <!-- BP Row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <FormField
              id="systolic"
              label="Systolic BP (mmHg)"
              type="number"
              placeholder="e.g. 120"
              v-model="vitalsSystolic"
              required
            />
            <FormField
              id="diastolic"
              label="Diastolic BP (mmHg)"
              type="number"
              placeholder="e.g. 80"
              v-model="vitalsDiastolic"
              required
            />
          </div>

          <!-- Sugar + Pulse Row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <FormField
              id="bloodSugar"
              label="Blood Sugar (mg/dL)"
              type="number"
              placeholder="e.g. 95"
              v-model="vitalsBloodSugar"
              required
            />
            <FormField
              id="pulse"
              label="Pulse Rate (bpm)"
              type="number"
              placeholder="e.g. 72"
              v-model="vitalsPulse"
              required
            />
          </div>

          <!-- Temp + Respiration Row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <FormField
              id="temperature"
              label="Temperature (°F)"
              type="number"
              placeholder="e.g. 98.6"
              v-model="vitalsTemp"
              required
            />
            <FormField
              id="respiration"
              label="Respiration Rate (breaths/min)"
              type="number"
              placeholder="e.g. 16"
              v-model="vitalsRespiration"
              required
            />
          </div>

          <!-- Notes -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
              Clinical Notes
            </label>
            <textarea
              v-model="vitalsNotes"
              rows="3"
              placeholder="Additional observations or notes…"
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-500/10 dark:focus:ring-emerald-400/10 resize-none"
            ></textarea>
          </div>

          <!-- Doctor Referral Section (Verbal escalation logic) -->
          <div
            v-if="isCurrentAppointmentVitalsCheck"
            class="p-6 bg-slate-50 dark:bg-slate-800/40 rounded-3xl border border-gray-200/50 dark:border-slate-700/40 space-y-4"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-black text-gray-900 dark:text-white">Refer to Doctor?</p>
                <p class="text-xs text-gray-400 dark:text-slate-500 mt-0.5">
                  Does the patient verbally agree to be referred to a department physician?
                </p>
              </div>
              <button
                type="button"
                @click="referToDoctor = !referToDoctor"
                :class="`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  referToDoctor ? 'bg-amber-500' : 'bg-gray-300 dark:bg-slate-700'
                }`"
              >
                <span
                  :class="`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    referToDoctor ? 'translate-x-5' : 'translate-x-0'
                  }`"
                ></span>
              </button>
            </div>

            <!-- Department dropdown list -->
            <Transition name="fade">
              <div
                v-if="referToDoctor"
                class="w-full space-y-1.5 pt-2 border-t border-gray-200/30 dark:border-slate-700/30"
              >
                <label class="block text-xs font-black uppercase text-gray-400 dark:text-slate-500">
                  Select Clinical Department
                </label>
                <select
                  v-model="vitalsReferToDept"
                  required
                  class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 text-sm"
                >
                  <option value="" disabled>Choose a department to route to…</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                    {{ dept.name }}
                  </option>
                </select>
              </div>
            </Transition>
          </div>

          <div class="flex gap-4 pt-2">
            <button
              type="button"
              @click="resetVitalsForm"
              class="flex-1 py-4 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
            >
              Reset Form
            </button>
            <button
              type="submit"
              :disabled="vitalsSubmitting"
              class="flex-1 py-4 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <div
                v-if="vitalsSubmitting"
                class="animate-spin rounded-full h-4 w-4 border-[2px] border-white border-t-transparent"
              ></div>
              <span>{{ vitalsSubmitting ? 'Recording…' : 'Record Vitals' }}</span>
            </button>
          </div>
        </form>
      </div>

      <!-- ── TAB 3: My Profile ───────────────────────────────────────────── -->
      <div v-else-if="activeTab === 'profile'" class="space-y-6">
        <div class="flex items-center justify-between flex-wrap gap-4 mb-2">
          <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-teal-600 rounded-full"></span>
            My Profile
          </h3>
          <button
            @click="openEditModal"
            class="px-5 py-2.5 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/10 transition-all flex items-center gap-2"
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
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            Edit Profile
          </button>
        </div>

        <div
          v-if="!nurseProfile"
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
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
          <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
            Profile not available
          </h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium">
            Could not load nurse profile. Please try again later.
          </p>
        </div>

        <div v-else>
          <!-- Profile header card -->
          <div
            class="bg-gradient-to-br from-emerald-600 to-teal-700 rounded-3xl p-8 text-white shadow-xl shadow-emerald-500/25 mb-6"
          >
            <div class="flex items-center gap-6">
              <div
                class="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center text-white font-black text-3xl border border-white/30"
              >
                {{ nurseProfile.full_name?.charAt(0) || 'N' }}
              </div>
              <div>
                <h4 class="text-2xl font-black tracking-tight">{{ nurseProfile.full_name }}</h4>
                <p class="text-emerald-100 text-sm font-bold mt-1 uppercase tracking-widest">
                  {{ nurseProfile.nurse_code || '—' }}
                </p>
                <span
                  :class="`mt-2 inline-block px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                    nurseProfile.is_available
                      ? 'bg-white/20 text-white border border-white/30'
                      : 'bg-black/20 text-white/70 border border-white/10'
                  }`"
                >
                  {{ nurseProfile.is_available ? '● Available' : '○ Unavailable' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Detail Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="(item, idx) in [
                {
                  label: 'Department',
                  value: nurseProfile.department_name || nurseProfile.department || '—',
                  icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
                },
                {
                  label: 'Shift',
                  value: nurseProfile.shift
                    ? nurseProfile.shift.charAt(0).toUpperCase() + nurseProfile.shift.slice(1)
                    : '—',
                  icon: 'M12 8v4l3 3m6-3a9 9 0 11-12 0 9 9 0 0112 0z',
                },
                {
                  label: 'Experience',
                  value:
                    nurseProfile.experience_years != null
                      ? `${nurseProfile.experience_years} yrs`
                      : '—',
                  icon: 'M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z',
                },
                {
                  label: 'License Number',
                  value: nurseProfile.license_number || '—',
                  icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
                },
                {
                  label: 'Blood Group',
                  value: nurseProfile.blood_group || '—',
                  icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
                },
                {
                  label: 'Nurse Code',
                  value: nurseProfile.nurse_code || '—',
                  icon: 'M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2',
                },
              ]"
              :key="idx"
              class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-gray-100 dark:border-slate-800 shadow-sm group hover:-translate-y-0.5 transition-all duration-200"
            >
              <div class="flex items-center gap-3 mb-3">
                <div
                  class="w-9 h-9 bg-emerald-50 dark:bg-emerald-900/30 rounded-xl flex items-center justify-center text-emerald-600 dark:text-emerald-400 shrink-0"
                >
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      :d="item.icon"
                    />
                  </svg>
                </div>
                <p
                  class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
                >
                  {{ item.label }}
                </p>
              </div>
              <p class="text-base font-black text-gray-900 dark:text-white pl-12">
                {{ item.value }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </PortalBase>

  <!-- ── Edit Profile Modal ──────────────────────────────────────────────── -->
  <Transition name="fade">
    <div
      v-if="showEditModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-10 shadow-premium-xl animate-scale-up"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-8">
          <div>
            <span
              class="text-[10px] font-black text-emerald-600 bg-emerald-50 dark:bg-emerald-950 dark:text-emerald-400 px-3 py-1 rounded-full uppercase tracking-widest"
            >
              Edit Profile
            </span>
            <h3 class="text-2xl font-black text-gray-900 dark:text-white mt-3 tracking-tight">
              Update My Details
            </h3>
          </div>
          <button
            @click="showEditModal = false"
            class="w-10 h-10 rounded-full bg-gray-50 dark:bg-slate-800 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-slate-200 transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="handleProfileUpdate" class="space-y-6">
          <!-- Shift Selector -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
              Shift <span class="text-red-500 ml-0.5">*</span>
            </label>
            <select
              v-model="editShift"
              required
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
            >
              <option value="" disabled>Select shift…</option>
              <option value="morning">Morning</option>
              <option value="afternoon">Afternoon</option>
              <option value="night">Night</option>
              <option value="rotating">Rotating</option>
            </select>
          </div>

          <FormField
            id="editExpYears"
            label="Experience Years"
            type="number"
            placeholder="e.g. 5"
            v-model="editExperienceYears"
            required
          />

          <!-- Availability Toggle -->
          <div
            class="flex items-center justify-between px-4 py-3.5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-200 dark:border-slate-700/50"
          >
            <div>
              <p class="text-sm font-bold text-gray-700 dark:text-slate-300">Available for Duty</p>
              <p class="text-xs text-gray-400 dark:text-slate-500 mt-0.5">
                Toggle your on-duty availability status
              </p>
            </div>
            <button
              type="button"
              @click="editIsAvailable = !editIsAvailable"
              :class="`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                editIsAvailable ? 'bg-emerald-600' : 'bg-gray-300 dark:bg-slate-700'
              }`"
            >
              <span
                :class="`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  editIsAvailable ? 'translate-x-5' : 'translate-x-0'
                }`"
              ></span>
            </button>
          </div>

          <div class="flex gap-4 pt-4">
            <button
              type="button"
              @click="showEditModal = false"
              class="flex-1 py-4 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="editSubmitting"
              class="flex-1 py-4 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <div
                v-if="editSubmitting"
                class="animate-spin rounded-full h-4 w-4 border-[2px] border-white border-t-transparent"
              ></div>
              <span>{{ editSubmitting ? 'Saving…' : 'Save Changes' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
@keyframes scaleUp {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
.animate-scale-up {
  animation: scaleUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
</style>
