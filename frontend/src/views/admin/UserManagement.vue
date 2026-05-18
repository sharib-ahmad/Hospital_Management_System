<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import { useNotificationStore } from '../../stores/notification'
import api from '../../utils/axios'

type TabType = 'users' | 'patients' | 'doctors' | 'nurses'

const notification = useNotificationStore()
const activeTab = ref<TabType>('users')
const isLoading = ref(false)
const searchQuery = ref('')
const data = ref<any[]>([])
const selectedItem = ref<any | null>(null)
const isModalOpen = ref(false)

watch(isModalOpen, (newValue) => {
  if (newValue) {
    document.body.classList.add('overflow-hidden')
  } else {
    document.body.classList.remove('overflow-hidden')
  }
})

onUnmounted(() => {
  document.body.classList.remove('overflow-hidden')
})

const openDetails = (item: any) => {
  selectedItem.value = item
  isModalOpen.value = true
}

const closeDetails = () => {
  isModalOpen.value = false
  selectedItem.value = null
}

const filteredData = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return data.value

  return data.value.filter((item) => {
    const fullName = (item.full_name || item.user?.full_name || '').toLowerCase()
    const username = (item.username || item.user?.username || '').toLowerCase()
    const email = (item.email || item.user?.email || '').toLowerCase()
    const phone = (item.phone_number || item.user?.phone_number || '').toLowerCase()
    const role = (item.role || '').toLowerCase()
    const specialization = (item.specialization || '').toLowerCase()
    const dept = (item.department_id || '').toLowerCase()

    return (
      fullName.includes(query) ||
      username.includes(query) ||
      email.includes(query) ||
      phone.includes(query) ||
      role.includes(query) ||
      specialization.includes(query) ||
      dept.includes(query)
    )
  })
})

const tabs = [
  {
    id: 'users',
    name: 'All Users',
    icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
  },
  {
    id: 'patients',
    name: 'Patients',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  },
  {
    id: 'doctors',
    name: 'Doctors',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
  },
  {
    id: 'nurses',
    name: 'Nurses',
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
  },
]

const loadData = async (tab: TabType) => {
  isLoading.value = true
  activeTab.value = tab
  try {
    let endpoint = '/auth/users'
    if (tab === 'patients') endpoint = '/patients'
    if (tab === 'doctors') endpoint = '/doctors'
    if (tab === 'nurses') endpoint = '/nurses'

    const response = await api.get(endpoint)
    data.value = response.data.data || []
  } catch (error) {
    notification.error(`Failed to load ${tab}`)
    data.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(() => loadData('users'))
</script>

<template>
  <DashboardLayout>
    <div class="mb-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none">
        User Management
      </h1>
      <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
        Manage and view all participants in the system.
      </p>
    </div>

    <!-- Tabs & Search -->
    <div
      class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-10 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100"
    >
      <div
        class="flex flex-wrap gap-2 bg-gray-100/50 dark:bg-slate-800/50 p-1.5 rounded-2xl w-fit border border-gray-100 dark:border-slate-700"
      >
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="loadData(tab.id as TabType)"
          class="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all"
          :class="
            activeTab === tab.id
              ? 'bg-white dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-500 hover:text-gray-700 dark:hover:text-white hover:bg-white/50 dark:hover:bg-slate-700/50'
          "
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.icon" />
          </svg>
          {{ tab.name }}
        </button>
      </div>

      <!-- Search Input -->
      <div class="relative max-w-sm w-full">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="`Search ${activeTab}...`"
          class="block w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-2xl text-sm font-medium focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all dark:text-white"
        />
        <button
          v-if="searchQuery"
          @click="searchQuery = ''"
          class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-white"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>

    <div
      class="glass rounded-[2.5rem] border border-white/40 dark:border-white/5 shadow-premium overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200"
    >
      <div v-if="isLoading" class="p-20 text-center">
        <div
          class="animate-spin inline-block w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full mb-4"
        ></div>
        <p class="text-gray-500 font-medium">Fetching {{ activeTab }}...</p>
      </div>

      <div v-else-if="filteredData.length === 0" class="p-20 text-center">
        <div
          class="w-16 h-16 bg-gray-50 dark:bg-slate-700/50 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <p class="text-gray-500 font-medium">No results found for "{{ searchQuery }}"</p>
        <button
          v-if="searchQuery"
          @click="searchQuery = ''"
          class="mt-2 text-emerald-600 font-bold hover:underline"
        >
          Clear search
        </button>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead
            class="bg-gray-50/50 dark:bg-slate-800/50 text-gray-400 dark:text-slate-500 text-[10px] uppercase font-black tracking-[0.2em]"
          >
            <tr>
              <th class="px-8 py-5">Name</th>
              <th class="px-8 py-5" v-if="activeTab === 'users'">Role</th>
              <th class="px-8 py-5" v-if="activeTab === 'doctors' || activeTab === 'nurses'">
                Specialization/Dept
              </th>
              <th class="px-8 py-5">Contact</th>
              <th class="px-8 py-5">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-white/5">
            <tr
              v-for="item in filteredData"
              :key="item.id"
              class="hover:bg-emerald-50/30 dark:hover:bg-emerald-900/10 transition-colors cursor-pointer group"
              @click="openDetails(item)"
            >
              <td class="px-8 py-6">
                <div class="flex items-center gap-4">
                  <div
                    class="h-10 w-10 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 font-black text-sm shadow-sm border border-emerald-200/50 dark:border-emerald-500/20 group-hover:scale-110 transition-transform"
                  >
                    {{ (item.full_name || item.username || 'U').charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="text-sm font-black text-gray-900 dark:text-white leading-tight">
                      {{ item.full_name || item.username }}
                    </p>
                    <p class="text-[10px] text-gray-500 mt-0.5">
                      ID: {{ item.id?.toString().slice(0, 8) || 'N/A' }}...
                    </p>
                  </div>
                </div>
              </td>
              <td class="px-8 py-6" v-if="activeTab === 'users'">
                <span
                  class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest border"
                  :class="{
                    'bg-blue-50 text-blue-700 border-blue-100/50': item.role === 'admin',
                    'bg-green-50 text-green-700 border-green-100/50': item.role === 'patient',
                    'bg-indigo-50 text-indigo-700 border-indigo-100/50': item.role === 'doctor',
                    'bg-teal-50 text-teal-700 border-teal-100/50': item.role === 'nurse',
                    'bg-gray-50 text-gray-700 border-gray-100/50': item.role === 'user',
                  }"
                >
                  {{ item.role }}
                </span>
              </td>
              <td class="px-8 py-6" v-if="activeTab === 'doctors' || activeTab === 'nurses'">
                <p class="text-xs font-black text-gray-900 dark:text-white">
                  {{ item.specialization || item.department_id }}
                </p>
                <p class="text-[10px] text-gray-500 uppercase font-black tracking-tighter">
                  {{ item.shift }} Shift
                </p>
              </td>
              <td class="px-8 py-6">
                <p class="text-xs font-bold text-gray-900 dark:text-white">
                  {{ item.email || item.user?.email }}
                </p>
                <p class="text-[10px] text-gray-500">
                  {{ item.phone_number || item.user?.phone_number }}
                </p>
              </td>
              <td class="px-8 py-6">
                <span
                  class="inline-flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest text-emerald-600"
                >
                  <span
                    class="h-1.5 w-1.5 bg-emerald-500 rounded-full animate-pulse shadow-sm"
                  ></span>
                  Active
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- User Detail Modal -->
    <div
      v-if="isModalOpen && selectedItem"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-md"
      @click.self="closeDetails"
    >
      <div
        class="glass w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl rounded-[2.5rem] flex flex-col animate-in fade-in zoom-in-95 duration-300"
      >
        <div
          class="p-8 border-b border-gray-100 dark:border-white/5 flex justify-between items-center"
        >
          <div class="flex items-center gap-4">
            <div
              class="h-14 w-14 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 font-black text-xl shadow-sm border border-emerald-200/50 dark:border-emerald-500/20"
            >
              {{
                (
                  selectedItem.full_name ||
                  selectedItem.user?.full_name ||
                  selectedItem.username ||
                  selectedItem.user?.username ||
                  'U'
                )
                  .charAt(0)
                  .toUpperCase()
              }}
            </div>
            <div>
              <h3
                class="text-2xl font-black text-gray-900 dark:text-white tracking-tight leading-none"
              >
                {{
                  selectedItem.full_name ||
                  selectedItem.user?.full_name ||
                  selectedItem.username ||
                  selectedItem.user?.username
                }}
              </h3>
              <p class="text-xs text-gray-500 mt-1 uppercase font-black tracking-widest">
                {{ selectedItem.role || activeTab.slice(0, -1) }} Profile
              </p>
            </div>
          </div>
          <button
            @click="closeDetails"
            class="p-2 text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-800 rounded-xl transition-all"
          >
            <svg
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-8 overflow-y-auto flex-1">
          <!-- Identity Section -->
          <div class="grid grid-cols-2 gap-8 mb-10">
            <div>
              <label
                class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                >Full Name</label
              >
              <p class="text-gray-900 dark:text-white font-bold text-lg leading-tight">
                {{ selectedItem.full_name || selectedItem.user?.full_name || 'N/A' }}
              </p>
            </div>
            <div>
              <label
                class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                >User Handle</label
              >
              <p class="text-emerald-600 dark:text-emerald-400 font-black text-lg leading-tight">
                @{{ selectedItem.username || selectedItem.user?.username }}
              </p>
            </div>
            <div>
              <label
                class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                >Email Address</label
              >
              <p class="text-gray-900 dark:text-white font-bold">
                {{ selectedItem.email || selectedItem.user?.email }}
              </p>
            </div>
            <div>
              <label
                class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                >Phone Contact</label
              >
              <p class="text-gray-900 dark:text-white font-bold">
                {{ selectedItem.phone_number || selectedItem.user?.phone_number || 'N/A' }}
              </p>
            </div>
          </div>

          <!-- Role Specific Data -->
          <div
            v-if="selectedItem.role !== 'user' || activeTab !== 'users'"
            class="bg-emerald-50/50 dark:bg-emerald-900/10 rounded-3xl p-8 mb-10 border border-emerald-100 dark:border-emerald-500/10"
          >
            <h4
              class="text-xs font-black text-gray-900 dark:text-white uppercase tracking-widest mb-6 flex items-center gap-3"
            >
              <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
              {{ selectedItem.role || activeTab.slice(0, -1) }} Credentials
            </h4>

            <div class="grid grid-cols-2 gap-8">
              <!-- Identity Fields -->
              <div v-if="selectedItem.date_of_birth">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Date of Birth</label
                >
                <p class="text-gray-900 dark:text-white font-bold text-sm">
                  {{ selectedItem.date_of_birth }}
                </p>
              </div>
              <div v-if="selectedItem.blood_group">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Blood Group</label
                >
                <span
                  class="px-3 py-1 bg-red-50 text-red-600 rounded-full text-[10px] font-black border border-red-100/50 uppercase tracking-widest"
                  >{{ selectedItem.blood_group }}</span
                >
              </div>
              <div v-if="selectedItem.gender">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Gender</label
                >
                <p
                  class="text-gray-900 dark:text-white font-bold text-sm uppercase tracking-widest"
                >
                  {{ selectedItem.gender }}
                </p>
              </div>
              <div v-if="selectedItem.emergency_contact_number">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Emergency Contact</label
                >
                <p class="text-gray-900 dark:text-white font-bold text-sm">
                  {{ selectedItem.emergency_contact_number }}
                </p>
              </div>

              <!-- Professional Fields -->
              <div v-if="selectedItem.specialization">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Specialization</label
                >
                <p class="text-gray-900 dark:text-white font-bold text-sm">
                  {{ selectedItem.specialization }}
                </p>
              </div>
              <div v-if="selectedItem.license_number">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >License Number</label
                >
                <p
                  class="text-emerald-600 dark:text-emerald-400 font-black tracking-widest font-mono text-sm"
                >
                  {{ selectedItem.license_number }}
                </p>
              </div>
              <div v-if="selectedItem.department_id">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Department</label
                >
                <p class="text-gray-900 dark:text-white font-bold text-sm">
                  {{ selectedItem.department_id }}
                </p>
              </div>
              <div v-if="selectedItem.shift">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Assigned Shift</label
                >
                <p
                  class="text-gray-900 dark:text-white font-bold text-sm uppercase tracking-widest"
                >
                  {{ selectedItem.shift }} Shift
                </p>
              </div>
              <div v-if="selectedItem.experience_years">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Clinical Experience</label
                >
                <p class="text-gray-900 dark:text-white font-bold text-sm">
                  {{ selectedItem.experience_years }} Years
                </p>
              </div>

              <!-- Patient History -->
              <div v-if="selectedItem.medical_history" class="col-span-2">
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1.5"
                  >Medical History</label
                >
                <p class="text-gray-900 dark:text-white text-sm leading-relaxed font-medium">
                  {{ selectedItem.medical_history }}
                </p>
              </div>
            </div>
          </div>

          <!-- Location Info -->
          <div class="border-t border-gray-100 dark:border-white/5 pt-8">
            <div class="flex items-start gap-4">
              <div
                class="mt-1 p-2.5 bg-gray-50 dark:bg-slate-800 rounded-xl border border-gray-100 dark:border-white/5"
              >
                <svg
                  class="h-5 w-5 text-emerald-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
              <div>
                <label
                  class="block text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1"
                  >Residential Address</label
                >
                <p class="text-gray-900 dark:text-white font-bold">
                  {{ selectedItem.address || selectedItem.user?.address || 'Address not provided' }}
                </p>
                <p class="text-xs text-gray-500 mt-1 uppercase font-black tracking-widest">
                  Pincode: {{ selectedItem.pincode || selectedItem.user?.pincode || 'N/A' }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div
          class="p-8 border-t border-gray-100 dark:border-white/5 bg-gray-50 dark:bg-slate-900/30 flex justify-between items-center"
        >
          <p
            class="text-[10px] text-gray-400 dark:text-slate-500 font-black uppercase tracking-widest"
          >
            Member Since
            {{
              selectedItem.created_at || selectedItem.user?.created_at
                ? new Date(
                    selectedItem.created_at || selectedItem.user?.created_at,
                  ).toLocaleDateString()
                : 'N/A'
            }}
          </p>
          <button
            @click="closeDetails"
            class="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-black rounded-2xl shadow-xl shadow-emerald-500/25 transition-all uppercase tracking-widest active:scale-95"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
