<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import FormField from './FormField.vue'
import { useNotificationStore } from '../stores/notification'
import api from '../utils/axios'

interface Props {
  role: 'patient' | 'doctor' | 'nurse' | 'pharmacist'
}

const props = defineProps<Props>()
const emit = defineEmits(['success'])

const notification = useNotificationStore()
const isLoading = ref(false)
const departments = ref<{ id: string; name: string }[]>([])

const form = ref({
  reason: '',
  date_of_birth: '',
  gender: 'male',
  blood_group: 'O+',
  emergency_contact_number: '',
  // Role specific
  medical_history: '',
  full_name: '',
  relation: 'Self',
  email: '',
  phone_number: '',
  address: '',
  pincode: '',
  specialization: '',
  experience_years: 0,
  consultation_fee: 0,
  license_number: '',
  department_id: '',
  shift: 'Day',
})

const errors = ref<Record<string, string>>({})

const loadDepartments = async () => {
  try {
    const response = await api.get('/departments')
    departments.value = response.data.data || []
  } catch (error) {
    console.error('Failed to load departments', error)
  }
}

onMounted(() => {
  if (props.role === 'doctor' || props.role === 'nurse') {
    loadDepartments()
  }
})

const validate = () => {
  const newErrors: Record<string, string> = {}
  if (form.value.reason.length < 5) newErrors.reason = 'Reason must be at least 5 characters'
  if (!form.value.date_of_birth) newErrors.date_of_birth = 'Date of birth is required'

  if (props.role === 'doctor' || props.role === 'nurse' || props.role === 'pharmacist') {
    if (!form.value.license_number) newErrors.license_number = 'License number is required'
    if (form.value.license_number.length < 12)
      newErrors.license_number = 'License number must be at least 12 characters'
  }

  if (props.role === 'doctor' || props.role === 'nurse') {
    if (!form.value.department_id) newErrors.department_id = 'Department is required'
  }

  if (props.role === 'doctor') {
    if (!form.value.specialization) newErrors.specialization = 'Specialization is required'
  }

  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

const handleSubmit = async () => {
  if (!validate()) return

  isLoading.value = true
  try {
    const basePayload = {
      reason: form.value.reason,
      date_of_birth: form.value.date_of_birth,
      gender: form.value.gender,
      blood_group: form.value.blood_group,
      emergency_contact_number: form.value.emergency_contact_number,
    }

    let payload = {}
    if (props.role === 'patient') {
      payload = {
        ...basePayload,
        medical_history: form.value.medical_history,
        full_name: form.value.full_name || null,
        relation: form.value.relation,
        email: form.value.email || null,

        phone_number: form.value.phone_number || null,
        address: form.value.address || null,
        pincode: form.value.pincode || null,
      }
    } else if (props.role === 'doctor') {
      payload = {
        ...basePayload,
        specialization: form.value.specialization,
        experience_years: form.value.experience_years,
        consultation_fee: form.value.consultation_fee,
        license_number: form.value.license_number,
        department_id: form.value.department_id,
        shift: form.value.shift,
      }
    } else if (props.role === 'nurse') {
      payload = {
        ...basePayload,
        experience_years: form.value.experience_years,
        license_number: form.value.license_number,
        department_id: form.value.department_id,
        shift: form.value.shift,
      }
    } else if (props.role === 'pharmacist') {
      payload = {
        ...basePayload,
        experience_years: form.value.experience_years,
        license_number: form.value.license_number,
        shift: form.value.shift,
      }
    }

    await api.post(`/applications/${props.role}`, payload)
    notification.success(`Application for ${props.role} submitted successfully!`)
    emit('success')
  } catch (error: any) {
    notification.error(error.response?.data?.message || 'Failed to submit application')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Common Fields -->
      <FormField
        id="dob"
        v-model="form.date_of_birth"
        type="date"
        label="Date of Birth"
        :error="errors.date_of_birth"
        required
      />

      <div class="space-y-1.5">
        <label class="block text-sm font-semibold text-gray-700 dark:text-slate-300">Gender</label>
        <select
          v-model="form.gender"
          class="block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-gray-900 dark:text-white sm:text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 transition-all"
        >
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="space-y-1.5">
        <label class="block text-sm font-semibold text-gray-700 dark:text-slate-300"
          >Blood Group</label
        >
        <select
          v-model="form.blood_group"
          class="block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-gray-900 dark:text-white sm:text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 transition-all"
        >
          <option
            v-for="bg in ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']"
            :key="bg"
            :value="bg"
          >
            {{ bg }}
          </option>
        </select>
      </div>

      <FormField
        id="emergency_contact"
        v-model="form.emergency_contact_number"
        label="Emergency Contact (Optional)"
        placeholder="+1 (555) 000-0000"
        :error="errors.emergency_contact_number"
      />
    </div>

    <!-- Role Specific Fields -->
    <div v-if="role === 'patient'" class="space-y-6">
      <div
        class="p-6 bg-emerald-50/50 dark:bg-emerald-900/10 rounded-2xl border border-emerald-100 dark:border-emerald-800/30"
      >
        <h3 class="text-lg font-black text-emerald-900 dark:text-emerald-400 mb-4 tracking-tight">
          Patient Identity (Optional)
        </h3>
        <p
          class="text-xs text-emerald-700/60 dark:text-emerald-500/60 mb-6 font-medium uppercase tracking-widest"
        >
          Leave blank to use your own account details
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            id="p_name"
            v-model="form.full_name"
            label="Full Name"
            placeholder="Patient's legal name"
          />
          <div class="space-y-1.5">
            <label class="block text-sm font-semibold text-gray-700 dark:text-slate-300"
              >Relation</label
            >
            <select
              v-model="form.relation"
              class="block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-gray-900 dark:text-white sm:text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 transition-all"
            >
              <option
                v-for="rel in [
                  'Self',
                  'Father',
                  'Mother',
                  'Spouse',
                  'Son',
                  'Daughter',
                  'Brother',
                  'Sister',
                  'Other',
                ]"
                :key="rel"
                :value="rel"
              >
                {{ rel }}
              </option>
            </select>
          </div>
          <FormField
            id="p_email"
            v-model="form.email"
            type="email"
            label="Email Address"
            placeholder="patient@example.com"
          />
          <FormField
            id="p_phone"
            v-model="form.phone_number"
            label="Phone Number"
            placeholder="+1 (555) 000-0000"
          />
          <FormField id="p_pincode" v-model="form.pincode" label="Pincode" placeholder="123456" />
          <div class="md:col-span-2">
            <FormField
              id="p_address"
              v-model="form.address"
              label="Home Address"
              placeholder="Complete street address"
            />
          </div>
        </div>
      </div>

      <div class="space-y-1.5">
        <label class="block text-sm font-semibold text-gray-700 dark:text-slate-300"
          >Medical History</label
        >
        <textarea
          v-model="form.medical_history"
          rows="4"
          placeholder="List any past illnesses, surgeries, or chronic conditions..."
          class="block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-gray-900 dark:text-white sm:text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 transition-all"
        ></textarea>
      </div>
    </div>

    <div
      v-if="role === 'doctor' || role === 'nurse' || role === 'pharmacist'"
      class="grid grid-cols-1 md:grid-cols-2 gap-6"
    >
      <FormField
        id="license"
        v-model="form.license_number"
        label="License Number"
        placeholder="ABC123456789"
        :error="errors.license_number"
        required
      />

      <div v-if="role === 'doctor' || role === 'nurse'" class="space-y-1.5">
        <label class="block text-sm font-semibold text-gray-700 dark:text-slate-300"
          >Department</label
        >
        <select
          v-model="form.department_id"
          class="block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-gray-900 dark:text-white sm:text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 transition-all"
          required
        >
          <option value="" disabled>Select Department</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">
            {{ dept.name }}
          </option>
        </select>
        <p v-if="errors.department_id" class="text-xs text-red-500">{{ errors.department_id }}</p>
      </div>

      <FormField
        id="experience"
        v-model="form.experience_years"
        type="number"
        label="Experience (Years)"
        required
      />

      <div class="space-y-1.5">
        <label class="block text-sm font-semibold text-gray-700 dark:text-slate-300"
          >Preferred Shift</label
        >
        <select
          v-model="form.shift"
          class="block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-gray-900 dark:text-white sm:text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 transition-all"
        >
          <option value="Day">Day</option>
          <option value="Night">Night</option>
          <option value="Rotating">Rotating</option>
        </select>
      </div>
    </div>

    <div v-if="role === 'doctor'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <FormField
        id="specialization"
        v-model="form.specialization"
        label="Specialization"
        placeholder="e.g. Cardiology"
        :error="errors.specialization"
        required
      />
      <FormField
        id="fee"
        v-model="form.consultation_fee"
        type="number"
        label="Consultation Fee"
        required
      />
    </div>

    <FormField
      id="reason"
      v-model="form.reason"
      label="Why are you applying?"
      placeholder="Briefly explain your motivation..."
      :error="errors.reason"
      required
    />

    <button
      type="submit"
      :disabled="isLoading"
      class="w-full flex justify-center py-4 px-4 border border-transparent rounded-xl shadow-lg text-lg font-bold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all active:scale-95 disabled:opacity-70"
    >
      <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" viewBox="0 0 24 24">
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      {{ isLoading ? 'Submitting Application...' : 'Submit Application' }}
    </button>
  </form>
</template>
