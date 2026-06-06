<script setup lang="ts">
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import { Chart } from 'chart.js/auto'
import api from '../utils/axios'

const props = defineProps<{
  patients?: any[]
  role: 'user' | 'doctor' | 'nurse' | 'admin'
  currentUserId?: string
}>()

const localPatients = ref<any[]>([])
const patientVitals = ref<Record<string, any>>({})
const isLoading = ref(true)
const selectedMetric = ref<'bp' | 'sugar' | 'cardio' | 'temp'>('bp')

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

const chartPatients = computed(() => {
  let list = localPatients.value
  if (props.role === 'nurse' && props.currentUserId) {
    list = list.filter((p) => {
      const v = patientVitals.value[p.id]
      return v && String(v.recorded_by) === String(props.currentUserId)
    })
  }
  // Only plot patients who actually have vitals recorded in this component
  return list.filter((p) => patientVitals.value[p.id])
})

const averageStats = computed(() => {
  const list = chartPatients.value
  if (list.length === 0) return null

  let totalSys = 0
  let totalDia = 0
  let totalSugar = 0
  let totalPulse = 0
  let totalTemp = 0
  let highBPCount = 0
  let highSugarCount = 0

  list.forEach((p) => {
    const v = patientVitals.value[p.id]
    totalSys += v.systolic_bp || 0
    totalDia += v.diastolic_bp || 0
    totalSugar += v.blood_sugar || 0
    totalPulse += v.pulse_rate || 0
    totalTemp += v.temperature || 0

    if (v.systolic_bp >= 140) highBPCount++
    if (v.blood_sugar > 140) highSugarCount++
  })

  const count = list.length
  return {
    avgBP: `${Math.round(totalSys / count)}/${Math.round(totalDia / count)}`,
    avgSugar: Math.round((totalSugar / count) * 10) / 10,
    avgPulse: Math.round(totalPulse / count),
    avgTemp: Math.round((totalTemp / count) * 10) / 10,
    highBPCount,
    highSugarCount,
  }
})

const loadData = async () => {
  isLoading.value = true
  try {
    if (props.role === 'admin') {
      const res = await api.get('/patients/')
      localPatients.value = res.data.data || []
    } else {
      localPatients.value = props.patients || []
    }

    if (localPatients.value.length === 0) {
      isLoading.value = false
      return
    }

    const vitalsPromises = localPatients.value.map(async (p) => {
      try {
        const res = await api.get(`/vitals/${p.id}`)
        const data = res.data.data || res.data
        const singleVital = Array.isArray(data) ? data[0] : data
        if (singleVital && singleVital.patient_id) {
          patientVitals.value[p.id] = singleVital
        }
      } catch {
        // no vitals recorded yet
      }
    })

    await Promise.all(vitalsPromises)
  } catch (error) {
    console.error('Failed to load vitals for chart:', error)
  } finally {
    isLoading.value = false
    // Delay slightly to ensure canvas is rendered
    setTimeout(() => {
      renderChart()
    }, 50)
  }
}

const renderChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  if (!canvasRef.value) return

  const patientsList = chartPatients.value
  if (patientsList.length === 0) return

  const isDark = document.documentElement.classList.contains('dark')
  const textColor = isDark ? '#94a3b8' : '#475569'
  const gridColor = isDark ? 'rgba(51, 65, 85, 0.3)' : 'rgba(226, 232, 240, 0.8)'

  const datasets: any[] = []

  if (selectedMetric.value === 'bp') {
    datasets.push(
      {
        label: 'Systolic BP (Normal: <120)',
        data: patientsList.map((p) => patientVitals.value[p.id].systolic_bp),
        backgroundColor: 'rgba(244, 63, 94, 0.75)',
        borderColor: '#f43f5e',
        borderWidth: 2,
        borderRadius: 8,
        barPercentage: 0.6,
        categoryPercentage: 0.7,
      },
      {
        label: 'Diastolic BP (Normal: <80)',
        data: patientsList.map((p) => patientVitals.value[p.id].diastolic_bp),
        backgroundColor: 'rgba(245, 158, 11, 0.75)',
        borderColor: '#f59e0b',
        borderWidth: 2,
        borderRadius: 8,
        barPercentage: 0.6,
        categoryPercentage: 0.7,
      },
    )
  } else if (selectedMetric.value === 'sugar') {
    datasets.push({
      label: 'Blood Sugar (Normal: 70-140 mg/dL)',
      data: patientsList.map((p) => patientVitals.value[p.id].blood_sugar),
      backgroundColor: 'rgba(13, 148, 136, 0.75)',
      borderColor: '#0d9488',
      borderWidth: 2,
      borderRadius: 8,
      barPercentage: 0.4,
    })
  } else if (selectedMetric.value === 'cardio') {
    datasets.push(
      {
        label: 'Pulse Rate (bpm, Normal: 60-100)',
        data: patientsList.map((p) => patientVitals.value[p.id].pulse_rate),
        backgroundColor: 'rgba(16, 185, 129, 0.75)',
        borderColor: '#10b981',
        borderWidth: 2,
        borderRadius: 8,
        barPercentage: 0.6,
        categoryPercentage: 0.7,
      },
      {
        label: 'Respiration Rate (/min, Normal: 12-20)',
        data: patientsList.map((p) => patientVitals.value[p.id].respiration_rate),
        backgroundColor: 'rgba(99, 102, 241, 0.75)',
        borderColor: '#6366f1',
        borderWidth: 2,
        borderRadius: 8,
        barPercentage: 0.6,
        categoryPercentage: 0.7,
      },
    )
  } else if (selectedMetric.value === 'temp') {
    datasets.push({
      label: 'Body Temperature (°F, Normal: 98.6)',
      data: patientsList.map((p) => patientVitals.value[p.id].temperature),
      backgroundColor: 'rgba(236, 72, 153, 0.75)',
      borderColor: '#ec4899',
      borderWidth: 2,
      borderRadius: 8,
      barPercentage: 0.4,
    })
  }

  chartInstance = new Chart(canvasRef.value, {
    type: 'bar',
    data: {
      labels: patientsList.map((p) => p.full_name),
      datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: textColor,
            font: { family: 'Outfit, sans-serif', weight: 'bold', size: 11 },
            padding: 16,
          },
        },
        tooltip: {
          backgroundColor: isDark ? '#0f172a' : '#ffffff',
          titleColor: isDark ? '#ffffff' : '#0f172a',
          bodyColor: isDark ? '#94a3b8' : '#475569',
          borderColor: isDark ? '#334155' : '#e2e8f0',
          borderWidth: 1,
          titleFont: { family: 'Outfit, sans-serif', weight: 'bold', size: 12 },
          bodyFont: { family: 'Outfit, sans-serif', size: 11 },
          padding: 12,
          cornerRadius: 12,
          boxPadding: 6,
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: textColor,
            font: { family: 'Outfit, sans-serif', weight: 'bold', size: 10 },
          },
        },
        y: {
          grid: { color: gridColor },
          ticks: {
            color: textColor,
            font: { family: 'Outfit, sans-serif', size: 10 },
          },
          min: selectedMetric.value === 'temp' ? 94 : 0,
        },
      },
    },
  })
}

// Watchers
watch(selectedMetric, () => {
  renderChart()
})

watch(
  () => props.patients,
  (newPatients) => {
    if (props.role !== 'admin' && newPatients) {
      loadData()
    }
  },
  { deep: true },
)

onMounted(loadData)

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<template>
  <div
    class="card-animate bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-premium"
  >
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4 mb-6">
      <div>
        <h3
          class="text-base font-black text-gray-900 dark:text-white uppercase tracking-widest flex items-center gap-2"
        >
          <span class="h-1.5 w-6 bg-teal-600 rounded-full"></span>
          Clinical Vitals Dashboard
        </h3>
        <p class="text-xs text-gray-400 dark:text-slate-500 mt-1 font-medium">
          <template v-if="role === 'user'"
            >Vitals trends for your registered family profiles</template
          >
          <template v-if="role === 'doctor'"
            >Comparative vitals analytics for your assigned consultations</template
          >
          <template v-if="role === 'nurse'"
            >Visualizing patient vitals recorded during your shifts</template
          >
          <template v-if="role === 'admin'">Enterprise-wide patient vitals overview</template>
        </p>
      </div>

      <!-- Segment Selector tabs -->
      <div
        class="flex items-center p-1 bg-gray-100 dark:bg-slate-800/60 rounded-xl gap-0.5 border border-gray-200/40 dark:border-slate-700/40"
      >
        <button
          v-for="m in [
            { id: 'bp', label: 'BP' },
            { id: 'sugar', label: 'Sugar' },
            { id: 'cardio', label: 'Cardio' },
            { id: 'temp', label: 'Temp' },
          ]"
          :key="m.id"
          @click="selectedMetric = m.id as any"
          :class="`px-3.5 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider transition-all ${
            selectedMetric === m.id
              ? 'bg-white dark:bg-slate-900 text-teal-600 dark:text-teal-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          {{ m.label }}
        </button>
      </div>
    </div>

    <!-- Loader -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-24 space-y-4">
      <div
        class="animate-spin rounded-full h-8 w-8 border-[2px] border-teal-600 border-t-transparent"
      ></div>
      <p class="text-xs text-gray-400 dark:text-slate-500 uppercase tracking-widest font-black">
        Loading Vitals Stats...
      </p>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="chartPatients.length === 0"
      class="flex flex-col items-center justify-center py-16 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border border-dashed border-gray-100 dark:border-slate-800"
    >
      <div
        class="w-14 h-14 bg-white dark:bg-slate-900 rounded-2xl shadow-sm flex items-center justify-center mb-4 text-gray-300 dark:text-slate-700"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"
          />
        </svg>
      </div>
      <h4 class="text-sm font-bold text-gray-800 dark:text-slate-200 mb-1">
        No vitals data to plot
      </h4>
      <p class="text-xs text-gray-400 dark:text-slate-500 text-center max-w-xs px-4">
        Once vitals have been captured and saved, clinical charts will materialize here
        automatically.
      </p>
    </div>

    <div v-else class="space-y-6">
      <!-- Summary Stats row -->
      <div v-if="averageStats" class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- BP Average -->
        <div
          class="bg-gray-50/60 dark:bg-slate-800/30 border border-gray-100 dark:border-slate-800 rounded-2xl p-4"
        >
          <p
            class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
          >
            Avg Blood Pressure
          </p>
          <p class="text-lg font-black text-rose-600 dark:text-rose-400 leading-none mt-1.5">
            {{ averageStats.avgBP }}
            <span class="text-[10px] text-gray-400 font-bold ml-0.5">mmHg</span>
          </p>
        </div>
        <!-- Glucose Average -->
        <div
          class="bg-gray-50/60 dark:bg-slate-800/30 border border-gray-100 dark:border-slate-800 rounded-2xl p-4"
        >
          <p
            class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
          >
            Avg Blood Glucose
          </p>
          <p class="text-lg font-black text-teal-600 dark:text-teal-400 leading-none mt-1.5">
            {{ averageStats.avgSugar }}
            <span class="text-[10px] text-gray-400 font-bold ml-0.5">mg/dL</span>
          </p>
        </div>
        <!-- High BP Alert -->
        <div
          class="bg-gray-50/60 dark:bg-slate-800/30 border border-gray-100 dark:border-slate-800 rounded-2xl p-4 flex items-center justify-between"
        >
          <div>
            <p
              class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
            >
              Hypertension Alerts
            </p>
            <p
              class="text-lg font-black leading-none mt-1.5"
              :class="
                averageStats.highBPCount > 0
                  ? 'text-rose-600 animate-pulse'
                  : 'text-gray-900 dark:text-white'
              "
            >
              {{ averageStats.highBPCount }}
            </p>
          </div>
          <span
            v-if="averageStats.highBPCount > 0"
            class="h-2 w-2 rounded-full bg-rose-500 animate-ping"
          ></span>
        </div>
        <!-- High Sugar Alert -->
        <div
          class="bg-gray-50/60 dark:bg-slate-800/30 border border-gray-100 dark:border-slate-800 rounded-2xl p-4 flex items-center justify-between"
        >
          <div>
            <p
              class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
            >
              Hyperglycemia Alerts
            </p>
            <p
              class="text-lg font-black leading-none mt-1.5"
              :class="
                averageStats.highSugarCount > 0 ? 'text-amber-600' : 'text-gray-900 dark:text-white'
              "
            >
              {{ averageStats.highSugarCount }}
            </p>
          </div>
          <span
            v-if="averageStats.highSugarCount > 0"
            class="h-2 w-2 rounded-full bg-amber-500"
          ></span>
        </div>
      </div>

      <!-- Chart Container -->
      <div class="h-72 w-full relative">
        <canvas ref="canvasRef"></canvas>
      </div>
    </div>
  </div>
</template>
