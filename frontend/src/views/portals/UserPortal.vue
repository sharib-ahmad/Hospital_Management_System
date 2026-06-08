<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import PortalBase from './PortalBase.vue'
import FormField from '../../components/FormField.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'
import { useCartStore } from '../../stores/cart'
const router = useRouter()
const notification = useNotificationStore()

// Data refs
const patients = ref<any[]>([])
const applications = ref<any[]>([])
const appointments = ref<any[]>([])
const medicalRecords = ref<any[]>([])
const doctors = ref<any[]>([])
const invoices = ref<any[]>([])
const isLoading = ref(true)
const isLoadingAppointments = ref(false)
const isLoadingRecords = ref(false)
const isLoadingInvoices = ref(false)

// Tab state
const activeTab = ref<'patients' | 'appointments' | 'records' | 'billing'>('patients')

// Vitals export state
const exportingVitals = ref(false)
const showExportModal = ref(false)

// Prescription parser state
const parsingRecordId = ref<string | null>(null)
const matchedMedicines = ref<any[]>([])
const showPrescriptionModal = ref(false)
const isParsingPrescription = ref(false)

// Simulated payment and receipt state
const showPaymentModal = ref(false)
const selectedInvoice = ref<any>(null)
const isProcessingPayment = ref(false)
const showReceiptModal = ref(false)

// Book Appointment modal state
const showBookModal = ref(false)
const bookingSubmitting = ref(false)
const bookForm = ref({
  patient_id: '',
  doctor_id: '',
  appointment_date: '',
  reason: '',
  appointment_type: 'consultation',
})
const recentlyBookedId = ref<string | null>(null)

// Slot-based booking state
const bookingDate = ref('')
const bookingSlot = ref('')
const availableSlots = ref<string[]>([])
const isLoadingSlots = ref(false)

const minDate = computed(() => {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  const localNow = new Date(now.getTime() - offset * 60 * 1000)
  return localNow.toISOString().slice(0, 10)
})

const fetchSlots = async () => {
  const isVitalsCheck = bookForm.value.appointment_type === 'vitals_check'
  if (!bookingDate.value || (!isVitalsCheck && !bookForm.value.doctor_id)) {
    availableSlots.value = []
    return
  }
  isLoadingSlots.value = true
  availableSlots.value = []
  bookingSlot.value = ''
  try {
    const params: Record<string, string> = {
      date: bookingDate.value,
      appointment_type: bookForm.value.appointment_type,
    }
    if (!isVitalsCheck) {
      params.doctor_id = bookForm.value.doctor_id
    }
    const res = await api.get('/appointments/slots', { params })
    availableSlots.value = res.data.data || []
  } catch (err: any) {
    notification.error(err.response?.data?.message || 'Failed to load available slots')
  } finally {
    isLoadingSlots.value = false
  }
}

import { watch } from 'vue'
watch([bookingDate, () => bookForm.value.doctor_id, () => bookForm.value.appointment_type], () => {
  fetchSlots()
})

// Stats
const stats = ref([
  {
    name: 'Profile Status',
    value: 'Verified',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    color: 'bg-emerald-600',
  },
  {
    name: 'Registered Patients',
    value: '0',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'bg-teal-600',
  },
  {
    name: 'Active Appointments',
    value: '0',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    color: 'bg-emerald-500',
  },
  {
    name: 'Medical Records',
    value: '0',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'bg-teal-500',
  },
])

// Computed: active (non-cancelled/completed) appointments
const activeAppointments = computed(() =>
  appointments.value.filter((a) => a.status === 'pending' || a.status === 'confirmed'),
)

const minDateTime = computed(() => {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  const localNow = new Date(now.getTime() - offset * 60 * 1000)
  return localNow.toISOString().slice(0, 16)
})

const loadData = async () => {
  try {
    const [patientsRes, appsRes] = await Promise.all([
      api.get('/patients/my'),
      api.get('/applications/my'),
    ])
    patients.value = patientsRes.data.data || []
    const allApps = appsRes.data.data || []
    applications.value = allApps.filter(
      (app: any) => app.status === 'pending' || app.status === 'rejected',
    )
    if (stats.value[1]) stats.value[1].value = patients.value.length.toString()
  } catch (error) {
    console.error('Failed to load data', error)
  } finally {
    isLoading.value = false
  }
}

const loadAppointments = async () => {
  if (appointments.value.length > 0) return
  isLoadingAppointments.value = true
  try {
    const [apptRes, doctorsRes] = await Promise.all([
      api.get('/appointments'),
      api.get('/doctors/'),
    ])
    appointments.value = apptRes.data.data || []
    doctors.value = doctorsRes.data.data || []
    if (stats.value[2]) stats.value[2].value = activeAppointments.value.length.toString()
  } catch (error) {
    notification.error('Failed to load appointments')
  } finally {
    isLoadingAppointments.value = false
  }
}

const loadMedicalRecords = async () => {
  if (medicalRecords.value.length > 0) return
  isLoadingRecords.value = true
  try {
    const res = await api.get('/medical-records/my')
    medicalRecords.value = res.data.data || []
    if (stats.value[3]) stats.value[3].value = medicalRecords.value.length.toString()
  } catch (error) {
    notification.error('Failed to load medical records')
  } finally {
    isLoadingRecords.value = false
  }
}

const loadInvoices = async () => {
  isLoadingInvoices.value = true
  try {
    const res = await api.get('/invoices')
    invoices.value = res.data.data || []
  } catch (err) {
    notification.error('Failed to load invoices')
  } finally {
    isLoadingInvoices.value = false
  }
}

const handlePayInvoice = async (invoiceId: string) => {
  try {
    await api.post(`/invoices/${invoiceId}/pay`)
    notification.success('Payment simulated successfully!')
    await loadInvoices()
  } catch (err: any) {
    notification.error(err.response?.data?.message || 'Payment simulation failed')
  }
}

const downloadVitalsDirect = async () => {
  exportingVitals.value = true
  try {
    const res = await api.get('/vitals/my/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'my_patients_vitals.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    notification.success('Vitals CSV downloaded successfully!')
    showExportModal.value = false
  } catch (err) {
    notification.error('Failed to download vitals CSV')
  } finally {
    exportingVitals.value = false
  }
}

const downloadRecordFile = async (record: any) => {
  try {
    const res = await api.get(`/medical-records/${record.id}/file`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', record.file_name || 'attachment.pdf')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (err) {
    notification.error('Failed to download prescription attachment file')
  }
}

const renderMarkdown = (text: string) => {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/_(.*?)_/g, '<em>$1</em>')
  html = html.replace(/^### (.*?)$/gm, '<h4 class="text-xs font-black mt-2 mb-1 text-gray-800 dark:text-slate-100">$1</h4>')
  html = html.replace(/^- (.*?)$/gm, '<li class="list-disc ml-4 text-[11px] text-gray-600 dark:text-slate-350">$1</li>')
  html = html.replace(/\n/g, '<br />')
  
  return html
}

const triggerVitalsExportJob = async () => {
  exportingVitals.value = true
  try {
    await api.post('/vitals/my/export-job')
    notification.success('Background export job triggered! Check your email shortly.')
    showExportModal.value = false
  } catch (err) {
    notification.error('Failed to trigger vitals export job')
  } finally {
    exportingVitals.value = false
  }
}

const parsePrescriptionText = async (recordId: string) => {
  parsingRecordId.value = recordId
  isParsingPrescription.value = true
  matchedMedicines.value = []
  showPrescriptionModal.value = true
  try {
    const res = await api.get(`/medical-records/${recordId}/parse-prescription`)
    matchedMedicines.value = res.data.data || []
  } catch (err) {
    notification.error('Failed to scan prescription')
  } finally {
    isParsingPrescription.value = false
  }
}

const addPrescribedToCart = () => {
  const cart = useCartStore()
  let addedCount = 0
  matchedMedicines.value.forEach((med) => {
    if (med.stock > 0) {
      cart.addToCart(med)
      addedCount++
    }
  })
  if (addedCount > 0) {
    notification.success(`Successfully added ${addedCount} medicines to basket!`)
    showPrescriptionModal.value = false
    router.push('/store')
  } else {
    notification.error('No matched medicines are currently in stock.')
  }
}

const openPaymentModal = (invoice: any) => {
  selectedInvoice.value = invoice
  showPaymentModal.value = true
}

const triggerPaymentSimulation = async () => {
  if (!selectedInvoice.value) return
  isProcessingPayment.value = true
  try {
    await handlePayInvoice(selectedInvoice.value.id)
    showPaymentModal.value = false
  } finally {
    isProcessingPayment.value = false
  }
}

const printReceipt = (invoice: any) => {
  selectedInvoice.value = invoice
  showReceiptModal.value = true
}

const triggerNativePrint = () => {
  window.print()
}

const switchTab = async (tab: 'patients' | 'appointments' | 'records' | 'billing') => {
  activeTab.value = tab
  if (tab === 'appointments') await loadAppointments()
  if (tab === 'records') await loadMedicalRecords()
  if (tab === 'billing') await loadInvoices()
}

const openBookModal = () => {
  bookForm.value = {
    patient_id: '',
    doctor_id: '',
    appointment_date: '',
    reason: '',
    appointment_type: 'consultation',
  }
  bookingDate.value = ''
  bookingSlot.value = ''
  availableSlots.value = []
  showBookModal.value = true
}

const handleBookAppointment = async () => {
  const isVitalsCheck = bookForm.value.appointment_type === 'vitals_check'
  if (
    !bookForm.value.patient_id ||
    (!isVitalsCheck && !bookForm.value.doctor_id) ||
    !bookingDate.value ||
    !bookingSlot.value
  ) {
    notification.error('Please select a patient, date and time slot')
    return
  }
  bookingSubmitting.value = true
  try {
    const appointmentDateStr = `${bookingDate.value}T${bookingSlot.value}:00`
    await api.post('/appointments', {
      patient_id: bookForm.value.patient_id,
      doctor_id: isVitalsCheck ? null : bookForm.value.doctor_id,
      appointment_date: appointmentDateStr,
      reason: bookForm.value.reason,
      appointment_type: bookForm.value.appointment_type,
    })
    notification.success('Appointment booked successfully!')
    showBookModal.value = false
    // Force reload
    appointments.value = []
    await loadAppointments()
    // Pulse the first new appointment after reload
    if (appointments.value.length > 0) {
      recentlyBookedId.value = appointments.value[0]?.id ?? null
      setTimeout(() => {
        recentlyBookedId.value = null
      }, 2200)
    }
  } catch (error: any) {
    const msg = error.response?.data?.message || 'Failed to book appointment'
    notification.error(msg)
  } finally {
    bookingSubmitting.value = false
  }
}

const cancelAppointment = async (aptId: string) => {
  try {
    await api.put(`/appointments/${aptId}`, { status: 'cancelled' })
    notification.success('Appointment cancelled')
    const idx = appointments.value.findIndex((a) => a.id === aptId)
    if (idx !== -1) appointments.value[idx].status = 'cancelled'
    if (stats.value[2]) stats.value[2].value = activeAppointments.value.length.toString()
  } catch (error) {
    notification.error('Failed to cancel appointment')
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
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatRecordDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  const date = new Date(normalizeDate(dateString))
  return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
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
  <PortalBase role="user" title="Welcome to MediFlow" :stats="stats">
    <template #main>
      <!-- ── Pill Tab Switcher ─────────────────────────────── -->
      <div
        class="flex items-center p-1.5 bg-gray-100 dark:bg-slate-800/50 rounded-2xl w-fit mb-8 border border-gray-200/50 dark:border-slate-700/50 flex-wrap gap-1"
      >
        <button
          @click="switchTab('patients')"
          :class="`px-5 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'patients'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          My Patients
        </button>
        <button
          @click="switchTab('appointments')"
          :class="`px-5 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'appointments'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Appointments
        </button>
        <button
          @click="switchTab('records')"
          :class="`px-5 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'records'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Medical Records
        </button>
        <button
          @click="switchTab('billing')"
          :class="`px-5 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest transition-all ${
            activeTab === 'billing'
              ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Billing & Invoices
        </button>
      </div>

      <!-- ════════════════════════════════════════════════════ -->
      <!--  TAB 1 — MY PATIENTS                               -->
      <!-- ════════════════════════════════════════════════════ -->
      <div v-if="activeTab === 'patients'" class="space-y-8">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
            My Registered Patients
          </h3>
          <div class="flex items-center gap-3">
            <button
              v-if="patients.length > 0"
              @click="showExportModal = true"
              class="px-5 py-2.5 bg-blue-600/10 text-blue-600 dark:text-blue-400 font-bold rounded-xl hover:bg-blue-600 hover:text-white transition-all text-sm flex items-center gap-2 border border-blue-600/10"
            >
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
                  stroke-width="2.5"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Export Vitals (CSV)
            </button>
            <button
              @click="router.push('/register-patient')"
              class="px-5 py-2.5 bg-emerald-600/10 text-emerald-600 dark:text-emerald-400 font-bold rounded-xl hover:bg-emerald-600 hover:text-white transition-all text-sm flex items-center gap-2"
            >
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
                  stroke-width="3"
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Register Patient
            </button>
          </div>
        </div>

        <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="i in 4"
            :key="i"
            class="bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-gray-100 dark:border-slate-800 shadow-premium"
          >
            <div class="flex items-start justify-between mb-6">
              <div class="skeleton w-14 h-14 rounded-2xl"></div>
              <div class="skeleton h-6 w-16 rounded-full"></div>
            </div>
            <div class="skeleton h-5 w-3/4 mb-2"></div>
            <div class="skeleton h-3 w-1/2 mb-2"></div>
            <div class="skeleton h-3 w-2/3 mb-8"></div>
            <div class="skeleton h-px w-full mb-4"></div>
            <div class="skeleton h-3 w-1/3"></div>
          </div>
        </div>

        <div
          v-else-if="patients.length === 0"
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
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
          <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
            No patients registered
          </h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium mb-8">
            Register yourself or your family members to start managing health records and
            appointments.
          </p>
          <button
            @click="router.push('/register-patient')"
            class="px-8 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/20 hover:-translate-y-1 transition-all uppercase text-xs tracking-widest"
          >
            Start Registration
          </button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="patient in patients"
            :key="patient.id"
            class="card-animate glass p-8 rounded-[2rem] border border-white/40 dark:border-white/5 hover:border-emerald-500/30 transition-all group shadow-premium"
          >
            <div class="flex items-start justify-between mb-6">
              <div
                class="w-14 h-14 bg-emerald-50 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center text-emerald-600 shadow-sm group-hover:scale-110 transition-transform"
              >
                <span class="font-black text-xl">{{ patient.full_name?.charAt(0) || 'P' }}</span>
              </div>
              <span
                class="px-4 py-1.5 bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 text-[10px] font-black uppercase tracking-widest rounded-full border border-emerald-200/50 dark:border-emerald-500/20"
              >
                {{ patient.blood_group }}
              </span>
            </div>
            <h3 class="text-xl font-black text-gray-900 dark:text-white mb-1 tracking-tight">
              {{ patient.full_name }}
            </h3>
            <p
              class="text-[10px] text-emerald-600 dark:text-emerald-400 font-black uppercase tracking-[0.2em] mb-3"
            >
              {{ patient.relation }}
            </p>
            <p
              class="text-xs text-gray-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-6 space-y-1"
            >
              Sex: {{ patient.gender }} <br />
              DOB: {{ patient.date_of_birth }} <br />
              <span
                v-if="patient.assigned_doctor_name"
                class="block mt-2 text-indigo-600 dark:text-indigo-400"
              >
                Doctor: {{ patient.assigned_doctor_name }} ({{
                  patient.assigned_doctor_specialization
                }})
              </span>
              <span v-else class="block mt-2 text-amber-500"> Doctor: Pending Assignment </span>
            </p>

            <button
              @click="router.push(`/patients/${patient.id}`)"
              class="w-full mb-4 py-2.5 bg-emerald-50 hover:bg-emerald-100 dark:bg-slate-800 dark:hover:bg-slate-700 text-emerald-600 dark:text-emerald-400 text-xs font-black uppercase tracking-widest rounded-xl transition-all flex items-center justify-center gap-2 border border-emerald-100/50 dark:border-slate-700/50"
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
                  d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"
                />
              </svg>
              View Vitals & Stats
            </button>

            <div
              class="pt-6 border-t border-gray-100 dark:border-slate-800 flex items-center justify-between"
            >
              <span class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]"
                >Clinical Records</span
              >
              <div
                class="w-8 h-8 rounded-full bg-gray-50 dark:bg-slate-800 flex items-center justify-center group-hover:bg-emerald-600 group-hover:text-white transition-all cursor-pointer"
              >
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
                    stroke-width="3"
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Pending/Rejected Applications -->
        <div v-if="applications.length > 0" class="space-y-8 pt-4">
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-amber-500 rounded-full"></span>
            Registration Progress
          </h3>

          <div class="grid grid-cols-1 gap-6">
            <div
              v-for="app in applications"
              :key="app.id"
              class="glass p-6 rounded-3xl border border-white/40 dark:border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-premium"
            >
              <div class="flex items-center gap-6">
                <div
                  :class="`w-12 h-12 rounded-2xl flex items-center justify-center ${app.status === 'pending' ? 'bg-amber-50 text-amber-600' : 'bg-red-50 text-red-600'}`"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      v-if="app.status === 'pending'"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                    <path
                      v-else
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </div>
                <div>
                  <h4 class="text-lg font-black text-gray-900 dark:text-white">
                    <span v-if="app.role_applied === 'doctor'">Doctor Staff Application</span>
                    <span v-else-if="app.role_applied === 'nurse'">Nurse Staff Application</span>
                    <span v-else>{{ app.patient_full_name }}</span>
                  </h4>
                  <p class="text-xs text-gray-500 font-bold uppercase tracking-widest mt-0.5">
                    <span v-if="app.role_applied === 'doctor'">
                      {{ app.specialization || 'General Medicine' }} • Professional Staff
                    </span>
                    <span v-else-if="app.role_applied === 'nurse'">
                      Nurse Staff Registry • Professional Staff
                    </span>
                    <span v-else> {{ app.relation }} • Patient Registration </span>
                  </p>
                </div>
              </div>

              <div class="flex flex-col md:items-end gap-2">
                <div class="flex items-center gap-2">
                  <span
                    :class="`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${app.status === 'pending' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`"
                  >
                    {{ app.status }}
                  </span>
                </div>
                <p
                  v-if="app.reason && app.status === 'rejected'"
                  class="text-xs text-red-500 font-bold max-w-sm md:text-right"
                >
                  {{ app.reason }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════ -->
      <!--  TAB 2 — APPOINTMENTS                              -->
      <!-- ════════════════════════════════════════════════════ -->
      <div v-else-if="activeTab === 'appointments'" class="space-y-6">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-teal-600 rounded-full"></span>
            My Appointments
          </h3>
          <button
            @click="openBookModal"
            class="px-5 py-2.5 bg-emerald-600 text-white font-black rounded-xl hover:bg-emerald-700 transition-all text-sm flex items-center gap-2 shadow-lg shadow-emerald-500/20"
          >
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
                stroke-width="3"
                d="M12 4v16m8-8H4"
              />
            </svg>
            Book Appointment
          </button>
        </div>

        <!-- Loading skeleton -->
        <div v-if="isLoadingAppointments" class="space-y-4">
          <div
            v-for="i in 3"
            :key="i"
            class="bg-gray-50 dark:bg-slate-800/40 p-6 rounded-[2rem] border border-gray-100 dark:border-slate-800"
          >
            <div class="flex items-center gap-4 mb-4">
              <div class="skeleton w-12 h-12 rounded-2xl"></div>
              <div class="flex-1 space-y-2">
                <div class="skeleton h-4 w-1/2"></div>
                <div class="skeleton h-3 w-1/3"></div>
              </div>
              <div class="skeleton h-6 w-20 rounded-xl"></div>
            </div>
            <div class="skeleton h-3 w-2/3 mb-3"></div>
            <div class="skeleton h-16 rounded-2xl mb-4"></div>
            <div class="skeleton h-10 rounded-xl"></div>
          </div>
        </div>

        <!-- Empty state -->
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
          <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">No appointments yet</h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium mb-8">
            Book your first appointment with a doctor to get started.
          </p>
          <button
            @click="openBookModal"
            class="px-8 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/20 hover:-translate-y-1 transition-all uppercase text-xs tracking-widest"
          >
            Book Now
          </button>
        </div>

        <!-- Appointment Cards -->
        <div v-else class="space-y-4">
          <div
            v-for="apt in appointments"
            :key="apt.id"
            :class="`card-animate group bg-gray-50 dark:bg-slate-800/40 p-6 rounded-[2rem] border transition-all duration-300 shadow-sm hover:shadow-premium ${
              recentlyBookedId === apt.id
                ? 'success-pulse border-emerald-400 dark:border-emerald-600'
                : 'border-gray-100 dark:border-slate-800 hover:border-emerald-500/30'
            }`"
          >
            <div class="flex items-center justify-between flex-wrap gap-4 mb-4">
              <div class="flex items-center gap-4">
                <div
                  class="w-12 h-12 rounded-2xl bg-white dark:bg-slate-900 flex items-center justify-center shadow-sm text-emerald-600 font-black text-lg border border-gray-100 dark:border-slate-800"
                >
                  {{ apt.patient_name?.charAt(0) || 'P' }}
                </div>
                <div>
                  <h4 class="font-black text-gray-900 dark:text-white">{{ apt.patient_name }}</h4>
                  <p
                    class="text-[10px] text-teal-600 dark:text-teal-400 font-black uppercase tracking-widest mt-0.5"
                  >
                    Dr. {{ apt.doctor_name }}
                  </p>
                </div>
              </div>
              <span
                :class="`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest ${getStatusColor(apt.status)}`"
              >
                {{ apt.status }}
              </span>
            </div>

            <div class="space-y-3 mb-5">
              <!-- Date -->
              <div class="flex items-center gap-3 text-gray-500 dark:text-slate-400">
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
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span class="text-xs font-bold uppercase tracking-wider">{{
                  formatDate(apt.appointment_date)
                }}</span>
              </div>
              <!-- Appointment type / fee -->
              <div class="flex items-center gap-3 text-gray-500 dark:text-slate-400">
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
                    apt.appointment_type === 'vitals_check'
                      ? 'text-teal-600 dark:text-teal-400'
                      : ''
                  }`"
                >
                  {{ getFeeDisplay(apt) || apt.appointment_type }}
                </span>
              </div>
              <!-- Reason -->
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

            <!-- Cancel button for pending -->
            <div v-if="apt.status === 'pending'" class="flex items-center gap-3">
              <button
                @click="cancelAppointment(apt.id)"
                class="flex-1 py-3 bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-rose-600 hover:text-white transition-all border border-rose-100 dark:border-rose-500/20"
              >
                Cancel Appointment
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════ -->
      <!--  TAB 3 — MEDICAL RECORDS                           -->
      <!-- ════════════════════════════════════════════════════ -->
      <div v-else-if="activeTab === 'records'" class="space-y-6">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-indigo-600 rounded-full"></span>
            Medical Records
          </h3>
        </div>

        <!-- Loading skeleton -->
        <div v-if="isLoadingRecords" class="space-y-6">
          <div
            v-for="i in 2"
            :key="i"
            class="bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-gray-100 dark:border-slate-800 shadow-premium"
          >
            <div class="flex items-start justify-between mb-6">
              <div class="space-y-2">
                <div class="skeleton h-5 w-40"></div>
                <div class="skeleton h-3 w-24"></div>
              </div>
              <div class="skeleton h-6 w-24 rounded-full"></div>
            </div>
            <div class="skeleton h-px w-full mb-6"></div>
            <div class="grid grid-cols-2 gap-4">
              <div class="skeleton h-20 rounded-2xl"></div>
              <div class="skeleton h-20 rounded-2xl"></div>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div
          v-else-if="medicalRecords.length === 0"
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
            No medical records found
          </h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium">
            Your medical records will appear here once a doctor adds them after your consultation.
          </p>
        </div>

        <!-- Records list -->
        <div v-else class="space-y-6">
          <div
            v-for="record in medicalRecords"
            :key="record.id"
            class="card-animate bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-gray-100 dark:border-slate-800 shadow-premium hover:-translate-y-0.5 transition-all duration-300"
          >
            <!-- Header row -->
            <div class="flex items-start justify-between flex-wrap gap-4 mb-6">
              <div>
                <span
                  class="text-[10px] font-black text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1 rounded-full uppercase tracking-widest border border-indigo-100 dark:border-indigo-500/20"
                >
                  Medical Record
                </span>
                <h4 class="text-xl font-black text-gray-900 dark:text-white mt-3 tracking-tight">
                  {{ record.diagnosis || 'General Record' }}
                </h4>
                <p
                  class="text-xs text-gray-400 dark:text-slate-500 font-bold uppercase tracking-widest mt-1"
                >
                  Patient ID: {{ record.patient_id?.substring(0, 8) }}...
                </p>
              </div>
              <div class="text-right">
                <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">
                  Record Date
                </p>
                <p class="text-sm font-bold text-gray-700 dark:text-slate-300">
                  {{ formatRecordDate(record.created_at || record.record_date) }}
                </p>
              </div>
            </div>

            <!-- Details grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Diagnosis -->
              <div
                class="p-4 bg-emerald-50/50 dark:bg-emerald-900/10 rounded-2xl border border-emerald-100/50 dark:border-emerald-500/10"
              >
                <p
                  class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest mb-2"
                >
                  Diagnosis
                </p>
                <p class="text-sm text-gray-700 dark:text-slate-300 font-medium leading-relaxed">
                  {{ record.diagnosis || '—' }}
                </p>
              </div>

              <!-- Treatment -->
              <div
                class="p-4 bg-teal-50/50 dark:bg-teal-900/10 rounded-2xl border border-teal-100/50 dark:border-teal-500/10"
              >
                <p
                  class="text-[10px] font-black text-teal-600 dark:text-teal-400 uppercase tracking-widest mb-2"
                >
                  Treatment
                </p>
                <p class="text-sm text-gray-700 dark:text-slate-300 font-medium leading-relaxed">
                  {{ record.treatment || '—' }}
                </p>
              </div>

              <!-- Prescription (if any) -->
              <div
                v-if="record.prescription"
                class="p-4 bg-indigo-50/50 dark:bg-indigo-900/10 rounded-2xl border border-indigo-100/50 dark:border-indigo-500/10 flex flex-col justify-between"
              >
                <div>
                  <p
                    class="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest mb-2"
                  >
                    Prescription
                  </p>
                  <p class="text-sm text-gray-700 dark:text-slate-300 font-medium leading-relaxed">
                    {{ record.prescription }}
                  </p>
                </div>
                <button
                  @click="parsePrescriptionText(record.id)"
                  class="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-750 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-all self-start flex items-center gap-1.5 shadow-sm"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-3.5 w-3.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2.5"
                      d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17"
                    />
                  </svg>
                  Order Prescribed Medicines
                </button>
              </div>

              <!-- Notes (if any) -->
              <div
                v-if="record.notes"
                class="p-4 bg-amber-50/50 dark:bg-amber-900/10 rounded-2xl border border-amber-100/50 dark:border-amber-500/10"
              >
                <p
                  class="text-[10px] font-black text-amber-600 dark:text-amber-400 uppercase tracking-widest mb-2"
                >
                  Notes
                </p>
                <p
                  class="text-sm text-gray-700 dark:text-slate-350 font-medium leading-relaxed"
                  v-html="renderMarkdown(record.notes)"
                >
                </p>
              </div>

              <!-- Attached File (if any) -->
              <div
                v-if="record.file_path"
                class="col-span-full p-4 bg-emerald-50/50 dark:bg-emerald-900/10 rounded-2xl border border-emerald-100/50 dark:border-emerald-500/10 flex items-center justify-between mt-2"
              >
                <div class="flex items-center gap-2 min-w-0">
                  <span class="text-xl">📄</span>
                  <div class="min-w-0">
                    <p class="text-xs font-bold text-gray-800 dark:text-slate-200 truncate">{{ record.file_name || 'Prescription attachment' }}</p>
                    <p class="text-[9px] text-gray-400 dark:text-slate-500 uppercase font-black tracking-wider">Physician Prescription Attachment</p>
                  </div>
                </div>
                <button
                  type="button"
                  @click="downloadRecordFile(record)"
                  class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-black uppercase tracking-wider rounded-xl transition-all shadow-sm shrink-0"
                >
                  Download File
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════ -->
      <!--  TAB 4 — BILLING & INVOICES                        -->
      <!-- ════════════════════════════════════════════════════ -->
      <div v-else-if="activeTab === 'billing'" class="space-y-6">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-blue-600 rounded-full"></span>
            Billing & Invoices
          </h3>
        </div>

        <!-- Loading skeleton -->
        <div v-if="isLoadingInvoices" class="space-y-4">
          <div
            v-for="i in 3"
            :key="i"
            class="bg-gray-50 dark:bg-slate-800/40 p-6 rounded-[2rem] border border-gray-100 dark:border-slate-800"
          >
            <div class="flex items-center gap-4">
              <div class="skeleton w-12 h-12 rounded-2xl"></div>
              <div class="flex-1 space-y-2">
                <div class="skeleton h-4 w-1/3"></div>
                <div class="skeleton h-3 w-1/4"></div>
              </div>
              <div class="skeleton h-6 w-20 rounded-xl"></div>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div
          v-else-if="invoices.length === 0"
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">No invoices found</h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium">
            You don't have any pending or paid invoices in your records at the moment.
          </p>
        </div>

        <!-- Invoices List -->
        <div v-else class="space-y-4">
          <div
            v-for="invoice in invoices"
            :key="invoice.id"
            class="card-animate group bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-gray-100 dark:border-slate-800 hover:border-blue-500/30 shadow-sm hover:shadow-premium transition-all duration-300"
          >
            <div class="flex items-center justify-between flex-wrap gap-4">
              <div class="flex items-center gap-4">
                <div
                  class="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-950/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-black text-lg border border-blue-100/50 dark:border-blue-900/20"
                >
                  {{ invoice.invoice_type === 'consultation' ? '🩺' : '💊' }}
                </div>
                <div>
                  <h4 class="font-black text-gray-900 dark:text-white capitalize">
                    {{ invoice.invoice_type }} Invoice
                  </h4>
                  <p
                    class="text-xs text-gray-400 dark:text-slate-500 font-bold tracking-wider mt-0.5"
                  >
                    ID: {{ invoice.id }} • Patient:
                    {{ invoice.patient_name || invoice.patient_id?.substring(0, 8) }}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-4">
                <div class="text-right">
                  <p class="text-xl font-black text-gray-900 dark:text-white">
                    ${{ Number(invoice.amount).toFixed(2) }}
                  </p>
                  <p class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">
                    Created {{ formatDate(invoice.created_at) }}
                  </p>
                </div>
                <span
                  :class="`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest ${
                    invoice.status === 'paid'
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400'
                      : invoice.status === 'refunded'
                        ? 'bg-gray-100 text-gray-700 dark:bg-slate-800 dark:text-slate-400'
                        : 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-400'
                  }`"
                >
                  {{ invoice.status }}
                </span>
              </div>
            </div>

            <!-- Action footer -->
            <div
              class="mt-4 pt-4 border-t border-gray-100/50 dark:border-slate-800/60 flex justify-between items-center gap-3"
            >
              <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                Billing Method: Simulated Payment Gateway
              </span>
              <div class="flex items-center gap-2">
                <button
                  v-if="invoice.status === 'paid'"
                  @click="printReceipt(invoice)"
                  class="px-4 py-2 bg-gray-50 hover:bg-gray-100 dark:bg-slate-800 dark:hover:bg-slate-700 text-gray-700 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-xl transition-all border border-gray-100 dark:border-slate-700 flex items-center gap-1.5"
                >
                  🖨️ Print Receipt
                </button>
                <button
                  v-if="invoice.status === 'unpaid'"
                  @click="openPaymentModal(invoice)"
                  class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-black uppercase tracking-widest rounded-xl transition-all flex items-center gap-1.5 shadow-md shadow-blue-500/20"
                >
                  💳 Pay Now
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Sidebar ─────────────────────────────────────────── -->
    <template #sidebar>
      <!-- Pharmacy Section -->
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-8 shadow-premium relative overflow-hidden group"
      >
        <div
          class="absolute -right-4 -top-4 w-24 h-24 bg-emerald-600/10 rounded-full blur-2xl group-hover:bg-emerald-600/20 transition-all"
        ></div>

        <div
          class="w-14 h-14 bg-emerald-50 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center text-emerald-600 mb-6"
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
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
            />
          </svg>
        </div>

        <h3 class="text-xl font-black text-gray-900 dark:text-white mb-2 tracking-tight">
          MediStore
        </h3>
        <p class="text-sm text-gray-500 dark:text-slate-400 font-medium mb-8 leading-relaxed">
          Order prescribed medicines and health supplements directly to your home.
        </p>

        <div class="space-y-4 mb-8">
          <div
            class="flex items-center gap-4 p-4 bg-emerald-50/40 dark:bg-emerald-900/10 rounded-2xl border border-emerald-100/50 dark:border-emerald-500/10"
          >
            <div
              class="w-10 h-10 bg-white dark:bg-slate-900 rounded-xl flex items-center justify-center text-emerald-600 font-bold"
            >
              💊
            </div>
            <div class="flex-1">
              <h5 class="text-xs font-black text-gray-900 dark:text-white">Active Pharmacy</h5>
              <p class="text-[10px] text-gray-400 font-bold">100% Verified Medicines</p>
            </div>
            <span
              class="text-[10px] font-black text-emerald-600 bg-emerald-100/40 px-2 py-1 rounded"
              >Live</span
            >
          </div>
        </div>

        <RouterLink
          to="/store"
          class="w-full py-4 bg-emerald-600 text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-lg hover:shadow-emerald-500/20 hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2"
        >
          Browse Pharmacy Store
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </RouterLink>
      </div>

      <!-- Quick Links Card -->
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-8 shadow-premium mt-6"
      >
        <h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-widest mb-6">
          Quick Actions
        </h3>
        <div class="space-y-3">
          <button
            @click="
              switchTab('appointments')
              openBookModal();
            "
            class="w-full flex items-center gap-3 p-4 bg-emerald-50/50 dark:bg-emerald-900/10 rounded-2xl border border-emerald-100/50 dark:border-emerald-500/10 hover:border-emerald-500/40 transition-all text-left group"
          >
            <div
              class="w-9 h-9 bg-emerald-600/10 rounded-xl flex items-center justify-center text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white transition-all"
            >
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
                  stroke-width="2.5"
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </div>
            <span
              class="text-xs font-black text-gray-700 dark:text-slate-300 uppercase tracking-widest"
              >Book Appointment</span
            >
          </button>

          <button
            @click="router.push('/register-patient')"
            class="w-full flex items-center gap-3 p-4 bg-teal-50/50 dark:bg-teal-900/10 rounded-2xl border border-teal-100/50 dark:border-teal-500/10 hover:border-teal-500/40 transition-all text-left group"
          >
            <div
              class="w-9 h-9 bg-teal-600/10 rounded-xl flex items-center justify-center text-teal-600 group-hover:bg-teal-600 group-hover:text-white transition-all"
            >
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
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <span
              class="text-xs font-black text-gray-700 dark:text-slate-300 uppercase tracking-widest"
              >Register Patient</span
            >
          </button>
        </div>
      </div>

      <!-- Support Card -->
      <div
        class="bg-gradient-to-br from-emerald-600 to-teal-700 rounded-[2.5rem] p-8 text-white shadow-xl shadow-emerald-500/30 mt-6"
      >
        <h3 class="text-xl font-black mb-4 tracking-tight">Need Help?</h3>
        <p class="text-emerald-50 text-sm mb-8 font-medium leading-relaxed opacity-90">
          Our support team is available 24/7 for any questions regarding patient registration or
          medical services.
        </p>
        <button
          class="w-full py-4 bg-white text-emerald-600 rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-lg hover:-translate-y-1 transition-all"
        >
          Contact Support
        </button>
      </div>
    </template>
  </PortalBase>

  <!-- ════════════════════════════════════════════════════════ -->
  <!--  BOOK APPOINTMENT MODAL                                -->
  <!-- ════════════════════════════════════════════════════════ -->
  <Transition name="fade">
    <div
      v-if="showBookModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
      @click.self="showBookModal = false"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-10 shadow-premium-xl animate-scale-up max-h-[90vh] overflow-y-auto"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-8">
          <div>
            <span
              class="text-[10px] font-black text-emerald-600 bg-emerald-50 dark:bg-emerald-950 dark:text-emerald-400 px-3 py-1 rounded-full uppercase tracking-widest"
            >
              New Appointment
            </span>
            <h3 class="text-2xl font-black text-gray-900 dark:text-white mt-3 tracking-tight">
              Book Appointment
            </h3>
          </div>
          <button
            @click="showBookModal = false"
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

        <form @submit.prevent="handleBookAppointment" class="space-y-6">
          <!-- Checkup Type -->
          <div class="w-full space-y-2">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
              Checkup Type
            </label>
            <div class="flex gap-4">
              <label
                class="flex-1 flex items-center justify-between p-3.5 border rounded-2xl cursor-pointer transition-all bg-white dark:bg-slate-800/50"
                :class="
                  bookForm.appointment_type === 'consultation'
                    ? 'border-emerald-500 ring-2 ring-emerald-500/10'
                    : 'border-gray-200 dark:border-slate-700/50'
                "
              >
                <span class="text-xs font-black uppercase text-gray-800 dark:text-slate-200"
                  >Doctor Consult</span
                >
                <input
                  type="radio"
                  value="consultation"
                  v-model="bookForm.appointment_type"
                  class="text-emerald-500 focus:ring-emerald-500"
                />
              </label>
              <label
                class="flex-1 flex items-center justify-between p-3.5 border rounded-2xl cursor-pointer transition-all bg-white dark:bg-slate-800/50"
                :class="
                  bookForm.appointment_type === 'vitals_check'
                    ? 'border-emerald-500 ring-2 ring-emerald-500/10'
                    : 'border-gray-200 dark:border-slate-700/50'
                "
              >
                <span class="text-xs font-black uppercase text-gray-800 dark:text-slate-200"
                  >Vitals Screening</span
                >
                <input
                  type="radio"
                  value="vitals_check"
                  v-model="bookForm.appointment_type"
                  class="text-emerald-500 focus:ring-emerald-500"
                />
              </label>
            </div>
          </div>

          <!-- Select Patient -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
              Select Patient <span class="text-red-500 ml-0.5">*</span>
            </label>
            <select
              v-model="bookForm.patient_id"
              required
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
            >
              <option value="" disabled>Choose a registered patient</option>
              <option v-for="p in patients" :key="p.id" :value="p.id">
                {{ p.full_name }} ({{ p.relation }})
              </option>
            </select>
          </div>

          <!-- Select Doctor -->
          <div v-if="bookForm.appointment_type === 'consultation'" class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
              Select Doctor <span class="text-red-500 ml-0.5">*</span>
            </label>
            <select
              v-model="bookForm.doctor_id"
              required
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
            >
              <option value="" disabled>Choose a doctor</option>
              <option v-for="d in doctors" :key="d.id" :value="d.id">
                Dr. {{ d.full_name }} — {{ d.specialization || d.department_name || 'General' }}
              </option>
            </select>
          </div>

          <!-- Date Picker -->
          <FormField
            id="apt-date"
            label="Appointment Date"
            type="date"
            v-model="bookingDate"
            :min="minDate"
            required
          />

          <!-- Slot Selector -->
          <div class="w-full space-y-2">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
              Available Time Slots <span class="text-red-500 ml-0.5">*</span>
            </label>

            <!-- Loading state -->
            <div
              v-if="isLoadingSlots"
              class="flex items-center gap-2 py-3 text-xs text-gray-500 dark:text-slate-400"
            >
              <div
                class="animate-spin rounded-full h-4 w-4 border-2 border-emerald-600 border-t-transparent"
              ></div>
              <span>Checking slot availability...</span>
            </div>

            <!-- Warning states -->
            <div
              v-else-if="!bookingDate"
              class="text-xs text-gray-400 dark:text-slate-500 italic py-2"
            >
              Please select a date to view available time slots.
            </div>
            <div
              v-else-if="bookForm.appointment_type === 'consultation' && !bookForm.doctor_id"
              class="text-xs text-gray-400 dark:text-slate-500 italic py-2"
            >
              Please select a doctor to view available time slots.
            </div>
            <div
              v-else-if="availableSlots.length === 0"
              class="text-xs text-rose-500 font-medium py-2"
            >
              No slots available for this day. Please choose another date.
            </div>

            <!-- Slots Grid -->
            <div
              v-else
              class="grid grid-cols-4 gap-2 max-h-40 overflow-y-auto p-1.5 border border-gray-100 dark:border-slate-800 rounded-2xl"
            >
              <button
                v-for="slot in availableSlots"
                :key="slot"
                type="button"
                @click="bookingSlot = slot"
                :class="[
                  'py-2 px-3 text-xs font-bold rounded-xl border text-center transition-all duration-200 active:scale-95',
                  bookingSlot === slot
                    ? 'bg-emerald-600 text-white border-emerald-600 shadow-md shadow-emerald-600/15'
                    : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-slate-300 border-gray-200 dark:border-slate-700/50 hover:border-emerald-500/30',
                ]"
              >
                {{ slot }}
              </button>
            </div>
          </div>

          <!-- Reason -->
          <div class="w-full space-y-1.5">
            <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
              Reason for Visit
            </label>
            <textarea
              v-model="bookForm.reason"
              rows="3"
              placeholder="e.g. Routine check-up, fever, follow-up..."
              class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-500/10 dark:focus:ring-emerald-400/10 resize-none"
            ></textarea>
          </div>

          <!-- Buttons -->
          <div class="flex gap-4 pt-4">
            <button
              type="button"
              @click="showBookModal = false"
              class="flex-1 py-4 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="bookingSubmitting"
              class="flex-1 py-4 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <div
                v-if="bookingSubmitting"
                class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"
              ></div>
              {{ bookingSubmitting ? 'Booking...' : 'Confirm Booking' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Transition>

  <!-- ════════════════════════════════════════════════════════ -->
  <!--  EXPORT VITALS MODAL                                     -->
  <!-- ════════════════════════════════════════════════════════ -->
  <Transition name="fade">
    <div
      v-if="showExportModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
      @click.self="showExportModal = false"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-md w-full p-8 shadow-premium-xl animate-scale-up"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <span
              class="text-[10px] font-black text-blue-600 bg-blue-50 dark:bg-blue-950 dark:text-blue-400 px-3 py-1 rounded-full uppercase tracking-widest"
            >
              Data Export
            </span>
            <h3 class="text-xl font-black text-gray-900 dark:text-white mt-3 tracking-tight">
              Export Vitals History
            </h3>
          </div>
          <button
            @click="showExportModal = false"
            class="w-8 h-8 rounded-full bg-gray-50 dark:bg-slate-800 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-slate-200 transition-colors"
          >
            ✕
          </button>
        </div>

        <p class="text-xs text-gray-500 dark:text-slate-400 mb-6 leading-relaxed">
          Select how you want to export the vitals history for all patients registered under your
          profile. You can download the CSV directly to your browser or trigger a background job to
          receive it via email.
        </p>

        <div class="space-y-3">
          <button
            @click="downloadVitalsDirect"
            :disabled="exportingVitals"
            class="w-full p-4 bg-gray-50 hover:bg-gray-100 dark:bg-slate-800 dark:hover:bg-slate-700/80 border border-gray-200 dark:border-slate-700/50 rounded-2xl flex items-center gap-4 text-left transition-all duration-200"
          >
            <div
              class="w-10 h-10 bg-blue-100 dark:bg-blue-950 rounded-xl flex items-center justify-center text-blue-600 dark:text-blue-400 text-lg"
            >
              📥
            </div>
            <div class="flex-1">
              <h4 class="text-xs font-black text-gray-900 dark:text-white uppercase tracking-wider">
                Direct Download
              </h4>
              <p class="text-[10px] text-gray-400 mt-0.5">Instant CSV download in your browser</p>
            </div>
          </button>

          <button
            @click="triggerVitalsExportJob"
            :disabled="exportingVitals"
            class="w-full p-4 bg-gray-50 hover:bg-gray-100 dark:bg-slate-800 dark:hover:bg-slate-700/80 border border-gray-200 dark:border-slate-700/50 rounded-2xl flex items-center gap-4 text-left transition-all duration-200"
          >
            <div
              class="w-10 h-10 bg-indigo-100 dark:bg-indigo-950 rounded-xl flex items-center justify-center text-indigo-600 dark:text-indigo-400 text-lg"
            >
              ✉️
            </div>
            <div class="flex-1">
              <h4 class="text-xs font-black text-gray-900 dark:text-white uppercase tracking-wider">
                Send to Email
              </h4>
              <p class="text-[10px] text-gray-400 mt-0.5">Asynchronous background mailing task</p>
            </div>
          </button>
        </div>

        <div class="flex gap-4 pt-6 mt-6 border-t border-gray-100 dark:border-slate-800">
          <button
            type="button"
            @click="showExportModal = false"
            class="w-full py-3.5 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </Transition>

  <!-- ════════════════════════════════════════════════════════ -->
  <!--  PRESCRIPTION SCANNER MODAL                              -->
  <!-- ════════════════════════════════════════════════════════ -->
  <Transition name="fade">
    <div
      v-if="showPrescriptionModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
      @click.self="showPrescriptionModal = false"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-8 shadow-premium-xl animate-scale-up"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <span
              class="text-[10px] font-black text-indigo-600 bg-indigo-50 dark:bg-indigo-950 dark:text-indigo-400 px-3 py-1 rounded-full uppercase tracking-widest"
            >
              Prescription Integration
            </span>
            <h3 class="text-xl font-black text-gray-900 dark:text-white mt-3 tracking-tight">
              Prescription Parser Scanner
            </h3>
          </div>
          <button
            @click="showPrescriptionModal = false"
            class="w-8 h-8 rounded-full bg-gray-50 dark:bg-slate-800 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-slate-200 transition-colors"
          >
            ✕
          </button>
        </div>

        <!-- Scanning State -->
        <div
          v-if="isParsingPrescription"
          class="flex flex-col items-center justify-center py-12 space-y-4"
        >
          <div class="relative w-16 h-16">
            <div class="absolute inset-0 rounded-full border-4 border-indigo-600/20"></div>
            <div
              class="absolute inset-0 rounded-full border-4 border-indigo-600 border-t-transparent animate-spin"
            ></div>
            <div class="absolute inset-0 flex items-center justify-center text-xl">🔍</div>
          </div>
          <p
            class="text-xs text-gray-500 dark:text-slate-400 uppercase tracking-widest font-black animate-pulse"
          >
            Scanning prescription text...
          </p>
        </div>

        <div v-else>
          <!-- Match count -->
          <p class="text-xs text-gray-500 dark:text-slate-400 mb-6">
            We scanned the doctor's prescription text and found
            <span class="font-bold text-indigo-600 dark:text-indigo-400"
              >{{ matchedMedicines.length }} matches</span
            >
            in our pharmacy catalog.
          </p>

          <!-- Empty state -->
          <div
            v-if="matchedMedicines.length === 0"
            class="py-10 text-center border-2 border-dashed border-gray-100 dark:border-slate-800 rounded-2xl"
          >
            <p class="text-sm text-gray-400 dark:text-slate-500 font-medium">
              No matching medicines found in our catalog.
            </p>
          </div>

          <!-- Matches list -->
          <div v-else class="space-y-3 max-h-60 overflow-y-auto pr-1">
            <div
              v-for="med in matchedMedicines"
              :key="med.id"
              class="p-4 bg-gray-50 dark:bg-slate-800/40 border border-gray-100 dark:border-slate-800 rounded-2xl flex items-center justify-between gap-4"
            >
              <div>
                <h4
                  class="text-xs font-black text-gray-900 dark:text-white uppercase tracking-wider"
                >
                  {{ med.name }}
                </h4>
                <p class="text-[10px] text-gray-400 mt-0.5">
                  Category: {{ med.category }} • ${{ Number(med.price).toFixed(2) }}
                </p>
              </div>
              <div class="text-right">
                <span
                  v-if="med.stock > 0"
                  class="px-2.5 py-1 bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 text-[9px] font-black uppercase tracking-widest rounded-lg"
                >
                  In Stock ({{ med.stock }})
                </span>
                <span
                  v-else
                  class="px-2.5 py-1 bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-400 text-[9px] font-black uppercase tracking-widest rounded-lg"
                >
                  Out of Stock
                </span>
              </div>
            </div>
          </div>

          <!-- Cart Action -->
          <div class="flex gap-4 pt-6 mt-6 border-t border-gray-100 dark:border-slate-800">
            <button
              type="button"
              @click="showPrescriptionModal = false"
              class="flex-1 py-3.5 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="addPrescribedToCart"
              :disabled="matchedMedicines.filter((m) => m.stock > 0).length === 0"
              class="flex-1 py-3.5 bg-indigo-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-indigo-700 transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-md shadow-indigo-500/20"
            >
              🛒 Add to Basket
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>

  <!-- ════════════════════════════════════════════════════════ -->
  <!--  SIMULATED PAYMENT MODAL                                 -->
  <!-- ════════════════════════════════════════════════════════ -->
  <Transition name="fade">
    <div
      v-if="showPaymentModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
      @click.self="showPaymentModal = false"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-md w-full p-8 shadow-premium-xl animate-scale-up"
      >
        <div class="flex items-center justify-between mb-6">
          <div>
            <span
              class="text-[10px] font-black text-blue-600 bg-blue-50 dark:bg-blue-950 dark:text-blue-400 px-3 py-1 rounded-full uppercase tracking-widest"
            >
              Simulated Checkout
            </span>
            <h3 class="text-xl font-black text-gray-900 dark:text-white mt-3 tracking-tight">
              Pay Invoice
            </h3>
          </div>
          <button
            @click="showPaymentModal = false"
            class="w-8 h-8 rounded-full bg-gray-50 dark:bg-slate-800 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-slate-200 transition-colors"
          >
            ✕
          </button>
        </div>

        <div v-if="selectedInvoice" class="space-y-4">
          <div
            class="p-6 bg-blue-50/40 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/30 rounded-2xl text-center"
          >
            <p
              class="text-xs text-gray-400 dark:text-slate-500 uppercase tracking-widest font-bold"
            >
              Total Amount Due
            </p>
            <p class="text-3xl font-black text-blue-600 dark:text-blue-400 mt-2">
              ${{ Number(selectedInvoice.amount).toFixed(2) }}
            </p>
            <p class="text-[10px] text-gray-400 mt-1 uppercase tracking-wider font-bold capitalize">
              Type: {{ selectedInvoice.invoice_type }}
            </p>
          </div>

          <div class="space-y-3">
            <div class="flex justify-between text-xs">
              <span class="text-gray-400 font-bold uppercase tracking-wider">Invoice ID</span>
              <span class="text-gray-900 dark:text-white font-mono">{{ selectedInvoice.id }}</span>
            </div>
            <div class="flex justify-between text-xs">
              <span class="text-gray-400 font-bold uppercase tracking-wider">Payment Method</span>
              <span class="text-gray-900 dark:text-white font-black">Simulated Instant Check</span>
            </div>
          </div>

          <div class="flex gap-4 pt-6 border-t border-gray-100 dark:border-slate-800">
            <button
              type="button"
              @click="showPaymentModal = false"
              class="flex-1 py-3.5 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="triggerPaymentSimulation"
              :disabled="isProcessingPayment"
              class="flex-1 py-3.5 bg-blue-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-500/20 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <div
                v-if="isProcessingPayment"
                class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"
              ></div>
              {{ isProcessingPayment ? 'Processing...' : 'Simulate Payment' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>

  <!-- ════════════════════════════════════════════════════════ -->
  <!--  PRINTABLE RECEIPT OVERLAY / MODAL                       -->
  <!-- ════════════════════════════════════════════════════════ -->
  <Transition name="fade">
    <div
      v-if="showReceiptModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
      @click.self="showReceiptModal = false"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-10 shadow-premium-xl animate-scale-up print-container"
      >
        <div class="flex items-center justify-between mb-8 print:hidden">
          <h3 class="text-xl font-black text-gray-900 dark:text-white tracking-tight">
            Receipt / Proof of Payment
          </h3>
          <button
            @click="showReceiptModal = false"
            class="w-8 h-8 rounded-full bg-gray-50 dark:bg-slate-800 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-slate-200 transition-colors"
          >
            ✕
          </button>
        </div>

        <div v-if="selectedInvoice" class="space-y-6 text-gray-900 dark:text-white">
          <!-- Logo & Header -->
          <div class="text-center">
            <h2 class="text-2xl font-black tracking-tight text-emerald-600">
              MEDIFLOW CLINICAL GROUP
            </h2>
            <p class="text-[10px] text-gray-400 uppercase tracking-widest font-black mt-1">
              Hospital Management billing System
            </p>
          </div>

          <div
            class="border-t border-b border-dashed border-gray-200 dark:border-slate-800 py-4 space-y-2"
          >
            <div class="flex justify-between text-xs">
              <span class="text-gray-400 uppercase tracking-wider font-bold">Receipt ID</span>
              <span class="font-mono">{{ selectedInvoice.id }}</span>
            </div>
            <div class="flex justify-between text-xs">
              <span class="text-gray-400 uppercase tracking-wider font-bold">Transaction Date</span>
              <span>{{
                formatDate(selectedInvoice.updated_at || selectedInvoice.created_at)
              }}</span>
            </div>
            <div class="flex justify-between text-xs">
              <span class="text-gray-400 uppercase tracking-wider font-bold">Status</span>
              <span
                class="text-emerald-600 dark:text-emerald-400 uppercase font-black tracking-widest"
                >SUCCESSFULLY PAID</span
              >
            </div>
          </div>

          <div class="space-y-3">
            <h4 class="text-xs font-black text-gray-400 uppercase tracking-widest">
              Billing Breakdown
            </h4>
            <div class="flex justify-between text-sm py-2">
              <span class="capitalize font-bold text-gray-700 dark:text-slate-300"
                >{{ selectedInvoice.invoice_type }} charges</span
              >
              <span class="font-black">${{ Number(selectedInvoice.amount).toFixed(2) }}</span>
            </div>
            <div class="h-px bg-gray-100 dark:bg-slate-800"></div>
            <div class="flex justify-between text-base font-black">
              <span>Total Paid</span>
              <span class="text-emerald-600">${{ Number(selectedInvoice.amount).toFixed(2) }}</span>
            </div>
          </div>

          <p class="text-[9px] text-gray-400 text-center italic mt-8">
            Thank you for choosing MediFlow. This is an electronically generated proof of receipt.
          </p>

          <div class="flex gap-4 pt-6 border-t border-gray-100 dark:border-slate-800 print:hidden">
            <button
              type="button"
              @click="showReceiptModal = false"
              class="flex-1 py-3.5 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
            >
              Close
            </button>
            <button
              type="button"
              @click="triggerNativePrint"
              class="flex-1 py-3.5 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 transition-all flex items-center justify-center gap-1.5"
            >
              🖨️ Print Receipt
            </button>
          </div>
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

@media print {
  body * {
    visibility: hidden;
  }
  .print-container,
  .print-container * {
    visibility: visible;
  }
  .print-container {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    border: none;
    box-shadow: none;
    background: white;
    color: black;
  }
}
</style>
