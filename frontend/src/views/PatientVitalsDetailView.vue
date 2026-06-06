<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Chart } from 'chart.js/auto'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import api from '../utils/axios'
import { useNotificationStore } from '../stores/notification'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const notification = useNotificationStore()
const auth = useAuthStore()

const patient = ref<any>(null)
const vitals = ref<any>(null)
const vitalsHistory = ref<any[]>([])
const isLoading = ref(true)

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

const timelineCanvasRef = ref<HTMLCanvasElement | null>(null)
let timelineChartInstance: Chart | null = null

const showFullHistory = ref(false)
const selectedTimelineMetric = ref<'bp' | 'sugar' | 'cardio' | 'temp'>('bp')

const formatBloodPressureStatus = (systolic: number) => {
  if (systolic >= 140) return { label: 'High (Hypertension)', color: 'bg-rose-500 text-white' }
  if (systolic < 90) return { label: 'Low (Hypotension)', color: 'bg-amber-500 text-white' }
  return { label: 'Optimal / Normal', color: 'bg-emerald-600 text-white' }
}

const formatSugarStatus = (sugar: number) => {
  if (sugar > 140) return { label: 'High (Hyperglycemia)', color: 'bg-rose-500 text-white' }
  if (sugar < 70) return { label: 'Low (Hypoglycemia)', color: 'bg-amber-500 text-white' }
  return { label: 'Optimal / Normal', color: 'bg-emerald-600 text-white' }
}

const formatPulseStatus = (pulse: number) => {
  if (pulse > 100) return { label: 'High (Tachycardia)', color: 'bg-rose-500 text-white' }
  if (pulse < 60) return { label: 'Low (Bradycardia)', color: 'bg-amber-500 text-white' }
  return { label: 'Optimal / Normal', color: 'bg-emerald-600 text-white' }
}

const formatTempStatus = (temp: number) => {
  if (temp > 99.5) return { label: 'Fever (Hyperthermia)', color: 'bg-rose-500 text-white' }
  if (temp < 96.0) return { label: 'Low (Hypothermia)', color: 'bg-amber-500 text-white' }
  return { label: 'Normal / Optimal', color: 'bg-emerald-600 text-white' }
}

const filteredHistory = computed(() => {
  const chron = [...vitalsHistory.value].reverse()
  if (showFullHistory.value) {
    return chron
  }
  return chron.slice(-20)
})

const loadData = async () => {
  isLoading.value = true
  const patientId = route.params.id
  try {
    // 1. Load patient profile
    if (auth.user?.role === 'user') {
      const res = await api.get('/patients/my')
      const list = res.data.data || []
      patient.value = list.find((p: any) => p.id === patientId) || null
    } else {
      try {
        const res = await api.get(`/patients/${patientId}`)
        const data = res.data.data
        patient.value = Array.isArray(data) ? data[0] : data
      } catch {
        const res = await api.get('/patients/')
        const list = res.data.data || []
        patient.value = list.find((p: any) => p.id === patientId) || null
      }
    }

    if (!patient.value) {
      notification.error('Patient record not found')
      router.push('/')
      return
    }

    // 2. Load latest vitals
    try {
      const res = await api.get(`/vitals/${patientId}`)
      const data = res.data.data || res.data
      vitalsHistory.value = Array.isArray(data) ? data : (data ? [data] : [])
      vitals.value = vitalsHistory.value[0] || null
    } catch {
      vitalsHistory.value = []
      vitals.value = null
    }
  } catch (error) {
    notification.error('Failed to load patient vitals data')
  } finally {
    isLoading.value = false
    if (vitals.value) {
      setTimeout(() => {
        renderChart()
        renderTimelineChart()
      }, 50)
    }
  }
}

const renderChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  if (!canvasRef.value || !vitals.value) return

  const isDark = document.documentElement.classList.contains('dark')
  const textColor = isDark ? '#94a3b8' : '#475569'
  const gridColor = isDark ? 'rgba(71, 85, 105, 0.4)' : 'rgba(203, 213, 225, 0.9)'
  const radarBg = isDark ? 'rgba(13, 148, 136, 0.2)' : 'rgba(13, 148, 136, 0.1)'

  chartInstance = new Chart(canvasRef.value, {
    type: 'radar',
    data: {
      labels: [
        'Systolic BP',
        'Diastolic BP',
        'Blood Sugar',
        'Pulse Rate',
        'Temperature',
        'Respiration',
      ],
      datasets: [
        {
          label: 'Patient Value',
          data: [
            vitals.value.systolic_bp || 0,
            vitals.value.diastolic_bp || 0,
            vitals.value.blood_sugar || 0,
            vitals.value.pulse_rate || 0,
            vitals.value.temperature || 0,
            vitals.value.respiration_rate || 0,
          ],
          backgroundColor: radarBg,
          borderColor: '#0d9488',
          borderWidth: 3,
          pointBackgroundColor: '#0d9488',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#0d9488',
        },
        {
          label: 'Optimal Baseline',
          data: [120, 80, 100, 72, 98.6, 16],
          backgroundColor: 'rgba(99, 102, 241, 0.05)',
          borderColor: 'rgba(99, 102, 241, 0.4)',
          borderWidth: 1.5,
          borderDash: [5, 5],
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: textColor,
            font: { family: 'Outfit, sans-serif', weight: 'bold', size: 11 },
          },
        },
      },
      scales: {
        r: {
          grid: { color: gridColor },
          angleLines: { color: gridColor },
          pointLabels: {
            color: textColor,
            font: { family: 'Outfit, sans-serif', weight: 'bold', size: 10 },
          },
          ticks: {
            display: false,
          },
          suggestedMin: 10,
        },
      },
    },
  })
}

const renderTimelineChart = () => {
  if (timelineChartInstance) {
    timelineChartInstance.destroy()
  }

  if (!timelineCanvasRef.value || filteredHistory.value.length === 0) return

  const isDark = document.documentElement.classList.contains('dark')
  const textColor = isDark ? '#94a3b8' : '#475569'
  const gridColor = isDark ? 'rgba(71, 85, 105, 0.4)' : 'rgba(203, 213, 225, 0.9)'

  const labels = filteredHistory.value.map((v) => {
    return new Date(v.recorded_at).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  })

  let datasets: any[] = []

  if (selectedTimelineMetric.value === 'bp') {
    datasets = [
      {
        label: 'Systolic BP (Normal: <120)',
        data: filteredHistory.value.map((v) => v.systolic_bp),
        borderColor: '#f43f5e',
        backgroundColor: 'rgba(244, 63, 94, 0.05)',
        fill: true,
        tension: 0.35,
        borderWidth: 3,
        pointBackgroundColor: '#f43f5e',
      },
      {
        label: 'Diastolic BP (Normal: <80)',
        data: filteredHistory.value.map((v) => v.diastolic_bp),
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.05)',
        fill: true,
        tension: 0.35,
        borderWidth: 3,
        pointBackgroundColor: '#f59e0b',
      },
    ]
  } else if (selectedTimelineMetric.value === 'sugar') {
    datasets = [
      {
        label: 'Blood Glucose (Normal: 70-140)',
        data: filteredHistory.value.map((v) => v.blood_sugar),
        borderColor: '#0d9488',
        backgroundColor: 'rgba(13, 148, 136, 0.05)',
        fill: true,
        tension: 0.35,
        borderWidth: 3,
        pointBackgroundColor: '#0d9488',
      },
    ]
  } else if (selectedTimelineMetric.value === 'cardio') {
    datasets = [
      {
        label: 'Pulse Rate (Normal: 60-100)',
        data: filteredHistory.value.map((v) => v.pulse_rate),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.05)',
        fill: true,
        tension: 0.35,
        borderWidth: 3,
        pointBackgroundColor: '#10b981',
      },
      {
        label: 'Respiration Rate (Normal: 12-20)',
        data: filteredHistory.value.map((v) => v.respiration_rate),
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.05)',
        fill: true,
        tension: 0.35,
        borderWidth: 3,
        pointBackgroundColor: '#6366f1',
      },
    ]
  } else if (selectedTimelineMetric.value === 'temp') {
    datasets = [
      {
        label: 'Core Temp (Normal: 98.6)',
        data: filteredHistory.value.map((v) => v.temperature),
        borderColor: '#ec4899',
        backgroundColor: 'rgba(236, 72, 153, 0.05)',
        fill: true,
        tension: 0.35,
        borderWidth: 3,
        pointBackgroundColor: '#ec4899',
      },
    ]
  }

  timelineChartInstance = new Chart(timelineCanvasRef.value, {
    type: 'line',
    data: {
      labels,
      datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: textColor,
            font: { family: 'Outfit, sans-serif', weight: 'bold', size: 11 },
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: textColor,
            font: { family: 'Outfit, sans-serif', size: 9 },
          },
        },
        y: {
          grid: { color: gridColor },
          ticks: {
            color: textColor,
            font: { family: 'Outfit, sans-serif', size: 10 },
          },
          suggestedMin: selectedTimelineMetric.value === 'temp' ? 95 : 0,
        },
      },
    },
  })
}

watch([selectedTimelineMetric, showFullHistory], () => {
  renderTimelineChart()
})

const formatDate = (dateString: string) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const formatDateTime = (dateString: string) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(loadData)

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
  if (timelineChartInstance) {
    timelineChartInstance.destroy()
  }
})
</script>

<template>
  <DashboardLayout>
    <!-- Page Header -->
    <div class="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <button
            @click="router.back()"
            class="px-4 py-1.5 rounded-xl bg-gray-50 dark:bg-slate-800 text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-200 text-xs font-black uppercase tracking-widest border border-gray-100 dark:border-slate-700 transition-all"
          >
            ← Back
          </button>
          <span
            class="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest border border-emerald-100 dark:border-emerald-500/20"
          >
            Clinical Charts
          </span>
        </div>
        <h2 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
          Patient Vitals Metrics
        </h2>
      </div>
    </div>

    <!-- General Loader -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-32 space-y-4">
      <div class="animate-spin rounded-full h-12 w-12 border-[3px] border-emerald-600 border-t-transparent"></div>
      <p class="text-xs text-gray-400 dark:text-slate-500 uppercase tracking-widest font-black">
        Retrieving clinical records...
      </p>
    </div>

    <div v-else-if="patient" class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
      <!-- Left: Patient Summary Info -->
      <div class="lg:col-span-1 space-y-6">
        <div class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-premium text-center">
          <!-- Avatar -->
          <div class="w-24 h-24 rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white font-black text-4xl flex items-center justify-center shadow-lg shadow-emerald-500/10 mx-auto mb-6">
            {{ patient.full_name?.charAt(0) || 'P' }}
          </div>
          
          <h3 class="text-xl font-black text-gray-900 dark:text-white tracking-tight">
            {{ patient.full_name }}
          </h3>
          <p class="text-xs text-gray-400 dark:text-slate-500 mt-1 font-bold uppercase tracking-wider">
            Patient profile
          </p>

          <!-- Divider -->
          <div class="h-px bg-gray-100 dark:bg-slate-800/80 my-6"></div>

          <!-- Metadata List -->
          <div class="space-y-4 text-left">
            <div class="flex justify-between text-xs">
              <span class="text-gray-400 font-bold uppercase tracking-wider">Gender</span>
              <span class="text-gray-900 dark:text-white font-black capitalize">{{ patient.gender }}</span>
            </div>
            <div class="flex justify-between text-xs">
              <span class="text-gray-400 font-bold uppercase tracking-wider">DOB</span>
              <span class="text-gray-900 dark:text-white font-black">{{ patient.date_of_birth }}</span>
            </div>
            <div class="flex justify-between text-xs">
              <span class="text-gray-400 font-bold uppercase tracking-wider">Blood Group</span>
              <span class="text-rose-600 dark:text-rose-400 font-black">{{ patient.blood_group || 'N/A' }}</span>
            </div>
            <div class="flex justify-between text-xs" v-if="patient.relation">
              <span class="text-gray-400 font-bold uppercase tracking-wider">Relation</span>
              <span class="text-gray-900 dark:text-white font-black">{{ patient.relation }}</span>
            </div>
            <div class="flex justify-between text-xs" v-if="patient.assigned_doctor_name">
              <span class="text-gray-400 font-bold uppercase tracking-wider">Assigned Physician</span>
              <span class="text-teal-600 dark:text-teal-400 font-black">Dr. {{ patient.assigned_doctor_name }}</span>
            </div>
          </div>
        </div>

        <!-- Medical History Card -->
        <div class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-premium">
          <h4 class="text-xs font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-4">
            Medical History
          </h4>
          <p class="text-sm text-gray-600 dark:text-slate-300 font-medium leading-relaxed">
            {{ patient.medical_history || 'No historical medical records or pre-existing conditions registered.' }}
          </p>
        </div>
      </div>

      <!-- Right: Vitals Display and Charts -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Vitals Not Recorded -->
        <div
          v-if="!vitals"
          class="card-animate flex flex-col items-center justify-center py-20 bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-[2.5rem] shadow-premium text-center px-6"
        >
          <div class="w-16 h-16 bg-amber-50 dark:bg-amber-950/20 rounded-2xl flex items-center justify-center text-amber-500 mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-lg font-black text-gray-900 dark:text-white mb-2">No Vitals Captured</h3>
          <p class="text-xs text-gray-400 dark:text-slate-500 max-w-xs font-medium">
            Clinical vitals have not been captured for this patient yet. Please ask a nurse to perform a screening checkup.
          </p>
        </div>

        <template v-else>
          <!-- Clinical Gauge Cards Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- Blood Pressure Card -->
            <div class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm hover:shadow-premium transition-all">
              <div class="flex items-center justify-between mb-3">
                <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest">Blood Pressure</p>
                <span :class="`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-wider ${formatBloodPressureStatus(vitals.systolic_bp).color}`">
                  {{ formatBloodPressureStatus(vitals.systolic_bp).label }}
                </span>
              </div>
              <p class="text-2xl font-black text-rose-600 dark:text-rose-400">{{ vitals.systolic_bp }}/{{ vitals.diastolic_bp }} <span class="text-xs font-bold text-gray-400">mmHg</span></p>
              <p class="text-[9px] text-gray-400 mt-2 font-medium">Optimal Baseline: &lt;120 / &lt;80 mmHg</p>
            </div>

            <!-- Blood Sugar Card -->
            <div class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm hover:shadow-premium transition-all">
              <div class="flex items-center justify-between mb-3">
                <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest">Blood Glucose</p>
                <span :class="`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-wider ${formatSugarStatus(vitals.blood_sugar).color}`">
                  {{ formatSugarStatus(vitals.blood_sugar).label }}
                </span>
              </div>
              <p class="text-2xl font-black text-teal-600 dark:text-teal-400">{{ vitals.blood_sugar }} <span class="text-xs font-bold text-gray-400">mg/dL</span></p>
              <p class="text-[9px] text-gray-400 mt-2 font-medium">Optimal Baseline: 70 - 140 mg/dL</p>
            </div>

            <!-- Pulse Rate Card -->
            <div class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm hover:shadow-premium transition-all">
              <div class="flex items-center justify-between mb-3">
                <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest">Heart Rate (Pulse)</p>
                <span :class="`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-wider ${formatPulseStatus(vitals.pulse_rate).color}`">
                  {{ formatPulseStatus(vitals.pulse_rate).label }}
                </span>
              </div>
              <p class="text-2xl font-black text-emerald-600 dark:text-emerald-400">{{ vitals.pulse_rate }} <span class="text-xs font-bold text-gray-400">bpm</span></p>
              <p class="text-[9px] text-gray-400 mt-2 font-medium">Optimal Baseline: 60 - 100 bpm</p>
            </div>

            <!-- Body Temperature Card -->
            <div class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm hover:shadow-premium transition-all">
              <div class="flex items-center justify-between mb-3">
                <p class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest">Core Temperature</p>
                <span :class="`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-wider ${formatTempStatus(vitals.temperature).color}`">
                  {{ formatTempStatus(vitals.temperature).label }}
                </span>
              </div>
              <p class="text-2xl font-black text-indigo-600 dark:text-indigo-400">{{ vitals.temperature }} <span class="text-xs font-bold text-gray-400">°F</span></p>
              <p class="text-[9px] text-gray-400 mt-2 font-medium">Optimal Baseline: 97.8 - 99.0 °F</p>
            </div>
          </div>

          <!-- Chart Card -->
          <div class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-premium">
            <h4 class="text-xs font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
              <span class="h-1.5 w-4 bg-teal-600 rounded-full"></span>
              Deviation Radar Chart (Relative to optimal baseline)
            </h4>
            <div class="h-80 w-full relative">
              <canvas ref="canvasRef"></canvas>
            </div>
          </div>

          <!-- Vitals Timeline Chart Card -->
          <div class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-premium" v-if="vitalsHistory.length > 1">
            <div class="flex items-center justify-between flex-wrap gap-4 mb-6">
              <div>
                <h4 class="text-xs font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-2">
                  <span class="h-1.5 w-4 bg-indigo-600 rounded-full"></span>
                  Clinical Vitals Timeline Variation
                </h4>
                <p class="text-[10px] text-gray-400 dark:text-slate-500 mt-1 font-medium">
                  Showing {{ showFullHistory ? 'full screening history' : `last ${filteredHistory.length} records` }}
                </p>
              </div>

              <!-- Controls -->
              <div class="flex items-center gap-3">
                <!-- History length toggle -->
                <button
                  @click="showFullHistory = !showFullHistory"
                  class="px-3 py-1.5 rounded-lg bg-gray-50 hover:bg-gray-100 dark:bg-slate-800 dark:hover:bg-slate-700 text-gray-500 dark:text-slate-400 text-[9px] font-black uppercase tracking-wider transition-all border border-gray-100 dark:border-slate-700"
                >
                  {{ showFullHistory ? 'Show Recent Only' : 'Show Full Stats' }}
                </button>

                <!-- Segment Selector -->
                <div class="flex items-center p-0.5 bg-gray-100 dark:bg-slate-800 rounded-lg gap-0.5 border border-gray-200/40 dark:border-slate-700/40">
                  <button
                    v-for="m in [
                      { id: 'bp', label: 'BP' },
                      { id: 'sugar', label: 'Sugar' },
                      { id: 'cardio', label: 'Cardio' },
                      { id: 'temp', label: 'Temp' }
                    ]"
                    :key="m.id"
                    @click="selectedTimelineMetric = m.id as any"
                    :class="`px-2.5 py-1 rounded-md text-[8px] font-black uppercase tracking-wider transition-all ${
                      selectedTimelineMetric === m.id
                        ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-sm'
                        : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
                    }`"
                  >
                    {{ m.label }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Timeline Chart Canvas -->
            <div class="h-80 w-full relative">
              <canvas ref="timelineCanvasRef"></canvas>
            </div>
          </div>

          <!-- Notes Card -->
          <div class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-premium">
            <h4 class="text-xs font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-4">
              Clinical Screening Notes
            </h4>
            <p class="text-sm text-gray-600 dark:text-slate-300 font-medium leading-relaxed italic">
              "{{ vitals.notes || 'No additional screening notes provided by the recording nurse.' }}"
            </p>
            <div class="h-px bg-gray-100 dark:bg-slate-800/80 my-4"></div>
            <p class="text-[10px] text-gray-400 dark:text-slate-500 font-bold uppercase tracking-wider">
              Screening Performed on: {{ formatDateTime(vitals.recorded_at) }}
            </p>
          </div>
        </template>
      </div>
    </div>
  </DashboardLayout>
</template>
