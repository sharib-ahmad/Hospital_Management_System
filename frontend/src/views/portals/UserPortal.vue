<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const router = useRouter()
const notification = useNotificationStore()
const patients = ref<any[]>([])
const applications = ref<any[]>([])
const isLoading = ref(true)

const stats = ref([
  {
    name: 'Profile Status',
    value: 'Verified',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    color: 'bg-emerald-600',
  },
  {
    name: 'Registered Patients',
    value: '0',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'bg-teal-600',
  },
])

const loadData = async () => {
  try {
    const [patientsRes, appsRes] = await Promise.all([
      api.get('/patients/my'),
      api.get('/applications/my'),
    ])
    patients.value = patientsRes.data.data || []
    const allApps = appsRes.data.data || []

    // Filter to show pending apps or rejected patient apps
    applications.value = allApps.filter(
      (app: any) =>
        app.status === 'pending' || (app.status === 'rejected' && app.role_applied === 'patient'),
    )

    stats.value[1].value = patients.value.length.toString()
  } catch (error) {
    console.error('Failed to load data', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <PortalBase role="user" title="Welcome to MediFlow" :stats="stats">
    <template #main>
      <!-- Patient Management Section -->
      <div class="space-y-8">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
            My Registered Patients
          </h3>
          <button
            @click="router.push('/register-patient')"
            class="px-5 py-2.5 bg-emerald-600/10 text-emerald-600 dark:text-emerald-400 font-bold rounded-xl hover:bg-emerald-600 hover:text-white transition-all text-sm flex items-center gap-2"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="3"
                d="M12 4v16m8-8H4"
              />
            </svg>
            Register Patient
          </button>
        </div>

        <div v-if="isLoading" class="flex justify-center py-20">
          <div
            class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
          ></div>
        </div>

        <div
          v-else-if="patients.length === 0"
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
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
          <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
            No patients registered
          </h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium mb-8">
            Register yourself or your family members to start managing health records and
            appointments.
          </p>
          <button
            @click="router.push('/register-patient')"
            class="px-8 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/20 hover:-translate-y-1 transition-all uppercase text-xs tracking-widest"
          >
            Start Registration
          </button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="patient in patients"
            :key="patient.id"
            class="glass p-8 rounded-[2rem] border border-white/40 dark:border-white/5 hover:border-emerald-500/30 transition-all group shadow-premium"
          >
            <div class="flex items-start justify-between mb-6">
              <div
                class="w-14 h-14 bg-emerald-50 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center text-emerald-600 shadow-sm group-hover:scale-110 transition-transform"
              >
                <span class="font-black text-xl">{{ patient.full_name?.charAt(0) || 'P' }}</span>
              </div>
              <span
                class="px-4 py-1.5 bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 text-[10px] font-black uppercase tracking-widest rounded-full border border-emerald-200/50 dark:border-emerald-500/20"
              >
                {{ patient.blood_group }}
              </span>
            </div>
            <h3 class="text-xl font-black text-gray-900 dark:text-white mb-1 tracking-tight">
              {{ patient.full_name }}
            </h3>
            <p class="text-[10px] text-emerald-600 dark:text-emerald-400 font-black uppercase tracking-[0.2em] mb-3">
              {{ patient.relation }}
            </p>
            <p
              class="text-xs text-gray-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-6"
            >
              {{ patient.gender }} • {{ patient.date_of_birth }}
            </p>

            <div
              class="pt-6 border-t border-gray-100 dark:border-slate-800 flex items-center justify-between"
            >
              <span class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]"
                >Clinical Records</span
              >
              <div
                class="w-8 h-8 rounded-full bg-gray-50 dark:bg-slate-800 flex items-center justify-center group-hover:bg-emerald-600 group-hover:text-white transition-all cursor-pointer"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="3"
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Pending/Rejected Applications -->
        <div v-if="applications.length > 0" class="space-y-8 pt-4">
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-amber-500 rounded-full"></span>
            Registration Progress
          </h3>

          <div class="grid grid-cols-1 gap-6">
            <div
              v-for="app in applications"
              :key="app.id"
              class="glass p-6 rounded-3xl border border-white/40 dark:border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-premium"
            >
              <div class="flex items-center gap-6">
                <div
                  :class="`w-12 h-12 rounded-2xl flex items-center justify-center ${app.status === 'pending' ? 'bg-amber-50 text-amber-600' : 'bg-red-50 text-red-600'}`"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      v-if="app.status === 'pending'"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-12 0 9 9 0 0112 0z"
                    />
                    <path
                      v-else
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </div>
                <div>
                  <h4 class="text-lg font-black text-gray-900 dark:text-white">
                    {{ app.patient_full_name }}
                  </h4>
                  <p class="text-xs text-gray-500 font-bold uppercase tracking-widest mt-0.5">
                    {{ app.relation }} • Patient Registration
                  </p>
                </div>
              </div>

              <div class="flex flex-col md:items-end gap-2">
                <div class="flex items-center gap-2">
                  <span
                    :class="`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${app.status === 'pending' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`"
                  >
                    {{ app.status }}
                  </span>
                </div>
                <p
                  v-if="app.reason && app.status === 'rejected'"
                  class="text-xs text-red-500 font-bold max-w-sm md:text-right"
                >
                  {{ app.reason }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #sidebar>
      <!-- Pharmacy Section -->
      <div
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-8 shadow-premium relative overflow-hidden group"
      >
        <div
          class="absolute -right-4 -top-4 w-24 h-24 bg-emerald-600/10 rounded-full blur-2xl group-hover:bg-emerald-600/20 transition-all"
        ></div>

        <div
          class="w-14 h-14 bg-emerald-50 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center text-emerald-600 mb-6"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-8 w-8"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
            />
          </svg>
        </div>

        <h3 class="text-xl font-black text-gray-900 dark:text-white mb-2 tracking-tight">
          MediStore
        </h3>
        <p class="text-sm text-gray-500 dark:text-slate-400 font-medium mb-8 leading-relaxed">
          Order prescribed medicines and health supplements directly to your home.
        </p>

        <div class="space-y-4 mb-8">
          <div
            v-for="i in 3"
            :key="i"
            class="flex items-center gap-4 p-4 bg-gray-50/50 dark:bg-slate-800/50 rounded-2xl opacity-50 grayscale pointer-events-none border border-transparent"
          >
            <div
              class="w-10 h-10 bg-gray-200 dark:bg-slate-700 rounded-xl flex items-center justify-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4"
                />
              </svg>
            </div>
            <div class="flex-1 space-y-1.5">
              <div class="h-2.5 w-16 bg-gray-200 dark:bg-slate-700 rounded-full"></div>
              <div class="h-2 w-10 bg-gray-100 dark:bg-slate-700/50 rounded-full"></div>
            </div>
            <div class="h-6 w-12 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg"></div>
          </div>
        </div>

        <button
          class="w-full py-4 bg-emerald-600/10 text-emerald-600 dark:text-emerald-400 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] pointer-events-none"
        >
          Launching Soon
        </button>
      </div>

      <!-- Support Card -->
      <div
        class="bg-gradient-to-br from-emerald-600 to-teal-700 rounded-[2.5rem] p-8 text-white shadow-xl shadow-emerald-500/30 mt-10"
      >
        <h3 class="text-xl font-black mb-4 tracking-tight">Need Help?</h3>
        <p class="text-emerald-50 text-sm mb-8 font-medium leading-relaxed opacity-90">
          Our support team is available 24/7 for any questions regarding patient registration or
          medical services.
        </p>
        <button
          class="w-full py-4 bg-white text-emerald-600 rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-lg hover:-translate-y-1 transition-all"
        >
          Contact Support
        </button>
      </div>
    </template>
  </PortalBase>
</template>
