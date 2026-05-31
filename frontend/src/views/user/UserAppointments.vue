<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import FormField from '../../components/FormField.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()

// Data refs
const appointments = ref<any[]>([])
const patients = ref<any[]>([])
const doctors = ref<any[]>([])
const isLoading = ref(true)
const bookingSubmitting = ref(false)

// Book Appointment modal state
const showBookModal = ref(false)
const bookForm = ref({
  patient_id: '',
  doctor_id: '',
  appointment_date: '',
  reason: '',
})

const minDateTime = computed(() => {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  const localNow = new Date(now.getTime() - offset * 60 * 1000)
  return localNow.toISOString().slice(0, 16)
})

// Load all required data
const loadData = async () => {
  isLoading.value = true
  try {
    const [apptRes, patientsRes, doctorsRes] = await Promise.all([
      api.get('/appointments'),
      api.get('/patients/my'),
      api.get('/doctors/'),
    ])
    appointments.value = apptRes.data.data || []
    patients.value = patientsRes.data.data || []
    doctors.value = doctorsRes.data.data || []
  } catch (error) {
    notification.error('Failed to load appointments data')
  } finally {
    isLoading.value = false
  }
}

const openBookModal = () => {
  bookForm.value = { patient_id: '', doctor_id: '', appointment_date: '', reason: '' }
  showBookModal.value = true
}

const handleBookAppointment = async () => {
  if (!bookForm.value.patient_id || !bookForm.value.doctor_id || !bookForm.value.appointment_date) {
    notification.error('Please fill all required fields')
    return
  }
  bookingSubmitting.value = true
  try {
    await api.post('/appointments', {
      patient_id: bookForm.value.patient_id,
      doctor_id: bookForm.value.doctor_id,
      appointment_date: new Date(bookForm.value.appointment_date).toISOString(),
      reason: bookForm.value.reason,
    })
    notification.success('Appointment booked successfully!')
    showBookModal.value = false
    await loadData()
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
    await loadData()
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

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'pending':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20'
    case 'confirmed':
      return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20'
    case 'completed':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-500/20'
    case 'cancelled':
      return 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400 border border-rose-200 dark:border-rose-500/20'
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-slate-800 dark:text-slate-400 border border-gray-200 dark:border-slate-700'
  }
}

onMounted(loadData)
</script>

<template>
  <DashboardLayout>
    <!-- Page Header -->
    <div class="mb-12 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <span
            class="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest border border-emerald-100 dark:border-emerald-500/20"
          >
            User Portal
          </span>
        </div>
        <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">
          Appointments
        </h1>
        <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
          Schedule and manage clinical consultations for your registered patients.
        </p>
      </div>
      <button
        @click="openBookModal"
        class="px-8 py-4 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/25 hover:-translate-y-0.5 transition-all uppercase tracking-widest text-xs flex items-center justify-center gap-3 shrink-0"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="3"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        Book Appointment
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-32">
      <div
        class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
      ></div>
    </div>

    <!-- Appointments List -->
    <div v-else-if="appointments.length > 0" class="max-w-4xl mx-auto space-y-6">
      <div
        v-for="apt in appointments"
        :key="apt.id"
        class="glass bg-white dark:bg-slate-900 p-6 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 hover:border-emerald-500/30 transition-all duration-300 shadow-premium flex flex-col justify-between"
      >
        <div>
          <!-- Card Header -->
          <div
            class="flex items-center justify-between flex-wrap gap-4 mb-5 pb-4 border-b border-gray-55 dark:border-slate-850"
          >
            <div class="flex items-center gap-4">
              <div
                class="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center shadow-sm text-emerald-600 font-black text-lg border border-emerald-100 dark:border-emerald-500/10"
              >
                {{ apt.patient_name?.charAt(0) || 'P' }}
              </div>
              <div>
                <h4 class="font-black text-gray-900 dark:text-white text-base leading-tight">
                  {{ apt.patient_name }}
                </h4>
                <p
                  class="text-[10px] text-teal-600 dark:text-teal-400 font-black uppercase tracking-widest mt-0.5"
                >
                  Dr. {{ apt.doctor_name }} ({{ apt.doctor_specialization || 'General Physician' }})
                </p>
              </div>
            </div>
            <span
              :class="`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${getStatusColor(apt.status)}`"
            >
              {{ apt.status }}
            </span>
          </div>

          <!-- Information Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
            <div
              class="p-4 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">
                Appointment Date & Time
              </p>
              <p
                class="text-xs text-gray-700 dark:text-slate-300 font-bold uppercase tracking-wider"
              >
                {{ formatDate(apt.appointment_date) }}
              </p>
            </div>
            <div
              class="p-4 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">
                Consultation Fee
              </p>
              <p class="text-xs text-emerald-600 dark:text-emerald-400 font-black">
                ${{
                  apt.consultation_fee != null ? Number(apt.consultation_fee).toFixed(2) : '0.00'
                }}
              </p>
            </div>
          </div>

          <!-- Reason / Notes -->
          <div
            v-if="apt.reason"
            class="p-5 bg-gray-50 dark:bg-slate-850 rounded-2xl border border-gray-100 dark:border-slate-800 mb-5"
          >
            <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1.5">
              Reason for Visit
            </p>
            <p class="text-xs text-gray-600 dark:text-slate-300 font-medium leading-relaxed italic">
              "{{ apt.reason }}"
            </p>
          </div>
        </div>

        <!-- Action Panel -->
        <div v-if="apt.status === 'pending'" class="flex items-center gap-3">
          <button
            @click="cancelAppointment(apt.id)"
            class="w-full py-3.5 bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-450 hover:bg-rose-600 hover:text-white border border-rose-100 dark:border-rose-900/30 font-black text-[10px] uppercase tracking-widest rounded-2xl transition-all"
          >
            Cancel Appointment
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else
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
      <h3 class="text-xl font-black text-gray-900 dark:text-white mb-2">
        No appointments scheduled
      </h3>
      <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium mb-8">
        Schedule your first consultation with a medical doctor.
      </p>
      <button
        @click="openBookModal"
        class="px-8 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/20 hover:-translate-y-0.5 transition-all uppercase text-xs tracking-widest"
      >
        Book Now
      </button>
    </div>

    <!-- Book Appointment Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="showBookModal"
          class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
          @click.self="showBookModal = false"
        >
          <Transition name="slide-up">
            <div
              v-if="showBookModal"
              class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-10 shadow-premium-xl overflow-y-auto max-h-[90vh]"
            >
              <!-- Modal Header -->
              <div class="flex items-center justify-between mb-8">
                <div>
                  <h2 class="text-2xl font-black text-gray-900 dark:text-white">
                    Book Appointment
                  </h2>
                  <p class="text-sm text-gray-500 dark:text-slate-400 font-medium mt-0.5">
                    Schedule a clinical session with an active doctor.
                  </p>
                </div>
                <button
                  @click="showBookModal = false"
                  class="w-10 h-10 flex items-center justify-center rounded-2xl bg-gray-100 dark:bg-slate-800 text-gray-500 dark:text-slate-400 hover:bg-gray-200 dark:hover:bg-slate-700 transition-all"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Form -->
              <form @submit.prevent="handleBookAppointment" class="space-y-6">
                <!-- Patient Selector -->
                <div class="w-full space-y-1.5">
                  <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
                    Patient Profile <span class="text-red-500 ml-0.5">*</span>
                  </label>
                  <select
                    v-model="bookForm.patient_id"
                    required
                    class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
                  >
                    <option value="" disabled>Select a patient profile</option>
                    <option v-for="pat in patients" :key="pat.id" :value="pat.id">
                      {{ pat.full_name }} ({{ pat.relation }})
                    </option>
                  </select>
                </div>

                <!-- Doctor Selector -->
                <div class="w-full space-y-1.5">
                  <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
                    Medical Doctor <span class="text-red-500 ml-0.5">*</span>
                  </label>
                  <select
                    v-model="bookForm.doctor_id"
                    required
                    class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
                  >
                    <option value="" disabled>Select a doctor</option>
                    <option v-for="doc in doctors" :key="doc.id" :value="doc.id">
                      Dr. {{ doc.full_name }} ({{ doc.specialization }}) - ${{
                        doc.consultation_fee
                      }}
                    </option>
                  </select>
                </div>

                <!-- Date & Time -->
                <FormField
                  id="appointment_date"
                  label="Appointment Date & Time"
                  type="datetime-local"
                  v-model="bookForm.appointment_date"
                  :min="minDateTime"
                  required
                />

                <!-- Reason -->
                <div class="w-full space-y-1.5">
                  <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
                    Reason / Symptoms
                  </label>
                  <textarea
                    v-model="bookForm.reason"
                    placeholder="Briefly describe your symptoms or visit purpose..."
                    rows="3"
                    class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 resize-none"
                  ></textarea>
                </div>

                <!-- Action Buttons -->
                <div class="flex gap-4 pt-2">
                  <button
                    type="button"
                    @click="showBookModal = false"
                    class="flex-1 py-3.5 rounded-2xl border border-gray-200 dark:border-slate-700 text-gray-700 dark:text-slate-300 text-[10px] font-black uppercase tracking-widest hover:bg-gray-50 dark:hover:bg-slate-800 transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    :disabled="bookingSubmitting"
                    class="flex-1 py-3.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 active:scale-95"
                  >
                    <div
                      v-if="bookingSubmitting"
                      class="animate-spin rounded-full h-4 w-4 border-[2px] border-white border-t-transparent"
                    ></div>
                    {{ bookingSubmitting ? 'Booking...' : 'Book Now' }}
                  </button>
                </div>
              </form>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </DashboardLayout>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}
</style>
