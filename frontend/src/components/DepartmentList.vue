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
    <div class="flex gap-4 mb-8">
      <div class="relative flex-1 group">
        <div class="absolute inset-y-0 left-4 flex items-center pointer-events-none text-gray-400 group-focus-within:text-emerald-500 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search departments by name or ID..."
          class="w-full pl-12 pr-4 py-4 bg-gray-50 dark:bg-slate-800/50 border border-gray-100 dark:border-slate-700 rounded-2xl text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500/50 transition-all text-gray-900 dark:text-white"
        />
      </div>
      <button
        @click="loadDepartments"
        :disabled="isLoading"
        class="px-6 py-4 bg-white dark:bg-slate-800 border border-gray-100 dark:border-slate-700 text-gray-600 dark:text-slate-400 rounded-2xl hover:text-emerald-600 dark:hover:text-emerald-400 hover:border-emerald-500/30 transition-all disabled:opacity-50 shadow-sm flex items-center justify-center"
      >
        <svg
          v-if="isLoading"
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5 animate-spin"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        />
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36 10 10 0 0110.46 10.16M20.49 15a9 9 0 01-14.85 3.36 10 10 0 01-10.46-10.16" />
        </svg>
      </button>
    </div>

    <!-- Departments List -->
    <div
      v-if="isLoading && departments.length === 0"
      class="flex flex-col items-center justify-center py-20"
    >
      <div class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent mb-4"></div>
      <p class="text-sm font-black text-gray-400 uppercase tracking-widest">Fetching Departments...</p>
    </div>

    <div
      v-else-if="filteredDepartments.length === 0"
      class="flex flex-col items-center justify-center py-20 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border-2 border-dashed border-gray-100 dark:border-slate-800"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-12 w-12 text-gray-300 dark:text-slate-700 mb-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      <p class="text-gray-500 dark:text-slate-400 font-bold tracking-tight">
        {{ searchQuery ? 'No matches for your search' : 'No departments configured yet' }}
      </p>
    </div>

    <div v-else class="grid gap-4">
      <div
        v-for="dept in filteredDepartments"
        :key="dept.id"
        @click="selectedDept = selectedDept === dept.id ? null : dept.id"
        class="glass rounded-[2rem] border border-white/40 dark:border-white/5 hover:border-emerald-500/30 transition-all cursor-pointer shadow-premium overflow-hidden group"
      >
        <!-- Collapsed View -->
        <div class="p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-5">
              <div
                class="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:scale-110 transition-transform"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-6 w-6 text-white"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-black text-gray-900 dark:text-white tracking-tight">{{ dept.name }}</h3>
                <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest">{{ dept.id }}</p>
              </div>
            </div>

            <!-- Expand Icon -->
            <div 
              class="w-8 h-8 rounded-full flex items-center justify-center transition-colors"
              :class="selectedDept === dept.id ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30' : 'text-gray-400'"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 transition-transform duration-300"
                :class="{ 'rotate-180': selectedDept === dept.id }"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="3"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Expanded View -->
        <Transition name="expand">
          <div
            v-show="selectedDept === dept.id"
            class="border-t border-gray-100 dark:border-slate-800 p-8 space-y-6 bg-gray-50/30 dark:bg-slate-900/30"
          >
            <!-- Description -->
            <div>
              <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-2">Detailed Description</p>
              <p class="text-sm text-gray-600 dark:text-slate-300 leading-relaxed font-medium">
                {{ dept.description || 'No specialized description provided for this department.' }}
              </p>
            </div>

            <!-- Metadata -->
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 rounded-2xl bg-white dark:bg-slate-800 border border-gray-100 dark:border-slate-700/50 shadow-sm">
                <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1">Doctors</p>
                <p class="text-2xl font-black text-gray-900 dark:text-white tracking-tighter">
                  {{ dept.staff?.doctors || 0 }}
                </p>
              </div>
              <div class="p-4 rounded-2xl bg-white dark:bg-slate-800 border border-gray-100 dark:border-slate-700/50 shadow-sm">
                <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1">Nurses</p>
                <p class="text-2xl font-black text-gray-900 dark:text-white tracking-tighter">
                  {{ dept.staff?.nurses || 0 }}
                </p>
              </div>
            </div>

            <!-- Timestamps -->
            <div class="flex items-center justify-between text-[10px] font-black text-gray-400 uppercase tracking-widest pt-4 border-t border-gray-100 dark:border-slate-800">
              <p>Created: <span class="text-gray-600 dark:text-slate-400 ml-1">{{ formatDate(dept.created_at) }}</span></p>
              <p>Last Sync: <span class="text-gray-600 dark:text-slate-400 ml-1">{{ formatDate(dept.updated_at) }}</span></p>
            </div>

            <!-- Actions -->
            <div v-if="editable" class="flex gap-4 pt-2">
              <button
                @click.stop="handleEdit(dept)"
                class="flex-1 px-4 py-3 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Modify
              </button>
              <button
                @click.stop="handleDelete(dept.id)"
                class="flex-1 px-4 py-3 bg-red-50 text-red-600 text-xs font-black uppercase tracking-widest rounded-xl hover:bg-red-600 hover:text-white transition-all border border-red-100 dark:border-red-900/30 flex items-center justify-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
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
