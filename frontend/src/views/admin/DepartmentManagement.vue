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
    <div class="mb-8 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Department Management</h1>
        <p class="text-gray-600 dark:text-slate-400 mt-1">
          Create, manage, and organize hospital departments
        </p>
      </div>
      <button
        @click="openCreateForm"
        class="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors flex items-center gap-2 shadow-lg hover:shadow-xl"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        New Department
      </button>
    </div>

    <!-- Info Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div
        class="bg-white dark:bg-slate-800 rounded-xl border border-gray-200 dark:border-slate-700 p-6"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-slate-400">Total Departments</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">
              {{ stats.departments }}
            </p>
          </div>
          <div
            class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-blue-600"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          </div>
        </div>
      </div>

      <div
        class="bg-white dark:bg-slate-800 rounded-xl border border-gray-200 dark:border-slate-700 p-6"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-slate-400">Active Doctors</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ stats.doctors }}</p>
          </div>
          <div
            class="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-green-600"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
        </div>
      </div>

      <div
        class="bg-white dark:bg-slate-800 rounded-xl border border-gray-200 dark:border-slate-700 p-6"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-slate-400">Staff Members</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ stats.staff }}</p>
          </div>
          <div
            class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-purple-600"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
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
      class="bg-white dark:bg-slate-800 rounded-2xl border border-gray-200 dark:border-slate-700 p-6"
    >
      <div class="mb-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">All Departments</h2>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
          View and manage all hospital departments
        </p>
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
