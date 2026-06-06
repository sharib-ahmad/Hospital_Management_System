<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import FormField from '../../components/FormField.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()

interface TimeInterval {
  start: string
  end: string
}

interface WeeklyAvailability {
  Monday?: TimeInterval[]
  Tuesday?: TimeInterval[]
  Wednesday?: TimeInterval[]
  Thursday?: TimeInterval[]
  Friday?: TimeInterval[]
  Saturday?: TimeInterval[]
  Sunday?: TimeInterval[]
}

interface DoctorProfile {
  id: string
  doctor_code: string
  specialization: string
  consultation_fee: number
  shift: string
  is_available: boolean
  experience_years: number
  license_number: string
  blood_group: string
  gender: string
  date_of_birth: string
  emergency_contact_number: string
  department_name: string
  full_name: string
  availability?: WeeklyAvailability
}

const profile = ref<DoctorProfile | null>(null)
const isLoading = ref(true)

// Edit modal state
const showEditModal = ref(false)
const isSaving = ref(false)
const editForm = ref({
  specialization: '',
  consultation_fee: 0,
  shift: '',
  is_available: false,
  experience_years: 0,
})
const formErrors = ref({
  specialization: '',
  consultation_fee: '',
  shift: '',
  experience_years: '',
})

// Weekly Availability state
const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const localAvailability = ref<Record<string, TimeInterval[]>>({})
const isSavingAvailability = ref(false)

const initializeAvailability = () => {
  const target = profile.value?.availability || {}
  const result: Record<string, TimeInterval[]> = {}
  daysOfWeek.forEach((day) => {
    const intervals = target[day as keyof WeeklyAvailability] || []
    result[day] = JSON.parse(JSON.stringify(intervals))
  })
  localAvailability.value = result
}

const isDayActive = (day: string) => {
  return localAvailability.value[day] && localAvailability.value[day].length > 0
}

const toggleDay = (day: string) => {
  if (isDayActive(day)) {
    localAvailability.value[day] = []
  } else {
    localAvailability.value[day] = [{ start: '09:00', end: '17:00' }]
  }
}

const addInterval = (day: string) => {
  if (!localAvailability.value[day]) {
    localAvailability.value[day] = []
  }
  const dayIntervals = localAvailability.value[day] || []
  const len = dayIntervals.length
  if (len > 0) {
    const lastEnd = dayIntervals[len - 1]!.end
    dayIntervals.push({ start: lastEnd, end: lastEnd })
  } else {
    dayIntervals.push({ start: '09:00', end: '17:00' })
  }
}

const removeInterval = (day: string, index: number) => {
  if (localAvailability.value[day]) {
    localAvailability.value[day].splice(index, 1)
  }
}

const saveAvailability = async () => {
  // Validate intervals
  for (const day of daysOfWeek) {
    const intervals = localAvailability.value[day] || []
    for (const interval of intervals) {
      if (!interval.start || !interval.end) {
        notification.error(`Please select a valid time range for ${day}.`)
        return
      }
      if (interval.start >= interval.end) {
        notification.error(`The start time must be earlier than the end time on ${day}.`)
        return
      }
    }
  }

  isSavingAvailability.value = true
  try {
    const payload: Record<string, TimeInterval[]> = {}
    daysOfWeek.forEach((day) => {
      if (localAvailability.value[day] && localAvailability.value[day].length > 0) {
        payload[day] = localAvailability.value[day]
      }
    })
    const res = await api.put('/doctors/me', { availability: payload })
    profile.value = res.data.data ?? res.data
    initializeAvailability()
    notification.success('Availability updated successfully')
  } catch {
    notification.error('Failed to update availability')
  } finally {
    isSavingAvailability.value = false
  }
}

const avatarLetter = computed(() => {
  return profile.value?.full_name?.charAt(0)?.toUpperCase() || 'D'
})

const shiftColor = computed(() => {
  switch (profile.value?.shift?.toLowerCase()) {
    case 'day':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-500/20'
    case 'night':
      return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 border-indigo-200 dark:border-indigo-500/20'
    case 'rotating':
      return 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400 border-teal-200 dark:border-teal-500/20'
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-slate-800 dark:text-slate-400 border-gray-200 dark:border-slate-700'
  }
})

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const formatPrice = (p: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(p)

const loadProfile = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/doctors/me')
    profile.value = res.data.data ?? res.data
    initializeAvailability()
  } catch {
    notification.error('Failed to load profile')
  } finally {
    isLoading.value = false
  }
}

const openEditModal = () => {
  if (!profile.value) return
  editForm.value = {
    specialization: profile.value.specialization ?? '',
    consultation_fee: profile.value.consultation_fee ?? 0,
    shift: profile.value.shift ?? '',
    is_available: profile.value.is_available ?? false,
    experience_years: profile.value.experience_years ?? 0,
  }
  formErrors.value = { specialization: '', consultation_fee: '', shift: '', experience_years: '' }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const validateForm = () => {
  let valid = true
  formErrors.value = { specialization: '', consultation_fee: '', shift: '', experience_years: '' }

  if (!editForm.value.specialization.trim()) {
    formErrors.value.specialization = 'Specialization is required.'
    valid = false
  }
  if (editForm.value.consultation_fee < 0) {
    formErrors.value.consultation_fee = 'Consultation fee must be 0 or more.'
    valid = false
  }
  if (!editForm.value.shift) {
    formErrors.value.shift = 'Shift is required.'
    valid = false
  }
  if (editForm.value.experience_years < 0) {
    formErrors.value.experience_years = 'Experience must be 0 or more.'
    valid = false
  }
  return valid
}

const saveProfile = async () => {
  if (!validateForm()) return
  isSaving.value = true
  try {
    const res = await api.put('/doctors/me', {
      specialization: editForm.value.specialization,
      consultation_fee: editForm.value.consultation_fee,
      shift: editForm.value.shift,
      is_available: editForm.value.is_available,
      experience_years: editForm.value.experience_years,
    })
    profile.value = res.data.data ?? res.data
    notification.success('Profile updated successfully')
    closeEditModal()
  } catch {
    notification.error('Failed to update profile')
  } finally {
    isSaving.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <DashboardLayout>
    <!-- Page Header -->
    <div class="mb-12">
      <div class="flex items-center gap-3 mb-2">
        <span
          class="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest border border-emerald-100 dark:border-emerald-500/20"
        >
          Doctor
        </span>
      </div>
      <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">My Profile</h1>
      <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
        View and manage your personal and professional medical information.
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-32">
      <div
        class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
      ></div>
    </div>

    <!-- Profile Layout -->
    <div v-else-if="profile" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Hero Card (Left Third) -->
      <div
        class="lg:col-span-1 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-8 shadow-premium flex flex-col items-center text-center hover:-translate-y-1 transition-all duration-300"
      >
        <!-- Avatar -->
        <div
          class="w-28 h-28 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-600/30 mb-5 ring-4 ring-emerald-100 dark:ring-emerald-900/40"
        >
          <span class="text-4xl font-black text-white">{{ avatarLetter }}</span>
        </div>

        <!-- Full Name -->
        <h2 class="text-2xl font-black text-gray-900 dark:text-white leading-tight mb-1">
          Dr. {{ profile.full_name }}
        </h2>

        <!-- Specialization -->
        <p class="text-sm font-bold text-gray-500 dark:text-slate-400 mb-1">
          {{ profile.specialization || 'General Physician' }}
        </p>

        <!-- Doctor Code -->
        <p
          class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest mb-4"
        >
          {{ profile.doctor_code }}
        </p>

        <!-- Shift Badge -->
        <span
          :class="`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${shiftColor} mb-3`"
        >
          {{ profile.shift || 'No Shift' }} Shift
        </span>

        <!-- Availability Badge -->
        <span
          :class="[
            'px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border',
            profile.is_available
              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/20'
              : 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400 border-rose-200 dark:border-rose-500/20',
          ]"
        >
          <span class="inline-flex items-center gap-1.5">
            <span
              :class="[
                'w-1.5 h-1.5 rounded-full',
                profile.is_available ? 'bg-emerald-500' : 'bg-rose-500',
              ]"
            ></span>
            {{ profile.is_available ? 'Available for Consult' : 'Not Available' }}
          </span>
        </span>

        <!-- Edit Button -->
        <button
          @click="openEditModal"
          class="mt-8 w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 shadow-lg shadow-emerald-600/25"
        >
          Edit Profile
        </button>
      </div>

      <!-- Right Two-Thirds Wrapper -->
      <div class="lg:col-span-2 space-y-8">
        <!-- Info Grid -->
        <div
          class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-10 shadow-premium hover:-translate-y-1 transition-all duration-300"
        >
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3 mb-8">
            <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
            Professional Details
          </h3>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <!-- Department -->
            <div
              class="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p
                class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1.5"
              >
                Department
              </p>
              <p class="text-sm font-bold text-gray-900 dark:text-white">
                {{ profile.department_name || '—' }}
              </p>
            </div>

            <!-- Consultation Fee -->
            <div
              class="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p
                class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1.5"
              >
                Consultation Fee
              </p>
              <p class="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                {{ formatPrice(profile.consultation_fee ?? 0) }}
              </p>
            </div>

            <!-- Experience -->
            <div
              class="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p
                class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1.5"
              >
                Experience
              </p>
              <p class="text-sm font-bold text-gray-900 dark:text-white">
                {{
                  profile.experience_years != null
                    ? `${profile.experience_years} Year${profile.experience_years !== 1 ? 's' : ''}`
                    : '—'
                }}
              </p>
            </div>

            <!-- License Number -->
            <div
              class="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p
                class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1.5"
              >
                License Number
              </p>
              <p class="text-sm font-bold text-gray-900 dark:text-white font-mono">
                {{ profile.license_number || '—' }}
              </p>
            </div>

            <!-- Blood Group -->
            <div
              class="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p
                class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1.5"
              >
                Blood Group
              </p>
              <p class="text-sm font-bold text-gray-900 dark:text-white">
                {{ profile.blood_group || '—' }}
              </p>
            </div>

            <!-- Gender -->
            <div
              class="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p
                class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1.5"
              >
                Gender
              </p>
              <p class="text-sm font-bold text-gray-900 dark:text-white capitalize">
                {{ profile.gender || '—' }}
              </p>
            </div>

            <!-- Date of Birth -->
            <div
              class="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p
                class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1.5"
              >
                Date of Birth
              </p>
              <p class="text-sm font-bold text-gray-900 dark:text-white">
                {{ formatDate(profile.date_of_birth) }}
              </p>
            </div>

            <!-- Emergency Contact -->
            <div
              class="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
            >
              <p
                class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1.5"
              >
                Emergency Contact
              </p>
              <p class="text-sm font-bold text-gray-900 dark:text-white">
                {{ profile.emergency_contact_number || '—' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Weekly Availability Card -->
        <div
          class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-10 shadow-premium hover:-translate-y-1 transition-all duration-300"
        >
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3 mb-6">
            <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
            Weekly Availability
          </h3>
          <p class="text-xs text-gray-500 dark:text-slate-400 font-medium mb-8">
            Configure your working time slots for each day of the week. Patients will only be able
            to book appointments during these intervals.
          </p>

          <div class="space-y-6">
            <div
              v-for="day in daysOfWeek"
              :key="day"
              class="p-6 bg-gray-50 dark:bg-slate-800/50 rounded-3xl border border-gray-100 dark:border-slate-700/50 space-y-4"
            >
              <div class="flex items-center justify-between">
                <span class="text-sm font-bold text-gray-900 dark:text-white">{{ day }}</span>
                <button
                  type="button"
                  @click="toggleDay(day)"
                  :class="[
                    'px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all duration-200 active:scale-95',
                    isDayActive(day)
                      ? 'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 border-emerald-100 dark:border-emerald-900/30'
                      : 'bg-gray-100 dark:bg-slate-800 text-gray-400 border-gray-200 dark:border-slate-700',
                  ]"
                >
                  {{ isDayActive(day) ? 'Active' : 'Inactive' }}
                </button>
              </div>

              <!-- Intervals list for this day -->
              <div v-if="isDayActive(day)" class="space-y-3 pt-2">
                <div
                  v-for="(interval, idx) in localAvailability[day]"
                  :key="idx"
                  class="flex items-center gap-4"
                >
                  <div class="flex-1 grid grid-cols-2 gap-3">
                    <div class="flex items-center gap-2">
                      <span class="text-[10px] font-black text-gray-400 uppercase">From</span>
                      <input
                        type="time"
                        v-model="interval.start"
                        class="block w-full px-3 py-2 border border-gray-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white text-xs focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/10 outline-none"
                      />
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-[10px] font-black text-gray-400 uppercase">To</span>
                      <input
                        type="time"
                        v-model="interval.end"
                        class="block w-full px-3 py-2 border border-gray-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white text-xs focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/10 outline-none"
                      />
                    </div>
                  </div>
                  <button
                    type="button"
                    @click="removeInterval(day, idx)"
                    class="p-2.5 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20 rounded-xl transition-all border border-transparent hover:border-rose-100 dark:hover:border-rose-950/30"
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
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>

                <button
                  type="button"
                  @click="addInterval(day)"
                  class="inline-flex items-center gap-1.5 px-3.5 py-2 text-[10px] font-black uppercase tracking-widest text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 border border-dashed border-emerald-200 dark:border-emerald-800/40 rounded-xl transition-all"
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
                      stroke-width="3"
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Add Time Slot
                </button>
              </div>
            </div>
          </div>

          <div class="mt-8 flex justify-end">
            <button
              type="button"
              @click="saveAvailability"
              :disabled="isSavingAvailability"
              class="px-6 py-3.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 shadow-lg shadow-emerald-600/25 flex items-center gap-2 active:scale-95"
            >
              <div
                v-if="isSavingAvailability"
                class="animate-spin rounded-full h-4 w-4 border-[2px] border-white border-t-transparent"
              ></div>
              {{ isSavingAvailability ? 'Saving Availability...' : 'Save Availability' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty / Error State -->
    <div
      v-else
      class="flex flex-col items-center justify-center py-24 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border-2 border-dashed border-gray-100 dark:border-slate-800"
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
      <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">Profile not found</h4>
      <p class="text-gray-500 dark:text-slate-400 text-sm font-medium max-w-xs text-center">
        We couldn't load your profile data. Please try refreshing the page.
      </p>
      <button
        @click="loadProfile"
        class="mt-6 px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-emerald-700 transition-all"
      >
        Retry
      </button>
    </div>

    <!-- Edit Profile Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="showEditModal"
          class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
          @click.self="closeEditModal"
        >
          <Transition name="slide-up">
            <div
              v-if="showEditModal"
              class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-10 shadow-premium-xl overflow-y-auto max-h-[90vh]"
            >
              <!-- Modal Header -->
              <div class="flex items-center justify-between mb-8">
                <div>
                  <h2 class="text-2xl font-black text-gray-900 dark:text-white">Edit Profile</h2>
                  <p class="text-sm text-gray-500 dark:text-slate-400 font-medium mt-0.5">
                    Update your availability and professional details.
                  </p>
                </div>
                <button
                  @click="closeEditModal"
                  class="w-10 h-10 flex items-center justify-center rounded-2xl bg-gray-100 dark:bg-slate-800 text-gray-500 dark:text-slate-400 hover:bg-gray-200 dark:hover:bg-slate-700 transition-all"
                  aria-label="Close modal"
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

              <form @submit.prevent="saveProfile" class="space-y-6">
                <!-- Specialization -->
                <FormField
                  id="specialization"
                  label="Specialization"
                  placeholder="e.g. Cardiologist"
                  :model-value="editForm.specialization"
                  :error="formErrors.specialization"
                  @update:model-value="editForm.specialization = $event"
                  required
                />

                <!-- Consultation Fee -->
                <FormField
                  id="consultation_fee"
                  label="Consultation Fee (USD)"
                  type="number"
                  placeholder="e.g. 150"
                  :model-value="editForm.consultation_fee"
                  :error="formErrors.consultation_fee"
                  @update:model-value="editForm.consultation_fee = Number($event)"
                  required
                />

                <!-- Shift Select -->
                <div class="w-full space-y-1.5">
                  <label
                    for="shift"
                    class="block text-sm font-bold text-gray-600 dark:text-slate-400"
                    :class="formErrors.shift ? 'text-red-500' : ''"
                  >
                    Shift <span class="text-red-500 ml-0.5">*</span>
                  </label>
                  <select
                    id="shift"
                    v-model="editForm.shift"
                    class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
                    :class="formErrors.shift ? 'border-red-500 focus:ring-red-500/10' : ''"
                  >
                    <option value="" disabled>Select a shift</option>
                    <option value="Day">Day</option>
                    <option value="Night">Night</option>
                    <option value="Rotating">Rotating</option>
                  </select>
                  <div class="min-h-[1.25rem] px-1">
                    <p
                      v-if="formErrors.shift"
                      class="text-xs font-medium text-red-500 flex items-center gap-1"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-3 w-3"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        stroke-width="2.5"
                      >
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="12" />
                        <line x1="12" y1="16" x2="12.01" y2="16" />
                      </svg>
                      {{ formErrors.shift }}
                    </p>
                  </div>
                </div>

                <!-- Experience Years -->
                <FormField
                  id="experience_years"
                  label="Experience Years"
                  type="number"
                  placeholder="e.g. 10"
                  :model-value="editForm.experience_years"
                  :error="formErrors.experience_years"
                  @update:model-value="editForm.experience_years = Number($event)"
                />

                <!-- Is Available Toggle -->
                <div
                  class="flex items-center justify-between p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50"
                >
                  <div>
                    <p class="text-sm font-bold text-gray-900 dark:text-white">
                      Availability Status
                    </p>
                    <p class="text-xs text-gray-500 dark:text-slate-400 font-medium mt-0.5">
                      Mark yourself as available for consultations
                    </p>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="editForm.is_available"
                    @click="editForm.is_available = !editForm.is_available"
                    :class="[
                      'relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-4 focus:ring-emerald-500/20',
                      editForm.is_available ? 'bg-emerald-600' : 'bg-gray-200 dark:bg-slate-700',
                    ]"
                  >
                    <span
                      :class="[
                        'pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out',
                        editForm.is_available ? 'translate-x-5' : 'translate-x-0',
                      ]"
                    ></span>
                  </button>
                </div>

                <!-- Action Buttons -->
                <div class="flex items-center gap-4 pt-2">
                  <button
                    type="button"
                    @click="closeEditModal"
                    class="flex-1 py-3.5 rounded-2xl border border-gray-200 dark:border-slate-700 text-gray-700 dark:text-slate-300 text-[10px] font-black uppercase tracking-widest hover:bg-gray-50 dark:hover:bg-slate-800 transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    :disabled="isSaving"
                    class="flex-1 py-3.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 active:scale-95"
                  >
                    <div
                      v-if="isSaving"
                      class="animate-spin rounded-full h-4 w-4 border-[2px] border-white border-t-transparent"
                    ></div>
                    {{ isSaving ? 'Saving...' : 'Save Changes' }}
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
