<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import FormField from '../../components/FormField.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()

interface PharmacistProfile {
  id: string
  pharmacist_code: string
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
}

const profile = ref<PharmacistProfile | null>(null)
const isLoading = ref(true)

// Edit modal state
const showEditModal = ref(false)
const isSaving = ref(false)
const editForm = ref({
  shift: '',
  is_available: false,
  experience_years: 0,
})
const formErrors = ref({
  shift: '',
  experience_years: '',
})

const avatarLetter = computed(() => {
  return profile.value?.full_name?.charAt(0)?.toUpperCase() || 'P'
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

const loadProfile = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/pharmacists/me')
    profile.value = res.data.data ?? res.data
  } catch {
    notification.error('Failed to load profile')
  } finally {
    isLoading.value = false
  }
}

const openEditModal = () => {
  if (!profile.value) return
  editForm.value = {
    shift: profile.value.shift ?? '',
    is_available: profile.value.is_available ?? false,
    experience_years: profile.value.experience_years ?? 0,
  }
  formErrors.value = { shift: '', experience_years: '' }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const validateForm = () => {
  let valid = true
  formErrors.value = { shift: '', experience_years: '' }

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
    const res = await api.put('/pharmacists/me', {
      shift: editForm.value.shift,
      is_available: editForm.value.is_available,
      experience_years: editForm.value.experience_years,
      // Provide default fallback values for required backend model properties if user isn't changing them
      license_number: profile.value?.license_number,
      date_of_birth: profile.value?.date_of_birth,
      gender: profile.value?.gender,
      blood_group: profile.value?.blood_group,
      emergency_contact_number: profile.value?.emergency_contact_number,
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
          class="px-3 py-1 rounded-full bg-violet-50 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 text-[10px] font-black uppercase tracking-widest border border-violet-100 dark:border-violet-500/20"
        >
          Pharmacist
        </span>
      </div>
      <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">My Profile</h1>
      <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
        View and manage your personal and professional pharmacist credentials.
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
          class="w-28 h-28 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-600/30 mb-5 ring-4 ring-violet-100 dark:ring-violet-900/40"
        >
          <span class="text-4xl font-black text-white">{{ avatarLetter }}</span>
        </div>

        <!-- Full Name -->
        <h2 class="text-2xl font-black text-gray-900 dark:text-white leading-tight mb-1">
          {{ profile.full_name }}
        </h2>

        <!-- Pharmacist Code -->
        <p
          class="text-[10px] font-black text-violet-600 dark:text-violet-400 uppercase tracking-widest mb-4"
        >
          {{ profile.pharmacist_code }}
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
            {{ profile.is_available ? 'Available' : 'Unavailable' }}
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
            <span class="h-1.5 w-6 bg-violet-600 rounded-full"></span>
            Professional Details
          </h3>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">


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
              class="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50 sm:col-span-2"
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
              class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-10 shadow-premium-xl"
            >
              <!-- Modal Header -->
              <div class="flex items-center justify-between mb-8">
                <div>
                  <h2 class="text-2xl font-black text-gray-900 dark:text-white">Edit Profile</h2>
                  <p class="text-sm text-gray-500 dark:text-slate-400 font-medium mt-0.5">
                    Update your shift details and professional experience.
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
                  placeholder="e.g. 5"
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
                      Mark yourself as available for assignments
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
