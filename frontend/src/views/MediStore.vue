<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import api from '../utils/axios'
import { useNotificationStore } from '../stores/notification'

import { useCartStore } from '../stores/cart'

const router = useRouter()
const notification = useNotificationStore()
const cartStore = useCartStore()

// State
const medicines = ref<any[]>([])
const myPatients = ref<any[]>([])
const myOrders = ref<any[]>([])
const isLoading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('All')
const activeViewTab = ref('browse') // 'browse' or 'orders'

const categories = [
  'All',
  'Antibiotic',
  'Pain Relief',
  'Supplements',
  'Cold & Flu',
  'Heart Health',
  'Other',
]

const stats = ref([
  {
    name: 'Available Medicines',
    value: '0',
    icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z',
    color: 'bg-emerald-600',
  },
  {
    name: 'My Orders',
    value: '0',
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
    color: 'bg-teal-600',
  },
])

const loadData = async () => {
  isLoading.value = true
  try {
    const [medsRes, patientsRes, ordersRes] = await Promise.all([
      api.get('/medistore/medicines'),
      api.get('/patients/my'),
      api.get('/medistore/orders/my'),
    ])
    medicines.value = medsRes.data.data || []
    myPatients.value = patientsRes.data.data || []
    myOrders.value = ordersRes.data.data || []

    if (stats.value[0]) stats.value[0].value = medicines.value.length.toString()
    if (stats.value[1]) stats.value[1].value = myOrders.value.length.toString()
  } catch (error) {
    notification.error('Failed to load medicine store catalog')
  } finally {
    isLoading.value = false
  }
}

const filteredMedicines = computed(() => {
  return medicines.value.filter((med) => {
    const matchesSearch =
      med.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      med.description?.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory =
      selectedCategory.value === 'All' || med.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const getOrderStatusClass = (status: string) => {
  switch (status) {
    case 'pending':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20'
    case 'processing':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-500/20'
    case 'shipped':
      return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20'
    case 'delivered':
      return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20'
    case 'cancelled':
      return 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400 border border-rose-200 dark:border-rose-500/20'
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-slate-800 dark:text-slate-400 border border-gray-200 dark:border-slate-700'
  }
}

onMounted(loadData)
</script>

<template>
  <DashboardLayout>
    <!-- Page Header -->
    <div class="mb-12 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <span
            class="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest border border-emerald-100 dark:border-emerald-500/20"
          >
            User Portal
          </span>
        </div>
        <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">
          MediStore Pharmacy
        </h1>
        <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
          Browse medicines, search catalog, and track your pharmacy orders.
        </p>
      </div>

      <!-- Go to Basket Button -->
      <RouterLink
        to="/store/basket"
        class="px-8 py-4 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/25 hover:-translate-y-0.5 transition-all uppercase tracking-widest text-xs flex items-center justify-center gap-3 shrink-0"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2.5"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
          />
        </svg>
        View Basket ({{ cartStore.cartCount }})
      </RouterLink>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
      <div
        v-for="stat in stats"
        :key="stat.name"
        class="card-animate group bg-white dark:bg-slate-900 p-8 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 shadow-premium hover:shadow-premium-xl transition-all duration-500 hover:-translate-y-1"
      >
        <div class="flex items-start justify-between mb-6">
          <div
            :class="`w-14 h-14 rounded-2xl flex items-center justify-center ${stat.color} shadow-lg shadow-current/20 group-hover:rotate-6 transition-transform`"
          >
            <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2.5"
                :d="stat.icon"
              />
            </svg>
          </div>
        </div>
        <div>
          <p
            class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
          >
            {{ stat.name }}
          </p>
          <p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter">
            {{ stat.value }}
          </p>
        </div>
      </div>
    </div>

    <!-- Main Section -->
    <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-10 min-h-[500px] shadow-premium flex flex-col">
      <!-- Navigation Tab Bar -->
      <div class="flex items-center gap-6 border-b border-gray-100 dark:border-slate-800 mb-8 pb-4">
        <button
          @click="activeViewTab = 'browse'"
          :class="`text-sm font-black uppercase tracking-widest pb-2 transition-all border-b-2 ${
            activeViewTab === 'browse'
              ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400'
              : 'border-transparent text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          Browse Medicines
        </button>
        <button
          @click="activeViewTab = 'orders'"
          :class="`text-sm font-black uppercase tracking-widest pb-2 transition-all border-b-2 ${
            activeViewTab === 'orders'
              ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400'
              : 'border-transparent text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
          }`"
        >
          My Orders ({{ myOrders.length }})
        </button>
      </div>

      <div v-if="isLoading" class="flex justify-center py-20 flex-1 items-center">
        <div
          class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
        ></div>
      </div>

      <!-- Tab Content: Browse medicines -->
      <div v-else-if="activeViewTab === 'browse'" class="space-y-8">
        <!-- Search and Filter categories -->
        <div class="flex flex-col lg:flex-row gap-4 items-center justify-between">
          <div class="relative w-full lg:max-w-md group">
            <div
              class="absolute inset-y-0 left-4 flex items-center pointer-events-none text-gray-400 group-focus-within:text-emerald-500 transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
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
              placeholder="Search medicine catalog..."
              class="w-full pl-12 pr-4 py-3.5 bg-gray-50 dark:bg-slate-800 border border-gray-100 dark:border-slate-800/80 rounded-2xl text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500/40 text-gray-900 dark:text-white transition-all"
            />
          </div>

          <!-- Category Pills -->
          <div class="flex items-center gap-2 overflow-x-auto w-full lg:w-auto pb-2 scrollbar-none">
            <button
              v-for="cat in categories"
              :key="cat"
              @click="selectedCategory = cat"
              :class="`px-4 py-2 text-xs font-black rounded-full uppercase tracking-wider transition-all border ${
                selectedCategory === cat
                  ? 'bg-emerald-600 text-white border-emerald-600 shadow-lg shadow-emerald-500/15'
                  : 'bg-white dark:bg-slate-900 border-gray-100 dark:border-slate-800 text-gray-500 dark:text-slate-400 hover:border-emerald-500/20'
              }`"
            >
              {{ cat }}
            </button>
          </div>
        </div>

        <div
          v-if="filteredMedicines.length === 0"
          class="flex flex-col items-center justify-center py-20 bg-gray-50/50 dark:bg-slate-800/30 rounded-[2.5rem] border-2 border-dashed border-gray-100 dark:border-slate-800 text-center"
        >
          <p class="text-gray-400 dark:text-slate-500 font-bold">
            No medicines match your selection
          </p>
        </div>

        <!-- Catalogue Grid -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
          <div
            v-for="med in filteredMedicines"
            :key="med.id"
            class="glass p-6 rounded-3xl border border-gray-100 dark:border-slate-800 shadow-premium flex flex-col justify-between group hover:border-emerald-500/20 transition-all duration-300"
          >
            <div>
              <div class="flex items-start justify-between mb-4">
                <div>
                  <span
                    class="px-2.5 py-1 bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 text-[9px] font-black uppercase tracking-wider rounded-md border border-emerald-100/50 dark:border-emerald-500/10"
                  >
                    {{ med.category }}
                  </span>
                  <h4 class="text-lg font-black text-gray-900 dark:text-white mt-2 line-clamp-1">
                    {{ med.name }}
                  </h4>
                </div>
              </div>
              <p class="text-xs text-gray-500 dark:text-slate-400 font-medium leading-relaxed mb-6 line-clamp-3 min-h-[4.5rem]">
                {{ med.description || 'No detailed instructions provided.' }}
              </p>
              
              <div class="flex items-baseline gap-2 mb-6 justify-between">
                <div>
                  <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest block mb-0.5">Price</span>
                  <p class="text-xl font-black text-emerald-600 dark:text-emerald-400 tracking-tight">
                    ${{ Number(med.price).toFixed(2) }}
                  </p>
                </div>
                <div class="text-right">
                  <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest block mb-0.5">Availability</span>
                  <p :class="`text-[10px] font-black uppercase tracking-widest ${med.stock > 0 ? 'text-teal-600 dark:text-teal-400' : 'text-rose-500'}`">
                    {{ med.stock > 0 ? `Stock: ${med.stock}` : 'Out of stock' }}
                  </p>
                </div>
              </div>
            </div>

            <button
              @click="cartStore.addToCart(med)"
              :disabled="med.stock <= 0"
              class="w-full py-3 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 shadow-md shadow-emerald-500/10 transition-all disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2 active:scale-95"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                />
              </svg>
              Add to Basket
            </button>
          </div>
        </div>
      </div>

      <!-- Tab Content: Past Orders -->
      <div v-else-if="activeViewTab === 'orders'" class="space-y-6">
        <div
          v-if="myOrders.length === 0"
          class="flex flex-col items-center justify-center py-20 bg-gray-50/50 dark:bg-slate-800/30 rounded-3xl border-2 border-dashed border-gray-100 dark:border-slate-800"
        >
          <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">No orders placed yet</h4>
          <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium text-center">
            When you purchase items from the pharmacy catalog, they will appear here to track your
            delivery status.
          </p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="order in myOrders"
            :key="order.id"
            class="glass p-6 rounded-3xl border border-gray-100 dark:border-slate-800 shadow-premium flex flex-col justify-between"
          >
            <div>
              <div
                class="flex items-start justify-between flex-wrap gap-4 border-b border-gray-100 dark:border-slate-800 pb-4 mb-4"
              >
                <div>
                  <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                    Order Reference
                  </p>
                  <h4 class="text-sm font-black text-gray-900 dark:text-white mt-0.5 font-mono">
                    {{ order.id.slice(0, 8) }}...
                  </h4>
                </div>
                <div>
                  <p
                    class="text-[10px] font-black text-gray-400 uppercase tracking-widest text-right"
                  >
                    Date Placed
                  </p>
                  <p class="text-xs text-gray-700 dark:text-slate-300 font-bold mt-0.5 text-right">
                    {{ formatDate(order.order_date) }}
                  </p>
                </div>
                <span
                  :class="`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${getOrderStatusClass(order.status)}`"
                >
                  {{ order.status }}
                </span>
              </div>

              <!-- Items -->
              <div class="space-y-3 mb-6">
                <div
                  v-for="item in order.items"
                  :key="item.id"
                  class="flex items-center justify-between text-xs"
                >
                  <p class="text-gray-500 dark:text-slate-400 font-medium">
                    {{ item.medicine_name }}
                    <span class="font-black text-gray-900 dark:text-white ml-2"
                      >x{{ item.quantity }}</span
                    >
                  </p>
                  <p class="font-black text-gray-950 dark:text-white">
                    ${{ (item.price * item.quantity).toFixed(2) }}
                  </p>
                </div>
              </div>
            </div>

            <div
              class="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-slate-800 flex-wrap gap-4"
            >
              <div>
                <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  Delivery Address
                </p>
                <p class="text-xs text-gray-700 dark:text-slate-300 font-medium mt-0.5">
                  {{ order.shipping_address }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  Total Amount
                </p>
                <p
                  class="text-xl font-black text-emerald-600 dark:text-emerald-400 tracking-tight mt-0.5"
                >
                  ${{ Number(order.total_price).toFixed(2) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
