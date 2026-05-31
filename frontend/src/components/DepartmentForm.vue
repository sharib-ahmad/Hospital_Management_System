<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import FormField from './FormField.vue'
import { useNotificationStore } from '../stores/notification'
import api from '../utils/axios'

interface Department {
  id?: string
  name: string
  description?: string
  doctor_limit?: number
  nurse_limit?: number
}

interface Props {
  isOpen: boolean
  department?: Department | null
  isEditing?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isEditing: false,
  department: null,
})

const emit = defineEmits<{
  close: []
  refresh: []
}>()

const notification = useNotificationStore()

// Form state
const form = ref({
  id: '',
  name: '',
  description: '',
  doctor_limit: 3,
  nurse_limit: 5,
})

const errors = ref<Record<string, string>>({})
const isLoading = ref(false)
const descriptionLength = ref(0)

// Watch description to update length live
watch(
  () => form.value.description,
  (newVal) => {
    descriptionLength.value = newVal?.length || 0
  },
  { immediate: true },
)

const isFormValid = computed(() => {
  return (
    form.value.id.trim().length >= 6 &&
    form.value.name.trim().length >= 2 &&
    form.value.doctor_limit >= 0 &&
    form.value.nurse_limit >= 0
  )
})

// Initialize form with department data
watch(
  () => props.department,
  (newDept) => {
    if (newDept) {
      form.value = {
        id: newDept.id || '',
        name: newDept.name,
        description: newDept.description || '',
        doctor_limit: newDept.doctor_limit ?? 3,
        nurse_limit: newDept.nurse_limit ?? 5,
      }
    } else {
      resetForm()
    }
    errors.value = {}
  },
)

watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal) {
      document.body.classList.add('overflow-hidden')
    } else {
      document.body.classList.remove('overflow-hidden')
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  document.body.classList.remove('overflow-hidden')
})

const resetForm = () => {
  form.value = {
    id: '',
    name: '',
    description: '',
    doctor_limit: 3,
    nurse_limit: 5,
  }
  errors.value = {}
}

const validateForm = (): boolean => {
  const newErrors: Record<string, string> = {}

  if (!form.value.id.trim()) {
    newErrors.id = 'Department ID is required'
  } else if (form.value.id.length < 6) {
    newErrors.id = 'Department ID must be at least 6 characters'
  } else if (form.value.id.length > 12) {
    newErrors.id = 'Department ID cannot exceed 12 characters'
  }

  if (!form.value.name.trim()) {
    newErrors.name = 'Department name is required'
  } else if (form.value.name.length < 2) {
    newErrors.name = 'Department name must be at least 2 characters'
  } else if (form.value.name.length > 100) {
    newErrors.name = 'Department name cannot exceed 100 characters'
  }

  if (form.value.description && form.value.description.length > 500) {
    newErrors.description = 'Description cannot exceed 500 characters'
  }

  if (form.value.doctor_limit < 0) {
    newErrors.doctor_limit = 'Limit cannot be negative'
  }

  if (form.value.nurse_limit < 0) {
    newErrors.nurse_limit = 'Limit cannot be negative'
  }

  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    notification.error('Please fix the form errors')
    return
  }

  isLoading.value = true

  try {
    const payload = {
      id: form.value.id,
      name: form.value.name,
      description: form.value.description || undefined,
      doctor_limit: form.value.doctor_limit,
      nurse_limit: form.value.nurse_limit,
    }

    if (props.isEditing) {
      await api.put(`/departments/${form.value.id}`, payload)
      notification.success('Department updated successfully')
    } else {
      await api.post('/departments', payload)
      notification.success('Department created successfully')
    }

    emit('refresh')
    handleClose()
  } catch (error: any) {
    const message = error.response?.data?.message || 'Failed to save department'
    notification.error(message)
  } finally {
    isLoading.value = false
  }
}

const handleClose = () => {
  resetForm()
  emit('close')
}
</script>

<template>
  <!-- Modal Backdrop -->
  <Transition name="fade">
    <div
      v-show="isOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
      @click="handleClose"
    />
  </Transition>

  <!-- Modal Dialog -->
  <Transition name="slide-up">
    <div
      v-show="isOpen"
      class="fixed inset-x-0 bottom-0 z-50 max-h-[90vh] overflow-y-auto glass rounded-t-3xl shadow-2xl md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:rounded-2xl md:w-full md:max-w-md"
      @click.stop
    >
      <div class="p-6 sm:p-8">
        <!-- Close Button -->
        <button
          @click="handleClose"
          class="absolute top-4 right-4 p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-full transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6 text-gray-500 dark:text-slate-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        <!-- Header -->
        <div class="mb-10">
          <h2 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
            {{ isEditing ? 'Modify Department' : 'New Department' }}
          </h2>
          <p
            class="text-xs text-gray-500 dark:text-slate-400 mt-2 font-black uppercase tracking-widest"
          >
            {{
              isEditing
                ? 'Syncing departmental resource limits'
                : 'Expanding hospital clinical units'
            }}
          </p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Department ID -->
          <FormField
            id="dept_id"
            label="Department ID"
            v-model="form.id"
            type="text"
            placeholder="e.g., CARD001"
            :error="errors.id"
            :disabled="isEditing"
            required
            help-text="Unique identifier (6-12 characters). Cannot be changed after creation."
          />

          <!-- Department Name -->
          <FormField
            id="dept_name"
            label="Department Name"
            v-model="form.name"
            type="text"
            placeholder="e.g., Cardiology"
            :error="errors.name"
            required
            help-text="Name of the department (2-100 characters)"
          />

          <div class="grid grid-cols-2 gap-4">
            <!-- Doctor Limit -->
            <FormField
              id="doctor_limit"
              label="Doctor Limit"
              v-model.number="form.doctor_limit"
              type="number"
              placeholder="3"
              min="0"
              :error="errors.doctor_limit"
              required
              help-text="Max doctors allowed"
            />

            <!-- Nurse Limit -->
            <FormField
              id="nurse_limit"
              label="Nurse Limit"
              v-model.number="form.nurse_limit"
              type="number"
              placeholder="5"
              min="0"
              :error="errors.nurse_limit"
              required
              help-text="Max nurses allowed"
            />
          </div>

          <!-- Description -->
          <div class="w-full space-y-1.5">
            <div class="flex justify-between items-center px-0.5">
              <label
                for="dept_description"
                class="block text-sm font-semibold text-gray-700 dark:text-slate-300"
              >
                Description
              </label>
            </div>

            <div class="relative">
              <textarea
                id="dept_description"
                v-model="form.description"
                placeholder="Enter department description..."
                rows="4"
                class="appearance-none block w-full px-4 py-3 border rounded-xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 border-gray-300 dark:border-slate-600 focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-500/10 dark:focus:ring-emerald-400/10"
              />
            </div>

            <div class="min-h-[1.25rem] px-1">
              <p
                v-if="errors.description"
                class="text-xs font-medium text-red-500 flex items-center gap-1"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-3 w-3"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                {{ errors.description }}
              </p>
              <p v-else class="text-xs text-gray-500 dark:text-slate-400 flex justify-between">
                <span>Brief description of the department</span>
                <span :class="{ 'text-red-500 font-bold': descriptionLength > 500 }">
                  {{ descriptionLength }} / 500
                </span>
              </p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-4 pt-6">
            <button
              type="button"
              @click="handleClose"
              class="flex-1 px-4 py-4 text-center text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-slate-400 bg-gray-50 dark:bg-slate-800/50 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-2xl transition-colors disabled:opacity-50"
              :disabled="isLoading"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="flex-1 px-4 py-4 text-center text-[10px] font-black uppercase tracking-widest text-white bg-emerald-600 hover:bg-emerald-700 rounded-2xl transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              :disabled="!isFormValid || isLoading"
            >
              <svg
                v-if="isLoading"
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" />
              </svg>
              {{ isLoading ? 'Syncing...' : isEditing ? 'Update Unit' : 'Create Unit' }}
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
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition:
    transform 0.3s ease,
    opacity 0.2s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

@media (min-width: 768px) {
  .slide-up-enter-from,
  .slide-up-leave-to {
    transform: translate(-50%, 20px) scale(0.95);
    opacity: 0;
  }
}
</style>
