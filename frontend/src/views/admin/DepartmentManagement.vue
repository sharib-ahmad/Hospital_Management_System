<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import DepartmentForm from '../../components/DepartmentForm.vue'
import DepartmentList from '../../components/DepartmentList.vue'
import api from '../../utils/axios'

interface Department {
  id?: string
  name: string
  description?: string
}

const isFormOpen = ref(false)
const isEditing = ref(false)
const selectedDepartment = ref<Department | null>(null)
const refreshKey = ref(0)

const stats = ref({
  departments: 0,
  doctors: 0,
  staff: 0,
})

const loadStats = async () => {
  try {
    const [deptRes, docRes, nurseRes] = await Promise.all([
      api.get('/departments'),
      api.get('/doctors'),
      api.get('/nurses'),
    ])
    stats.value = {
      departments: deptRes.data.data?.length || 0,
      doctors: docRes.data.data?.length || 0,
      staff: nurseRes.data.data?.length || 0,
    }
  } catch (error) {
    console.error('Failed to load stats', error)
  }
}

onMounted(loadStats)

const openCreateForm = () => {
  isEditing.value = false
  selectedDepartment.value = null
  isFormOpen.value = true
}

const openEditForm = (dept: Department) => {
  isEditing.value = true
  selectedDepartment.value = dept
  isFormOpen.value = true
}

const closeForm = () => {
  isFormOpen.value = false
  isEditing.value = false
  selectedDepartment.value = null
}

const handleRefresh = () => {
  refreshKey.value += 1
  loadStats()
  closeForm()
}
</script>

<template>
  <DashboardLayout>
    <!-- Header -->
    <div class="mb-12 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">
          Department Management
        </h1>
        <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
          Create, manage, and organize hospital departments and resource limits.
        </p>
      </div>
      <button
        @click="openCreateForm"
        class="px-8 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/20 hover:-translate-y-1 transition-all active:scale-95 uppercase tracking-widest text-xs flex items-center justify-center gap-3"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="3"
        >
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        New Department
      </button>
    </div>

    <!-- Info Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
      <div
        class="glass p-8 rounded-[2rem] border border-white/40 dark:border-white/5 shadow-premium group"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1">Total Departments</p>
            <p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter">
              {{ stats.departments }}
            </p>
          </div>
          <div
            class="w-14 h-14 bg-emerald-50 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center text-emerald-600 shadow-sm group-hover:rotate-6 transition-transform"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-7 w-7"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          </div>
        </div>
      </div>

      <div
        class="glass p-8 rounded-[2rem] border border-white/40 dark:border-white/5 shadow-premium group"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1">Active Doctors</p>
            <p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter">{{ stats.doctors }}</p>
          </div>
          <div
            class="w-14 h-14 bg-teal-50 dark:bg-teal-900/30 rounded-2xl flex items-center justify-center text-teal-600 shadow-sm group-hover:rotate-6 transition-transform"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-7 w-7"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
        </div>
      </div>

      <div
        class="glass p-8 rounded-[2rem] border border-white/40 dark:border-white/5 shadow-premium group"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1">Staff Members</p>
            <p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter">{{ stats.staff }}</p>
          </div>
          <div
            class="w-14 h-14 bg-emerald-50 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center text-emerald-600 shadow-sm group-hover:rotate-6 transition-transform"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-7 w-7"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div
      class="glass rounded-[2.5rem] border border-white/40 dark:border-white/5 p-10 shadow-premium"
    >
      <div class="mb-10 flex items-center justify-between">
        <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
          <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
          Hospital Departments
        </h3>
      </div>

      <!-- Department List Component -->
      <DepartmentList :key="refreshKey" editable @edit="openEditForm" @delete="handleRefresh" />
    </div>

    <!-- Department Form Modal -->
    <DepartmentForm
      :is-open="isFormOpen"
      :department="selectedDepartment"
      :is-editing="isEditing"
      @close="closeForm"
      @refresh="handleRefresh"
    />
  </DashboardLayout>
</template>
