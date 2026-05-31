<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'
import FormField from '../../components/FormField.vue'

const notification = useNotificationStore()
const route = useRoute()
const appointments = ref<any[]>([])
const assignedPatients = ref<any[]>([])
const isLoading = ref(true)
const activeTab = ref('consultations') // 'consultations' | 'patients' | 'records'

// Sync activeTab with route path
const syncTabWithRoute = () => {
  if (route.path === '/doctor/records') {
    activeTab.value = 'records'
  } else if (route.path === '/doctor/patients') {
    activeTab.value = 'patients'
  } else {
    activeTab.value = 'consultations'
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

// ───────── Schedule Modal ─────────
const showScheduleModal = ref(false)
const selectedPatient = ref<any>(null)
const meetDate = ref('')
const meetReason = ref('')

// ───────── Medical Records Tab ─────────
const recordsSelectedPatientId = ref('')
const patientRecords = ref<any[]>([])
const isLoadingRecords = ref(false)

const recordsSelectedPatient = computed(
  () =>
    assignedPatients.value.find(
      (p) => p.id?.toLowerCase() === recordsSelectedPatientId.value?.toLowerCase(),
    ) || null,
)

const loadPatientRecords = async (patientId: string) => {
  if (!patientId) return
  isLoadingRecords.value = true
  try {
    const res = await api.get(`/medical-records/patient/${patientId}`)
    patientRecords.value = res.data.data || res.data || []
  } catch {
    notification.error('Failed to load medical records')
    patientRecords.value = []
  } finally {
    isLoadingRecords.value = false
  }
}

const onRecordsPatientChange = (e: Event) => {
  const id = (e.target as HTMLSelectElement).value
  recordsSelectedPatientId.value = id
  patientRecords.value = []
  if (id) loadPatientRecords(id)
}

// ───────── Write Record Modal ─────────
const showWriteRecordModal = ref(false)
const writeRecord = ref({
  patient_id: '',
  appointment_id: '',
  diagnosis: '',
  treatment: '',
  prescription: '',
  notes: '',
})
const isSubmittingRecord = ref(false)
const recentlyWrittenPatientId = ref<string | null>(null)

// ───────── Patient Vitals Integration ─────────
const selectedPatientVitals = ref<any>(null)
const isLoadingVitals = ref(false)

const loadPatientVitals = async (patientId: string) => {
  if (!patientId) return
  isLoadingVitals.value = true
  try {
    const res = await api.get(`/vitals/${patientId}`)
    selectedPatientVitals.value = res.data.data || res.data || null
  } catch {
    selectedPatientVitals.value = null
  } finally {
    isLoadingVitals.value = false
  }
}

const onModalPatientChange = async () => {
  selectedPatientVitals.value = null
  if (writeRecord.value.patient_id) {
    await loadPatientVitals(writeRecord.value.patient_id)
  }
}

const writeRecordPatientAppointments = computed(() => {
  if (!writeRecord.value.patient_id) return []
  return appointments.value.filter(
    (a) =>
      a.patient_id?.toLowerCase() === writeRecord.value.patient_id?.toLowerCase() &&
      (a.status === 'confirmed' || a.status === 'completed'),
  )
})

const openWriteRecordModal = async () => {
  writeRecord.value = {
    patient_id: recordsSelectedPatientId.value,
    appointment_id: '',
    diagnosis: '',
    treatment: '',
    prescription: '',
    notes: '',
  }
  selectedPatientVitals.value = null
  showWriteRecordModal.value = true
  if (writeRecord.value.patient_id) {
    await loadPatientVitals(writeRecord.value.patient_id)
  }
}

const handleWriteRecordSubmit = async () => {
  if (!writeRecord.value.patient_id) {
    notification.error('Please select a patient')
    return
  }
  if (!writeRecord.value.diagnosis.trim()) {
    notification.error('Diagnosis is required')
    return
  }
  if (writeRecord.value.appointment_id) {
    const apt = appointments.value.find((a) => a.id === writeRecord.value.appointment_id)
    if (apt && !apt.vitals_checked) {
      notification.error(
        'Cannot submit record: Patient vitals have not been captured by a nurse for this appointment.',
      )
      return
    }
  }
  isSubmittingRecord.value = true
  try {
    const payload: any = {
      patient_id: writeRecord.value.patient_id,
      diagnosis: writeRecord.value.diagnosis,
      treatment: writeRecord.value.treatment,
      prescription: writeRecord.value.prescription,
      notes: writeRecord.value.notes,
    }
    if (writeRecord.value.appointment_id) {
      payload.appointment_id = writeRecord.value.appointment_id
    }
    await api.post('/medical-records', payload)
    notification.success('Medical record created successfully')
    showWriteRecordModal.value = false
    // Refresh records if the written record belongs to the currently viewed patient
    if (
      writeRecord.value.patient_id?.toLowerCase() === recordsSelectedPatientId.value?.toLowerCase()
    ) {
      await loadPatientRecords(recordsSelectedPatientId.value)
    }
  } catch (error: any) {
    const message = error.response?.data?.message || 'Failed to create record'
    notification.error(message)
  } finally {
    isSubmittingRecord.value = false
  }
}

// ───────── Patient History Modal ─────────
const showHistoryModal = ref(false)
const historyPatient = ref<any>(null)
const historyRecords = ref<any[]>([])
const isLoadingHistory = ref(false)

const openHistoryModal = async (patient: any) => {
  historyPatient.value = patient
  historyRecords.value = []
  showHistoryModal.value = true
  isLoadingHistory.value = true
  try {
    const res = await api.get(`/medical-records/patient/${patient.id}`)
    historyRecords.value = res.data.data || res.data || []
  } catch {
    notification.error('Failed to load patient history')
  } finally {
    isLoadingHistory.value = false
  }
}

// ───────── Stats ─────────
const stats = ref([
  {
    name: "Today's Appointments",
    value: '0',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    color: 'bg-emerald-600',
  },
  {
    name: 'Assigned Patients',
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

// ───────── Load Data ─────────
const loadData = async () => {
  isLoading.value = true
  try {
    const [appRes, appointRes, patientsRes] = await Promise.all([
      api.get('/applications'),
      api.get('/appointments'),
      api.get('/patients/assigned'),
    ])

    const pendingApps = (appRes.data.data || []).filter((a: any) => a.status === 'pending').length
    if (stats.value[2]) stats.value[2].value = pendingApps.toString()

    appointments.value = appointRes.data.data || []
    console.log('Loaded appointments:', appointments.value)
    assignedPatients.value = patientsRes.data.data || []
    if (stats.value[1]) stats.value[1].value = assignedPatients.value.length.toString()

    const today = new Date().toDateString()
    const todayAppointments = appointments.value.filter(
      (a) => new Date(a.appointment_date).toDateString() === today,
    )
    if (stats.value[0]) stats.value[0].value = todayAppointments.length.toString()
    const completedToday = todayAppointments.filter((a) => a.status === 'completed').length
    if (stats.value[3]) stats.value[3].value = completedToday.toString()
  } catch {
    notification.error('Failed to load dashboard data')
  } finally {
    isLoading.value = false
  }
}

const minDateTime = computed(() => {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  const localNow = new Date(now.getTime() - offset * 60 * 1000)
  return localNow.toISOString().slice(0, 16)
})

const getPatientActiveAppointment = (patientId: string) => {
  return appointments.value.find(
    (a) =>
      a.patient_id?.toLowerCase() === patientId?.toLowerCase() &&
      (a.status === 'pending' || a.status === 'confirmed'),
  )
}

// ───────── Schedule Modal ─────────
const openScheduleModal = (patient: any) => {
  selectedPatient.value = patient
  meetDate.value = ''
  meetReason.value = 'Routine checkup and clinical review'
  showScheduleModal.value = true
}

const handleScheduleSubmit = async () => {
  if (!meetDate.value) {
    notification.error('Please specify a date and time')
    return
  }
  try {
    const payload = {
      patient_id: selectedPatient.value.id,
      doctor_id: '',
      appointment_date: new Date(meetDate.value).toISOString(),
      reason: meetReason.value,
    }
    await api.post('/appointments', payload)
    notification.success('Consultation scheduled successfully')
    showScheduleModal.value = false
    await loadData()
  } catch (error: any) {
    const message = error.response?.data?.message || 'Failed to schedule consultation'
    notification.error(message)
  }
}

// ───────── Helpers ─────────
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

const formatDateShort = (dateString: string) => {
  if (!dateString) return '—'
  const date = new Date(normalizeDate(dateString))
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
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
      <!-- Navigation Tab Bar -->
      <div
        class="flex items-center p-1.5 bg-gray-100 dark:bg-slate-800/50 rounded-2xl w-fit mb-8 border border-gray-200/50 dark:border-slate-700/50 flex-wrap gap-1"
      >
        <button
          @click="activeTab = 'consultations'"
          :class="`px-6 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'consultations'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Consultations
        </button>
        <button
          @click="activeTab = 'patients'"
          :class="`px-6 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'patients'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Patients ({{ assignedPatients.length }})
        </button>
        <button
          @click="activeTab = 'records'"
          :class="`px-6 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'records'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Medical Records
        </button>
      </div>

      <!-- Global Loading Skeleton -->
      <div v-if="isLoading" class="space-y-4">
        <div class="flex items-center justify-between mb-2">
          <div class="skeleton h-5 w-40 rounded-xl"></div>
          <div class="skeleton h-4 w-28 rounded"></div>
        </div>
        <div
          v-for="i in 4"
          :key="i"
          class="bg-gray-50 dark:bg-slate-800/40 p-6 rounded-3xl border border-gray-100 dark:border-slate-800"
        >
          <div class="flex items-center justify-between flex-wrap gap-4">
            <div class="flex items-center gap-4">
              <div class="skeleton w-12 h-12 rounded-2xl"></div>
              <div class="space-y-2">
                <div class="skeleton h-4 w-32"></div>
                <div class="skeleton h-3 w-24"></div>
              </div>
            </div>
            <div class="flex gap-2">
              <div class="skeleton h-6 w-20 rounded-full"></div>
              <div class="skeleton h-6 w-24 rounded-full"></div>
            </div>
          </div>
          <div class="skeleton h-3 w-2/3 mt-4 ml-16"></div>
        </div>
      </div>

      <!-- ─────────────────────────────────────────────────── -->
      <!-- Tab 1: Consultations -->
      <!-- ─────────────────────────────────────────────────── -->
      <div v-else-if="activeTab === 'consultations'" class="space-y-6">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
            Quick Overview
          </h3>
          <RouterLink
            to="/doctor/appointments"
            class="text-xs font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest hover:underline"
          >
            View Full Schedule
          </RouterLink>
        </div>

        <div
          v-if="appointments.length === 0"
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
            When patients book consultations or you schedule meeting times, they will list here.
          </p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="apt in appointments.slice(0, 8)"
            :key="apt.id"
            class="card-animate group bg-gray-50 dark:bg-slate-800/40 p-6 rounded-3xl border border-gray-100 dark:border-slate-800 hover:border-emerald-500/30 transition-all duration-300"
          >
            <div class="flex items-center justify-between flex-wrap gap-4">
              <div class="flex items-center gap-4">
                <div
                  class="w-12 h-12 rounded-2xl bg-white dark:bg-slate-900 flex items-center justify-center shadow-sm text-emerald-600 font-bold border border-gray-100 dark:border-slate-800"
                >
                  {{ apt.patient_name?.charAt(0) || 'P' }}
                </div>
                <div>
                  <h4 class="font-black text-gray-900 dark:text-white">{{ apt.patient_name }}</h4>
                  <p
                    class="text-[10px] text-gray-400 dark:text-slate-500 font-black uppercase tracking-widest mt-0.5"
                  >
                    {{ formatDate(apt.appointment_date) }}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-3 flex-wrap">
                <span
                  v-if="!apt.vitals_checked && apt.appointment_type !== 'vitals_check'"
                  class="px-3 py-1 bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 rounded-full text-[10px] font-black uppercase tracking-widest border border-amber-200/50 dark:border-amber-500/10 flex items-center gap-1.5"
                >
                  <span class="h-1.5 w-1.5 bg-amber-500 rounded-full animate-pulse"></span>
                  Awaiting Vitals
                </span>
                <span
                  v-else-if="apt.vitals_checked"
                  class="px-3 py-1 bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 rounded-full text-[10px] font-black uppercase tracking-widest border border-emerald-200/50 dark:border-emerald-500/10 flex items-center gap-1.5"
                >
                  <span class="h-1.5 w-1.5 bg-emerald-500 rounded-full"></span>
                  Vitals Checked
                </span>
                <span
                  :class="`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${getStatusColor(apt.status)}`"
                >
                  {{ apt.status }}
                </span>
              </div>
            </div>
            <p
              v-if="apt.reason"
              class="text-xs text-gray-500 dark:text-slate-400 mt-4 pl-16 border-l-2 border-emerald-500/20 italic"
            >
              "{{ apt.reason }}"
            </p>
          </div>
        </div>
      </div>

      <!-- ─────────────────────────────────────────────────── -->
      <!-- Tab 2: Approved Patients -->
      <!-- ─────────────────────────────────────────────────── -->
      <div v-else-if="activeTab === 'patients'" class="space-y-6">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-teal-600 rounded-full"></span>
            My Assigned Patients
          </h3>
        </div>

        <div
          v-if="assignedPatients.length === 0"
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
          <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">No assigned patients</h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium">
            When user registration applications are approved by you, they will appear here.
          </p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="patient in assignedPatients"
            :key="patient.id"
            class="card-animate bg-white dark:bg-slate-900 p-6 rounded-3xl border border-gray-100 dark:border-slate-800 shadow-premium group flex flex-col justify-between hover:-translate-y-1 transition-all duration-300"
          >
            <div>
              <div class="flex items-start justify-between mb-4">
                <div
                  class="w-12 h-12 bg-emerald-50 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center text-emerald-600 font-bold text-lg"
                >
                  {{ patient.full_name?.charAt(0) || 'P' }}
                </div>
                <div class="flex items-center gap-2">
                  <!-- History icon button -->
                  <button
                    @click="openHistoryModal(patient)"
                    title="View medical history"
                    class="w-8 h-8 rounded-xl bg-teal-50 dark:bg-teal-900/30 flex items-center justify-center text-teal-600 dark:text-teal-400 hover:bg-teal-100 dark:hover:bg-teal-900/60 transition-colors"
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
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                  </button>
                  <span
                    class="px-3 py-1 bg-teal-100 dark:bg-teal-900/40 text-teal-700 dark:text-teal-400 text-[10px] font-black uppercase tracking-widest rounded-full"
                  >
                    Blood: {{ patient.blood_group || 'N/A' }}
                  </span>
                </div>
              </div>
              <h4 class="text-lg font-black text-gray-900 dark:text-white">
                {{ patient.full_name }}
              </h4>
              <p class="text-[10px] text-gray-400 uppercase tracking-widest mb-4">
                {{ patient.gender }} • DOB: {{ patient.date_of_birth }}
              </p>

              <div
                v-if="patient.medical_history"
                class="text-xs text-gray-500 dark:text-slate-400 mb-6 bg-gray-50/50 dark:bg-slate-800/30 p-3 rounded-xl border border-gray-100 dark:border-slate-800"
              >
                <span
                  class="font-black block uppercase text-[8px] text-gray-400 tracking-wider mb-1"
                  >Clinical History</span
                >
                "{{ patient.medical_history }}"
              </div>
            </div>

            <div v-if="getPatientActiveAppointment(patient.id)" class="w-full">
              <div
                class="p-4 bg-teal-50/50 dark:bg-teal-900/10 border border-teal-100/50 dark:border-teal-500/10 rounded-2xl flex items-center justify-between"
              >
                <div>
                  <p
                    class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
                  >
                    Scheduled Meet
                  </p>
                  <p class="text-xs font-bold text-teal-700 dark:text-teal-400">
                    {{ formatDate(getPatientActiveAppointment(patient.id).appointment_date) }}
                  </p>
                </div>
                <span
                  class="px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-widest bg-teal-100 dark:bg-teal-900/60 text-teal-700 dark:text-teal-400 border border-teal-200 dark:border-teal-500/20"
                >
                  {{ getPatientActiveAppointment(patient.id).status }}
                </span>
              </div>
            </div>
            <button
              v-else
              @click="openScheduleModal(patient)"
              class="w-full py-3 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/10 transition-all flex items-center justify-center gap-2"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              Schedule Meet Time
            </button>
          </div>
        </div>
      </div>

      <!-- ─────────────────────────────────────────────────── -->
      <!-- Tab 3: Medical Records -->
      <!-- ─────────────────────────────────────────────────── -->
      <div v-else-if="activeTab === 'records'" class="space-y-6">
        <!-- Header row -->
        <div class="flex items-center justify-between flex-wrap gap-4">
          <h3 class="text-lg font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
            Medical Records
          </h3>
          <button
            @click="openWriteRecordModal"
            class="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 transition-all"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Write New Record
          </button>
        </div>

        <!-- Patient Selector -->
        <div
          class="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-gray-100 dark:border-slate-800 shadow-premium"
        >
          <label
            class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-3"
          >
            Select Patient to View Records
          </label>
          <div class="flex flex-wrap gap-3 mb-4">
            <button
              v-for="p in assignedPatients"
              :key="p.id"
              @click="
                recordsSelectedPatientId = p.id
                loadPatientRecords(p.id)
              "
              :class="`px-4 py-2 rounded-full text-xs font-black uppercase tracking-widest transition-all border ${
                recordsSelectedPatientId === p.id
                  ? 'bg-emerald-600 text-white border-emerald-600 shadow-lg shadow-emerald-500/20'
                  : 'bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 border-gray-200 dark:border-slate-700 hover:border-emerald-500/50'
              }`"
            >
              {{ p.full_name }}
            </button>
          </div>
          <p v-if="assignedPatients.length === 0" class="text-sm text-gray-500 dark:text-slate-400">
            No assigned patients found.
          </p>
        </div>

        <!-- Records List -->
        <div
          v-if="!recordsSelectedPatientId"
          class="flex flex-col items-center justify-center py-16 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border-2 border-dashed border-gray-100 dark:border-slate-800"
        >
          <div
            class="w-16 h-16 bg-white dark:bg-slate-900 rounded-3xl shadow-premium flex items-center justify-center mb-4 text-gray-300 dark:text-slate-700"
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
          <h4 class="text-base font-bold text-gray-900 dark:text-white mb-1">
            Select a patient above
          </h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm font-medium">
            Medical records will appear here
          </p>
        </div>

        <div v-else-if="isLoadingRecords" class="flex items-center justify-center py-16">
          <div
            class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
          ></div>
        </div>

        <div
          v-else-if="patientRecords.length === 0"
          class="flex flex-col items-center justify-center py-16 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border-2 border-dashed border-gray-100 dark:border-slate-800"
        >
          <div
            class="w-16 h-16 bg-white dark:bg-slate-900 rounded-3xl shadow-premium flex items-center justify-center mb-4 text-gray-300 dark:text-slate-700"
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
          <h4 class="text-base font-bold text-gray-900 dark:text-white mb-1">No records found</h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm font-medium">
            No medical records for {{ recordsSelectedPatient?.full_name }} yet.
          </p>
          <button
            @click="openWriteRecordModal"
            class="mt-5 px-5 py-2.5 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 transition-all"
          >
            Write First Record
          </button>
        </div>

        <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            v-for="record in patientRecords"
            :key="record.id"
            class="bg-white dark:bg-slate-900 p-7 rounded-3xl border border-gray-100 dark:border-slate-800 shadow-premium hover:-translate-y-1 transition-all duration-300"
          >
            <!-- Record Date -->
            <div class="flex items-center justify-between mb-5">
              <span
                class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
              >
                {{ formatDateShort(record.created_at || record.date) }}
              </span>
              <span
                v-if="record.appointment_id"
                class="px-2.5 py-1 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-[9px] font-black uppercase tracking-widest rounded-full"
              >
                Linked Appointment
              </span>
            </div>

            <!-- Diagnosis -->
            <div class="mb-4">
              <p
                class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
              >
                Diagnosis
              </p>
              <p class="text-base font-black text-gray-900 dark:text-white leading-snug">
                {{ record.diagnosis }}
              </p>
            </div>

            <!-- Treatment -->
            <div v-if="record.treatment" class="mb-4">
              <p
                class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
              >
                Treatment
              </p>
              <p class="text-sm text-gray-700 dark:text-slate-300 font-medium leading-relaxed">
                {{ record.treatment }}
              </p>
            </div>

            <!-- Prescription pills -->
            <div v-if="record.prescription" class="mb-4">
              <p
                class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-2"
              >
                Prescription
              </p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(med, idx) in record.prescription.split(',')"
                  :key="idx"
                  class="px-3 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-[10px] font-black rounded-full border border-emerald-100 dark:border-emerald-500/20"
                >
                  {{ med.trim() }}
                </span>
              </div>
            </div>

            <!-- Notes -->
            <div
              v-if="record.notes"
              class="mt-4 pt-4 border-t border-gray-100 dark:border-slate-800"
            >
              <p
                class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
              >
                Notes
              </p>
              <p class="text-xs text-gray-500 dark:text-slate-400 italic leading-relaxed">
                {{ record.notes }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </PortalBase>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- Schedule Modal -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <Transition name="fade">
    <div
      v-if="showScheduleModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-10 shadow-premium-xl animate-scale-up"
      >
        <div class="flex items-center justify-between mb-8">
          <div>
            <span
              class="text-[10px] font-black text-emerald-600 bg-emerald-50 dark:bg-emerald-950 dark:text-emerald-400 px-3 py-1 rounded-full uppercase tracking-widest"
            >
              Schedule Consultation
            </span>
            <h3 class="text-2xl font-black text-gray-900 dark:text-white mt-3 tracking-tight">
              Set Meet Time
            </h3>
          </div>
          <button
            @click="showScheduleModal = false"
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

        <form @submit.prevent="handleScheduleSubmit" class="space-y-6">
          <div>
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400 mb-2"
              >Patient Details</label
            >
            <div
              class="px-4 py-3.5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-200 dark:border-slate-700/50 font-bold text-gray-700 dark:text-slate-300 text-sm flex items-center justify-between"
            >
              <span>{{ selectedPatient?.full_name }}</span>
              <span class="text-xs text-gray-500 uppercase tracking-widest">{{
                selectedPatient?.gender
              }}</span>
            </div>
          </div>

          <FormField
            id="meetDate"
            label="Meet Date & Time"
            type="datetime-local"
            v-model="meetDate"
            :min="minDateTime"
            required
          />

          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400"
              >Reason / Clinical Notes <span class="text-red-500 ml-0.5">*</span></label
            >
            <textarea
              v-model="meetReason"
              required
              rows="3"
              placeholder="e.g. Follow-up consultation for health check"
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-500/10 dark:focus:ring-emerald-400/10 resize-none"
            ></textarea>
          </div>

          <div class="flex gap-4 pt-4">
            <button
              type="button"
              @click="showScheduleModal = false"
              class="flex-1 py-4 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="flex-1 py-4 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 transition-all"
            >
              Confirm Schedule
            </button>
          </div>
        </form>
      </div>
    </div>
  </Transition>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- Write Record Modal -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <Transition name="fade">
    <div
      v-if="showWriteRecordModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-2xl w-full p-10 shadow-premium-xl animate-scale-up max-h-[90vh] overflow-y-auto"
      >
        <div class="flex items-center justify-between mb-8">
          <div>
            <span
              class="text-[10px] font-black text-emerald-600 bg-emerald-50 dark:bg-emerald-950 dark:text-emerald-400 px-3 py-1 rounded-full uppercase tracking-widest"
            >
              Clinical Documentation
            </span>
            <h3 class="text-2xl font-black text-gray-900 dark:text-white mt-3 tracking-tight">
              Write Medical Record
            </h3>
          </div>
          <button
            @click="showWriteRecordModal = false"
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

        <form @submit.prevent="handleWriteRecordSubmit" class="space-y-5">
          <!-- Patient selector -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400"
              >Patient <span class="text-red-500 ml-0.5">*</span></label
            >
            <select
              v-model="writeRecord.patient_id"
              required
              @change="onModalPatientChange"
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
            >
              <option value="" disabled>Select a patient...</option>
              <option v-for="p in assignedPatients" :key="p.id" :value="p.id">
                {{ p.full_name }}
              </option>
            </select>
          </div>

          <!-- Clinical Vitals Parameters Grid -->
          <div
            v-if="writeRecord.patient_id"
            class="w-full p-5 bg-gray-50 dark:bg-slate-800/30 rounded-2xl border border-gray-100 dark:border-slate-800/80"
          >
            <h4
              class="text-xs font-black text-gray-900 dark:text-white uppercase tracking-widest mb-3 flex items-center gap-2"
            >
              <span class="h-1.5 w-1.5 bg-emerald-600 rounded-full"></span>
              Patient Vitals
            </h4>
            <div v-if="isLoadingVitals" class="flex justify-center py-4">
              <div
                class="animate-spin rounded-full h-5 w-5 border-2 border-emerald-600 border-t-transparent"
              ></div>
            </div>
            <div
              v-else-if="!selectedPatientVitals"
              class="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-100 dark:border-amber-900/30 text-xs text-amber-700 dark:text-amber-400 font-bold flex items-center gap-2"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              No recorded vitals found for this patient. Please ensure a nurse records their vitals.
            </div>
            <div v-else class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div
                class="bg-white dark:bg-slate-900 p-3 rounded-xl border border-gray-100 dark:border-slate-800"
              >
                <span
                  class="block text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
                  >Blood Pressure</span
                >
                <span class="text-sm font-bold text-gray-800 dark:text-slate-200">
                  {{ selectedPatientVitals.systolic_bp }}/{{ selectedPatientVitals.diastolic_bp }}
                  <span class="text-[10px] text-gray-400">mmHg</span>
                </span>
              </div>
              <div
                class="bg-white dark:bg-slate-900 p-3 rounded-xl border border-gray-100 dark:border-slate-800"
              >
                <span
                  class="block text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
                  >Blood Sugar</span
                >
                <span class="text-sm font-bold text-gray-800 dark:text-slate-200">
                  {{ selectedPatientVitals.blood_sugar }}
                  <span class="text-[10px] text-gray-400">mg/dL</span>
                </span>
              </div>
              <div
                class="bg-white dark:bg-slate-900 p-3 rounded-xl border border-gray-100 dark:border-slate-800"
              >
                <span
                  class="block text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
                  >Pulse Rate</span
                >
                <span class="text-sm font-bold text-gray-800 dark:text-slate-200">
                  {{ selectedPatientVitals.pulse_rate }}
                  <span class="text-[10px] text-gray-400">bpm</span>
                </span>
              </div>
              <div
                class="bg-white dark:bg-slate-900 p-3 rounded-xl border border-gray-100 dark:border-slate-800"
              >
                <span
                  class="block text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
                  >Temperature</span
                >
                <span class="text-sm font-bold text-gray-800 dark:text-slate-200">
                  {{ selectedPatientVitals.temperature }}
                  <span class="text-[10px] text-gray-400">°F</span>
                </span>
              </div>
              <div
                class="bg-white dark:bg-slate-900 p-3 rounded-xl border border-gray-100 dark:border-slate-800"
              >
                <span
                  class="block text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
                  >Respiration</span
                >
                <span class="text-sm font-bold text-gray-800 dark:text-slate-200">
                  {{ selectedPatientVitals.respiration_rate }}
                  <span class="text-[10px] text-gray-400">/min</span>
                </span>
              </div>
              <div
                class="bg-white dark:bg-slate-900 p-3 rounded-xl border border-gray-100 dark:border-slate-800 col-span-2 sm:col-span-1"
              >
                <span
                  class="block text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1 font-bold text-teal-600"
                  >Recorded By</span
                >
                <span class="text-xs font-bold text-gray-800 dark:text-slate-200 truncate block">
                  Nurse: {{ selectedPatientVitals.recorded_by || 'Staff' }}
                </span>
              </div>
              <div
                v-if="selectedPatientVitals.notes"
                class="col-span-full bg-white dark:bg-slate-900 p-3 rounded-xl border border-gray-100 dark:border-slate-800"
              >
                <span
                  class="block text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
                  >Vitals Notes</span
                >
                <p class="text-xs italic text-gray-500 dark:text-slate-400">
                  "{{ selectedPatientVitals.notes }}"
                </p>
              </div>
            </div>
          </div>

          <!-- Appointment selector (optional) -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400"
              >Linked Appointment
              <span class="text-gray-400 text-xs font-normal ml-1">(optional)</span></label
            >
            <select
              v-model="writeRecord.appointment_id"
              :disabled="!writeRecord.patient_id"
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value="">No appointment linked</option>
              <option v-for="a in writeRecordPatientAppointments" :key="a.id" :value="a.id">
                {{ formatDate(a.appointment_date) }} — {{ a.status }}
              </option>
            </select>
            <p
              v-if="writeRecord.patient_id && writeRecordPatientAppointments.length === 0"
              class="text-xs text-gray-400 px-1"
            >
              No confirmed/completed appointments for this patient.
            </p>
          </div>

          <!-- Diagnosis -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400"
              >Diagnosis <span class="text-red-500 ml-0.5">*</span></label
            >
            <textarea
              v-model="writeRecord.diagnosis"
              required
              rows="3"
              placeholder="Primary diagnosis and clinical findings..."
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 resize-none"
            ></textarea>
          </div>

          <!-- Treatment -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400"
              >Treatment Plan</label
            >
            <textarea
              v-model="writeRecord.treatment"
              rows="3"
              placeholder="Recommended treatment and procedures..."
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 resize-none"
            ></textarea>
          </div>

          <!-- Prescription -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400"
              >Prescription</label
            >
            <textarea
              v-model="writeRecord.prescription"
              rows="2"
              placeholder="Medications, dosage... (comma-separated for pills display)"
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 resize-none"
            ></textarea>
          </div>

          <!-- Notes -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400"
              >Additional Notes</label
            >
            <textarea
              v-model="writeRecord.notes"
              rows="2"
              placeholder="Any additional observations or follow-up notes..."
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 resize-none"
            ></textarea>
          </div>

          <div class="flex gap-4 pt-4">
            <button
              type="button"
              @click="showWriteRecordModal = false"
              class="flex-1 py-4 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isSubmittingRecord"
              class="flex-1 py-4 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <div
                v-if="isSubmittingRecord"
                class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"
              ></div>
              {{ isSubmittingRecord ? 'Saving...' : 'Save Record' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Transition>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- Patient History Modal -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <Transition name="fade">
    <div
      v-if="showHistoryModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-2xl w-full p-10 shadow-premium-xl animate-scale-up max-h-[90vh] flex flex-col"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-8 flex-shrink-0">
          <div class="flex items-center gap-4">
            <div
              class="w-12 h-12 bg-teal-50 dark:bg-teal-900/30 rounded-2xl flex items-center justify-center text-teal-600 dark:text-teal-400 font-black text-lg"
            >
              {{ historyPatient?.full_name?.charAt(0) || 'P' }}
            </div>
            <div>
              <span
                class="text-[10px] font-black text-teal-600 bg-teal-50 dark:bg-teal-950 dark:text-teal-400 px-3 py-1 rounded-full uppercase tracking-widest"
              >
                Medical History
              </span>
              <h3 class="text-xl font-black text-gray-900 dark:text-white mt-1 tracking-tight">
                {{ historyPatient?.full_name }}
              </h3>
            </div>
          </div>
          <button
            @click="showHistoryModal = false"
            class="w-10 h-10 rounded-full bg-gray-50 dark:bg-slate-800 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-slate-200 transition-colors flex-shrink-0"
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

        <!-- Body -->
        <div class="overflow-y-auto flex-1 -mx-2 px-2">
          <div v-if="isLoadingHistory" class="flex items-center justify-center py-16">
            <div
              class="animate-spin rounded-full h-10 w-10 border-[3px] border-teal-600 border-t-transparent"
            ></div>
          </div>

          <div
            v-else-if="historyRecords.length === 0"
            class="flex flex-col items-center justify-center py-16"
          >
            <div
              class="w-16 h-16 bg-gray-50 dark:bg-slate-800 rounded-3xl flex items-center justify-center mb-4 text-gray-300 dark:text-slate-700"
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
            <p class="text-gray-500 dark:text-slate-400 text-sm font-medium">
              No medical records yet
            </p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="record in historyRecords"
              :key="record.id"
              class="bg-gray-50 dark:bg-slate-800/50 p-5 rounded-2xl border border-gray-100 dark:border-slate-700"
            >
              <div class="flex items-center justify-between mb-3">
                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  {{ formatDateShort(record.created_at || record.date) }}
                </span>
                <span
                  v-if="record.appointment_id"
                  class="px-2 py-0.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-[9px] font-black uppercase tracking-widest rounded-full"
                >
                  Appt. linked
                </span>
              </div>
              <p class="font-black text-gray-900 dark:text-white mb-2">{{ record.diagnosis }}</p>
              <p v-if="record.treatment" class="text-xs text-gray-600 dark:text-slate-300 mb-2">
                {{ record.treatment }}
              </p>
              <div v-if="record.prescription" class="flex flex-wrap gap-1.5 mb-2">
                <span
                  v-for="(med, idx) in record.prescription.split(',')"
                  :key="idx"
                  class="px-2.5 py-0.5 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-[9px] font-black rounded-full border border-emerald-100 dark:border-emerald-500/20"
                >
                  {{ med.trim() }}
                </span>
              </div>
              <p v-if="record.notes" class="text-xs text-gray-400 italic">{{ record.notes }}</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex-shrink-0 pt-6 mt-4 border-t border-gray-100 dark:border-slate-800">
          <button
            @click="showHistoryModal = false"
            class="w-full py-3.5 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
          >
            Close
          </button>
        </div>
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
