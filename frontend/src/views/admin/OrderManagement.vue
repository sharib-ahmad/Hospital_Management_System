<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import PortalBase from '../portals/PortalBase.vue'
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
  <PortalBase role="admin" title="Pharmacy Order Management" :stats="stats">
    <template #main>
      <div class="space-y-8">
        <!-- Dashboard Header & Tabs -->
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3">
            <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
            All Orders Catalog
          </h3>

          <div class="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 scrollbar-none">
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
                  ? 'bg-emerald-600 text-white border-emerald-600 shadow-lg'
                  : 'bg-white dark:bg-slate-900 border-gray-100 dark:border-slate-800 text-gray-550 dark:text-slate-400 hover:border-emerald-500/20'
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

        <!-- Orders Grid -->
        <div v-else class="space-y-6">
          <div
            v-for="order in filteredOrders"
            :key="order.id"
            class="glass p-6 rounded-[2rem] border border-white/40 dark:border-white/5 shadow-premium group"
          >
            <div
              class="flex items-start justify-between flex-wrap gap-4 border-b border-gray-100 dark:border-slate-800 pb-4 mb-4"
            >
              <div>
                <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  Order ID
                </p>
                <h4 class="text-sm font-black text-gray-900 dark:text-white mt-0.5">
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
                <h5 class="font-black text-gray-400 uppercase tracking-widest mb-2">
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
                <h5 class="font-black text-gray-400 uppercase tracking-widest mb-2">
                  Delivery Details
                </h5>
                <p class="text-gray-900 dark:text-white font-medium">
                  {{ order.shipping_address }}
                </p>
              </div>
            </div>

            <!-- Items -->
            <div
              class="bg-gray-50/50 dark:bg-slate-800 p-4 rounded-2xl border border-gray-100 dark:border-slate-800 space-y-3 mb-6"
            >
              <h5 class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-2">
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

              <!-- Admin Workflow Actions -->
              <div
                v-if="order.status !== 'cancelled' && order.status !== 'delivered'"
                class="flex gap-2 flex-wrap"
              >
                <button
                  v-if="order.status === 'pending'"
                  @click="updateStatus(order.id, 'processing')"
                  class="px-4 py-2.5 bg-blue-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-blue-700 shadow-md shadow-blue-500/10 transition-all"
                >
                  Start Processing
                </button>
                <button
                  v-if="order.status === 'processing'"
                  @click="updateStatus(order.id, 'shipped')"
                  class="px-4 py-2.5 bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-indigo-700 shadow-md shadow-indigo-500/10 transition-all"
                >
                  Mark as Shipped
                </button>
                <button
                  v-if="order.status === 'shipped'"
                  @click="updateStatus(order.id, 'delivered')"
                  class="px-4 py-2.5 bg-emerald-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 shadow-md shadow-emerald-500/10 transition-all"
                >
                  Complete Delivery
                </button>
                <button
                  @click="updateStatus(order.id, 'cancelled')"
                  class="px-4 py-2.5 bg-rose-50 text-rose-600 text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-rose-600 hover:text-white border border-rose-100 dark:border-rose-900/30 transition-all"
                >
                  Cancel Order
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #sidebar>
      <div
        class="bg-gradient-to-br from-emerald-600 to-teal-700 rounded-[2.5rem] p-8 text-white shadow-xl shadow-emerald-500/30"
      >
        <h3 class="text-xl font-black mb-4 tracking-tight">Staff Helpdesk</h3>
        <p class="text-emerald-50 text-sm mb-6 font-medium leading-relaxed opacity-95">
          As a pharmacy administrator or nurse staff, you can review prescription orders and
          coordinate dispatches to the patient address.
        </p>
        <div class="border-t border-white/20 pt-6 text-xs space-y-2 opacity-80">
          <p>• Pending orders must be validated before processing.</p>
          <p>• Inventory decrementing is handled automatically.</p>
          <p>• Confirm package details before marking as Shipped.</p>
        </div>
      </div>
    </template>
  </PortalBase>
</template>
