<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useNotificationStore } from '../stores/notification'
import api from '../utils/axios'

interface Department {
  id: string
  name: string
  description?: string
  created_at?: string
  updated_at?: string
  staff?: {
    doctors: number
    nurses: number
  }
}

interface Props {
  editable?: boolean
}

withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  edit: [dept: Department]
  delete: [id: string]
}>()

const notification = useNotificationStore()

const departments = ref<Department[]>([])
const isLoading = ref(false)
const searchQuery = ref('')
const selectedDept = ref<string | null>(null)

const filteredDepartments = computed(() => {
  if (!searchQuery.value) return departments.value
  return departments.value.filter(
    (dept) =>
      dept.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      dept.id.toLowerCase().includes(searchQuery.value.toLowerCase()),
  )
})

const loadDepartments = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/departments')
    departments.value = response.data.data || []
    console.log('Loaded departments:', departments.value)
  } catch (error) {
    notification.error('Failed to load departments')
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const handleEdit = (dept: Department) => {
  emit('edit', dept)
}

const handleDelete = async (deptId: string) => {
  if (!confirm('Are you sure you want to delete this department?')) return

  try {
    await api.delete(`/departments/${deptId}`)
    notification.success('Department deleted successfully')
    await loadDepartments()
    emit('delete', deptId)
  } catch (error: any) {
    const message = error.response?.data?.message || 'Failed to delete department'
    notification.error(message)
  }
}

const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(() => {
  loadDepartments()
})
</script>

<template>
  <div class="space-y-4">
    <!-- Search Bar -->
    <div class="flex gap-2">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search departments by name or ID..."
        class="flex-1 px-4 py-2.5 border rounded-xl text-sm outline-none bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 border-gray-300 dark:border-slate-600 focus:border-emerald-500 dark:focus:border-emerald-400"
      />
      <button
        @click="loadDepartments"
        :disabled="isLoading"
        class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl transition-colors disabled:opacity-50 text-sm font-medium"
      >
        <svg
          v-if="isLoading"
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4 inline animate-spin"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        />
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4 inline"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="23 4 23 10 17 10" />
          <polyline points="1 20 1 14 7 14" />
          <path d="M3.51 9a9 9 0 0114.85-3.36 10 10 0 0110.46 10.16" />
          <path d="M20.49 15a9 9 0 01-14.85 3.36 10 10 0 01-10.46-10.16" />
        </svg>
      </button>
    </div>

    <!-- Departments List -->
    <div
      v-if="isLoading && departments.length === 0"
      class="flex items-center justify-center py-12"
    >
      <div class="text-center">
        <div class="animate-spin inline-block">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-8 w-8 text-emerald-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" />
          </svg>
        </div>
        <p class="mt-2 text-sm text-gray-500 dark:text-slate-400">Loading departments...</p>
      </div>
    </div>

    <div
      v-else-if="filteredDepartments.length === 0"
      class="flex items-center justify-center py-12"
    >
      <div class="text-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-12 w-12 mx-auto text-gray-300 dark:text-slate-600 mb-3"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
        <p class="text-gray-500 dark:text-slate-400 text-sm">
          {{ searchQuery ? 'No departments match your search.' : 'No departments found.' }}
        </p>
      </div>
    </div>

    <div v-else class="grid gap-3">
      <div
        v-for="dept in filteredDepartments"
        :key="dept.id"
        @click="selectedDept = selectedDept === dept.id ? null : dept.id"
        class="bg-white/70 dark:bg-slate-800/70 glass rounded-xl border border-gray-200 dark:border-slate-700 hover:border-emerald-300 dark:hover:border-emerald-600 transition-all cursor-pointer"
      >
        <!-- Collapsed View -->
        <div class="p-4">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5 text-white"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                  </svg>
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ dept.name }}</h3>
                  <p class="text-xs text-gray-500 dark:text-slate-400">{{ dept.id }}</p>
                </div>
              </div>
            </div>

            <!-- Expand Icon -->
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 text-gray-400 dark:text-slate-500 transition-transform"
              :class="{ 'rotate-180': selectedDept === dept.id }"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </div>

        <!-- Expanded View -->
        <Transition name="expand">
          <div
            v-show="selectedDept === dept.id"
            class="border-t border-gray-200 dark:border-slate-700 px-4 py-4 space-y-3 bg-gray-50 dark:bg-slate-700/50"
          >
            <!-- Description -->
            <div>
              <p class="text-xs font-medium text-gray-500 dark:text-slate-400 mb-1">Description</p>
              <p class="text-sm text-gray-700 dark:text-slate-300">
                {{ dept.description || 'No description provided' }}
              </p>
            </div>

            <!-- Metadata -->
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-xs font-medium text-gray-500 dark:text-slate-400">Doctors</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ dept.staff?.doctors || 0 }}
                </p>
              </div>
              <div>
                <p class="text-xs font-medium text-gray-500 dark:text-slate-400">Nurses</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ dept.staff?.nurses || 0 }}
                </p>
              </div>
            </div>

            <!-- Timestamps -->
            <div
              class="text-xs text-gray-500 dark:text-slate-400 space-y-1 pt-2 border-t border-gray-200 dark:border-slate-600"
            >
              <p>Created: {{ formatDate(dept.created_at) }}</p>
              <p>Updated: {{ formatDate(dept.updated_at) }}</p>
            </div>

            <!-- Actions -->
            <div v-if="editable" class="flex gap-2 pt-2">
              <button
                @click.stop="handleEdit(dept)"
                class="flex-1 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4 inline mr-1"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
                Edit
              </button>
              <button
                @click.stop="handleDelete(dept.id)"
                class="flex-1 px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4 inline mr-1"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <polyline points="3 6 5 6 21 6" />
                  <path
                    d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                  />
                </svg>
                Delete
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition:
    max-height 0.3s ease,
    opacity 0.2s ease;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
