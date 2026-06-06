<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()
const orders = ref<any[]>([])
const isLoading = ref(true)
const selectedFilter = ref('all')

const stats = ref([
  {
    name: 'Total Pharmacy Orders',
    value: '0',
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
    color: 'bg-emerald-600',
  },
  {
    name: 'Pending Invoices',
    value: '0',
    icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'bg-teal-600',
  },
])

const loadOrders = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/medistore/orders/all')
    orders.value = response.data.data || []
    if (stats.value[0]) stats.value[0].value = orders.value.length.toString()

    const pendingOrders = orders.value.filter((o) => o.status === 'pending').length
    if (stats.value[1]) stats.value[1].value = pendingOrders.toString()
  } catch (error) {
    notification.error('Failed to load pharmacy orders catalog')
  } finally {
    isLoading.value = false
  }
}

const updateStatus = async (orderId: string, newStatus: string) => {
  try {
    await api.put(`/medistore/orders/${orderId}/status`, { status: newStatus })
    notification.success(`Order marked as ${newStatus} successfully`)
    await loadOrders()
  } catch (error: any) {
    const message = error.response?.data?.message || 'Failed to update order status'
    notification.error(message)
  }
}

const filteredOrders = computed(() => {
  if (selectedFilter.value === 'all') return orders.value
  return orders.value.filter((o) => o.status === selectedFilter.value)
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getOrderStatusClass = (status: string) => {
  switch (status) {
    case 'pending':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200/50'
    case 'processing':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200/50'
    case 'shipped':
      return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 border-indigo-200/50'
    case 'delivered':
      return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200/50'
    case 'cancelled':
      return 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400 border-rose-200/50'
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400 border-gray-200/50'
  }
}

onMounted(loadOrders)
</script>

<template>
  <DashboardLayout>
    <!-- Page Header -->
    <div class="mb-12">
      <div class="flex items-center gap-3 mb-2">
        <span
          class="px-3 py-1 rounded-full bg-violet-50 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 text-[10px] font-black uppercase tracking-widest border border-violet-100 dark:border-violet-500/20"
        >
          Pharmacist Portal
        </span>
      </div>
      <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">
        Pharmacy Order Management
      </h1>
      <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
        Track customer orders, process dispatches, and complete pharmacy deliveries.
      </p>
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

    <!-- Main Content Section -->
    <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-10 shadow-premium flex flex-col">
      <!-- Dashboard Header & Tabs -->
      <div class="flex flex-col lg:flex-row items-center justify-between gap-6 border-b border-gray-100 dark:border-slate-800 pb-6 mb-8">
        <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
          <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
          All Orders Catalog
        </h3>

        <div class="flex items-center gap-2 overflow-x-auto w-full lg:w-auto pb-2 scrollbar-none">
          <button
            v-for="status in [
              'all',
              'pending',
              'processing',
              'shipped',
              'delivered',
              'cancelled',
            ]"
            :key="status"
            @click="selectedFilter = status"
            :class="`px-4 py-2 text-xs font-black rounded-full uppercase tracking-wider transition-all border ${
              selectedFilter === status
                ? 'bg-emerald-600 text-white border-emerald-600 shadow-lg shadow-emerald-500/15'
                : 'bg-white dark:bg-slate-900 border-gray-100 dark:border-slate-800 text-gray-500 dark:text-slate-400 hover:border-emerald-500/20'
            }`"
          >
            {{ status }}
          </button>
        </div>
      </div>

      <div v-if="isLoading" class="flex justify-center py-20">
        <div
          class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
        ></div>
      </div>

      <div
        v-else-if="filteredOrders.length === 0"
        class="flex flex-col items-center justify-center py-20 bg-gray-50/50 dark:bg-slate-800/30 rounded-[2.5rem] border-2 border-dashed border-gray-100 dark:border-slate-800 text-center"
      >
        <p class="text-gray-400 dark:text-slate-500 font-bold">
          No orders found in this status category.
        </p>
      </div>

      <!-- Orders List -->
      <div v-else class="space-y-6">
        <div
          v-for="order in filteredOrders"
          :key="order.id"
          class="glass p-6 rounded-[2rem] border border-gray-100 dark:border-slate-800 shadow-premium group hover:border-emerald-500/10 transition-all duration-300"
        >
          <div
            class="flex items-start justify-between flex-wrap gap-4 border-b border-gray-100 dark:border-slate-800 pb-4 mb-4"
          >
            <div>
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                Order ID
              </p>
              <h4 class="text-sm font-black text-gray-900 dark:text-white mt-0.5 font-mono">
                {{ order.id }}
              </h4>
            </div>
            <div class="text-right">
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                Order Date
              </p>
              <p class="text-xs text-gray-700 dark:text-slate-300 font-bold mt-0.5">
                {{ formatDate(order.order_date) }}
              </p>
            </div>
          </div>

          <!-- Customer and Delivery Details -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6 text-xs">
            <div>
              <h5 class="font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-2">
                Customer Info
              </h5>
              <p class="text-gray-900 dark:text-white font-black">
                Placed By:
                <span class="font-medium text-gray-600 dark:text-slate-300 ml-1">{{
                  order.user_name
                }}</span>
              </p>
              <p v-if="order.patient_name" class="text-gray-900 dark:text-white font-black mt-1">
                Patient Mapping:
                <span class="font-medium text-gray-600 dark:text-slate-300 ml-1">{{
                  order.patient_name
                }}</span>
              </p>
              <p class="text-gray-900 dark:text-white font-black mt-1">
                Contact:
                <span class="font-medium text-gray-600 dark:text-slate-300 ml-1">{{
                  order.phone_number
                }}</span>
              </p>
            </div>
            <div>
              <h5 class="font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-2">
                Delivery Details
              </h5>
              <p class="text-gray-900 dark:text-white font-medium">
                {{ order.shipping_address }}
              </p>
            </div>
          </div>

          <!-- Items -->
          <div
            class="bg-gray-50/50 dark:bg-slate-800/40 p-4 rounded-2xl border border-gray-100 dark:border-slate-700/50 space-y-3 mb-6"
          >
            <h5 class="text-[9px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-2">
              Cart Prescription Items
            </h5>
            <div
              v-for="item in order.items"
              :key="item.id"
              class="flex items-center justify-between text-xs"
            >
              <p class="text-gray-600 dark:text-slate-400 font-medium">
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

          <!-- Total and Actions Row -->
          <div
            class="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-slate-800 flex-wrap gap-6"
          >
            <div class="flex items-center gap-4">
              <span
                :class="`px-3.5 py-1.5 rounded-full text-[10px] font-black uppercase border tracking-widest ${getOrderStatusClass(order.status)}`"
              >
                {{ order.status }}
              </span>
              <p
                class="text-2xl font-black text-emerald-600 dark:text-emerald-400 tracking-tight"
              >
                ${{ Number(order.total_price).toFixed(2) }}
              </p>
            </div>

            <!-- Pharmacist Workflow Actions -->
            <div
              v-if="order.status !== 'cancelled' && order.status !== 'delivered'"
              class="flex gap-2 flex-wrap"
            >
              <button
                v-if="order.status === 'pending'"
                @click="updateStatus(order.id, 'processing')"
                class="px-4 py-2.5 bg-blue-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-blue-700 shadow-md shadow-blue-500/10 transition-all active:scale-95"
              >
                Start Processing
              </button>
              <button
                v-if="order.status === 'processing'"
                @click="updateStatus(order.id, 'shipped')"
                class="px-4 py-2.5 bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-indigo-700 shadow-md shadow-indigo-500/10 transition-all active:scale-95"
              >
                Mark as Shipped
              </button>
              <button
                v-if="order.status === 'shipped'"
                @click="updateStatus(order.id, 'delivered')"
                class="px-4 py-2.5 bg-emerald-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 shadow-md shadow-emerald-500/10 transition-all active:scale-95"
              >
                Complete Delivery
              </button>
              <button
                @click="updateStatus(order.id, 'cancelled')"
                class="px-4 py-2.5 bg-rose-50 text-rose-600 text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-rose-650 hover:text-white border border-rose-100 dark:border-rose-900/30 transition-all active:scale-95"
              >
                Cancel Order
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
