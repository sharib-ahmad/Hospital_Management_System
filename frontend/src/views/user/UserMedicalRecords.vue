<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()

const medicalRecords = ref<any[]>([])
const isLoading = ref(true)

const loadRecords = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/medical-records/my')
    medicalRecords.value = res.data.data || res.data || []
  } catch (error) {
    notification.error('Failed to load medical records')
  } finally {
    isLoading.value = false
  }
}

const normalizeDate = (dateString: string | null | undefined): string => {
  return dateString || ''
}

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return '—'
  const date = new Date(normalizeDate(dateString))
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(loadRecords)
</script>

<template>
  <DashboardLayout>
    <!-- Page Header -->
    <div class="mb-12">
      <div class="flex items-center gap-3 mb-2">
        <span
          class="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest border border-emerald-100 dark:border-emerald-500/20"
        >
          User Portal
        </span>
      </div>
      <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">
        Medical Records
      </h1>
      <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
        Access your official diagnostic reports, prescriptions, and clinical summaries.
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-32">
      <div
        class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
      ></div>
    </div>

    <!-- Empty State -->
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
      <h3 class="text-xl font-black text-gray-900 dark:text-white mb-2">No medical records</h3>
      <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium">
        Medical records will be generated here by your consulting physician after appointment
        completion.
      </p>
    </div>

    <!-- Records List -->
    <div
      v-else
      class="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500"
    >
      <div
        v-for="record in medicalRecords"
        :key="record.id"
        class="bg-white dark:bg-slate-900 p-8 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 shadow-premium hover:-translate-y-0.5 transition-all duration-300"
      >
        <!-- Header Row -->
        <div
          class="flex items-start justify-between flex-wrap gap-4 mb-6 pb-4 border-b border-gray-50 dark:border-slate-800"
        >
          <div>
            <span
              class="text-[9px] font-black text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1 rounded-full uppercase tracking-widest border border-indigo-100 dark:border-indigo-500/20"
            >
              Medical Report
            </span>
            <h4 class="text-xl font-black text-gray-900 dark:text-white mt-3 tracking-tight">
              {{ record.diagnosis || 'General Consultation' }}
            </h4>
            <p
              class="text-[9px] text-gray-400 dark:text-slate-500 font-black uppercase tracking-widest mt-1.5"
            >
              Patient Profile: {{ record.patient_name || 'My Patient Profile' }}
            </p>
          </div>
          <div class="text-right">
            <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">
              Record Date
            </p>
            <p class="text-xs font-bold text-gray-700 dark:text-slate-300 uppercase tracking-wider">
              {{ formatDate(record.created_at || record.record_date) }}
            </p>
          </div>
        </div>

        <!-- Details Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Diagnosis -->
          <div
            class="p-5 bg-emerald-50/30 dark:bg-emerald-950/10 rounded-2xl border border-emerald-100/50 dark:border-emerald-500/10"
          >
            <p
              class="text-[9px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest mb-2"
            >
              Diagnosis
            </p>
            <p class="text-xs text-gray-700 dark:text-slate-300 font-medium leading-relaxed">
              {{ record.diagnosis || '—' }}
            </p>
          </div>

          <!-- Treatment -->
          <div
            class="p-5 bg-teal-50/30 dark:bg-teal-950/10 rounded-2xl border border-teal-100/50 dark:border-teal-500/10"
          >
            <p
              class="text-[9px] font-black text-teal-600 dark:text-teal-400 uppercase tracking-widest mb-2"
            >
              Treatment
            </p>
            <p class="text-xs text-gray-700 dark:text-slate-300 font-medium leading-relaxed">
              {{ record.treatment || '—' }}
            </p>
          </div>

          <!-- Prescription (if any) -->
          <div
            v-if="record.prescription"
            class="p-5 bg-indigo-50/30 dark:bg-indigo-950/10 rounded-2xl border border-indigo-100/50 dark:border-indigo-500/10 sm:col-span-2"
          >
            <p
              class="text-[9px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest mb-2"
            >
              Prescription Items & Dosage
            </p>
            <p
              class="text-xs text-gray-700 dark:text-slate-300 font-medium leading-relaxed font-mono whitespace-pre-line"
            >
              {{ record.prescription }}
            </p>
          </div>

          <!-- Notes (if any) -->
          <div
            v-if="record.notes"
            class="p-5 bg-amber-50/30 dark:bg-amber-950/10 rounded-2xl border border-amber-100/50 dark:border-amber-500/10 sm:col-span-2"
          >
            <p
              class="text-[9px] font-black text-amber-600 dark:text-amber-400 uppercase tracking-widest mb-2"
            >
              Clinical Notes
            </p>
            <p class="text-xs text-gray-700 dark:text-slate-300 font-medium leading-relaxed italic">
              "{{ record.notes }}"
            </p>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<style scoped>
/* Scoped modal and general styling transitions are handled by tailwind classes */
</style>
