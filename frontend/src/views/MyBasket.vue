<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import FormField from '../components/FormField.vue'
import api from '../utils/axios'
import { useNotificationStore } from '../stores/notification'
import { useCartStore } from '../stores/cart'

const router = useRouter()
const notification = useNotificationStore()
const cartStore = useCartStore()

// State
const myPatients = ref<any[]>([])
const isLoading = ref(true)
const isSubmitting = ref(false)

// Checkout Form
const selectedPatientId = ref('')
const shippingAddress = ref('')
const phone_number = ref('')
const formErrors = ref({
  phone_number: '',
  shipping_address: '',
})

// Shopping Cart (computed from Pinia store)
const cart = computed(() => cartStore.items)
const cartTotal = computed(() => cartStore.cartTotal)
const cartCount = computed(() => cartStore.cartCount)

// Load Data
const loadData = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/patients/my')
    myPatients.value = res.data.data || []
  } catch (error) {
    notification.error('Failed to load patient profiles')
  } finally {
    isLoading.value = false
  }
}

// Cart operations mapped to Pinia store actions
const updateCartQuantity = (medicineId: string, quantity: number, maxStock: number) => {
  cartStore.updateQuantity(medicineId, quantity, maxStock)
}

const removeFromCart = (medicineId: string, name: string) => {
  cartStore.removeFromCart(medicineId, name)
}

// Validation
const validateForm = () => {
  let valid = true
  formErrors.value = { phone_number: '', shipping_address: '' }

  if (!phone_number.value.trim()) {
    formErrors.value.phone_number = 'Contact phone number is required.'
    valid = false
  }
  if (!shippingAddress.value.trim()) {
    formErrors.value.shipping_address = 'Shipping address is required.'
    valid = false
  }
  return valid
}

// Checkout Order
const handleCheckout = async () => {
  if (cart.value.length === 0) {
    notification.error('Your basket is empty')
    return
  }
  if (!validateForm()) return

  isSubmitting.value = true
  try {
    const payload = {
      patient_id: selectedPatientId.value || null,
      shipping_address: shippingAddress.value,
      phone_number: phone_number.value,
      items: cart.value.map((item) => ({
        medicine_id: item.medicine.id,
        quantity: item.quantity,
      })),
    }
    await api.post('/medistore/orders', payload)
    notification.success('Pharmacy order checked out successfully!')
    cartStore.clearCart()
    shippingAddress.value = ''
    phone_number.value = ''
    selectedPatientId.value = ''
    // Redirect to orders tab in store page
    router.push({ path: '/store' })
  } catch (error: any) {
    const message = error.response?.data?.message || 'Checkout failed'
    notification.error(message)
  } finally {
    isSubmitting.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <DashboardLayout>
    <!-- Page Header -->
    <div class="mb-12">
      <div class="flex items-center gap-3 mb-2">
        <span
          class="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest border border-emerald-100 dark:border-emerald-500/20"
        >
          Checkout
        </span>
      </div>
      <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">My Basket</h1>
      <p class="text-gray-500 dark:text-slate-400 mt-2 font-medium">
        Review pharmacy items in your basket and complete your order.
      </p>
    </div>

    <!-- Main Layout -->
    <div v-if="isLoading" class="flex justify-center items-center py-32">
      <div
        class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
      ></div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="cart.length === 0"
      class="flex flex-col items-center justify-center py-24 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 text-center px-6 shadow-premium hover:-translate-y-1 transition-all duration-300"
    >
      <div
        class="w-20 h-20 bg-emerald-50 dark:bg-emerald-900/30 rounded-3xl shadow-premium flex items-center justify-center mb-6 text-emerald-600"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-10 w-10"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
          />
        </svg>
      </div>
      <h3 class="text-xl font-black text-gray-900 dark:text-white mb-2">
        Your basket is empty
      </h3>
      <p class="text-gray-500 dark:text-slate-400 text-sm max-w-xs font-medium mb-8">
        Add medicines from the MediStore pharmacy catalog first.
      </p>
      <RouterLink
        to="/store"
        class="px-8 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/20 hover:-translate-y-0.5 transition-all uppercase text-xs tracking-widest active:scale-95"
      >
        Browse Medicines
      </RouterLink>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left Column: Basket Items -->
      <div
        class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-10 shadow-premium hover:-translate-y-1 transition-all duration-300"
      >
        <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3 mb-8">
          <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
          Selected Medicines ({{ cartCount }})
        </h3>

        <div class="space-y-6">
          <div
            v-for="item in cart"
            :key="item.medicine.id"
            class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 bg-gray-50 dark:bg-slate-800/40 rounded-2xl border border-gray-100 dark:border-slate-700/50"
          >
            <!-- Details -->
            <div class="flex-1 min-w-0">
              <span
                class="px-2 py-0.5 bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 text-[9px] font-black uppercase tracking-wider rounded border border-emerald-100/50 dark:border-emerald-500/10"
              >
                {{ item.medicine.category }}
              </span>
              <h4 class="font-black text-gray-900 dark:text-white text-base mt-2 truncate">
                {{ item.medicine.name }}
              </h4>
              <p class="text-xs text-gray-500 dark:text-slate-400 font-medium mt-1">
                Price: ${{ item.medicine.price.toFixed(2) }} each
              </p>
            </div>

            <!-- Controls -->
            <div class="flex items-center gap-4 shrink-0 justify-between sm:justify-start">
              <div class="flex items-center gap-2">
                <button
                  type="button"
                  @click="updateCartQuantity(item.medicine.id, item.quantity - 1, item.medicine.stock)"
                  class="w-8 h-8 rounded-xl bg-white dark:bg-slate-850 flex items-center justify-center font-bold text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-200 border border-gray-200 dark:border-slate-700 text-sm shadow-sm transition-all active:scale-90"
                >
                  -
                </button>
                <span class="text-sm font-black text-gray-950 dark:text-white w-8 text-center">
                  {{ item.quantity }}
                </span>
                <button
                  type="button"
                  @click="updateCartQuantity(item.medicine.id, item.quantity + 1, item.medicine.stock)"
                  class="w-8 h-8 rounded-xl bg-white dark:bg-slate-850 flex items-center justify-center font-bold text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-200 border border-gray-200 dark:border-slate-700 text-sm shadow-sm transition-all active:scale-90"
                >
                  +
                </button>
              </div>

              <div class="text-right sm:w-20">
                <p class="text-sm font-black text-gray-900 dark:text-white">
                  ${{ (item.medicine.price * item.quantity).toFixed(2) }}
                </p>
              </div>

              <button
                type="button"
                @click="removeFromCart(item.medicine.id, item.medicine.name)"
                class="p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20 border border-transparent hover:border-rose-100 dark:hover:border-rose-950/30 rounded-xl transition-all"
                title="Remove item"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div class="mt-8 pt-6 border-t border-gray-100 dark:border-slate-800 flex justify-between items-center">
          <span class="text-sm font-black text-gray-400 uppercase tracking-wider">Subtotal</span>
          <span class="text-3xl font-black text-emerald-600 dark:text-emerald-400 tracking-tight">
            ${{ cartTotal.toFixed(2) }}
          </span>
        </div>
      </div>

      <!-- Right Column: Shipping & Checkout Form -->
      <div
        class="lg:col-span-1 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-8 shadow-premium hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between"
      >
        <div>
          <h3 class="text-xl font-black text-gray-900 dark:text-white flex items-center gap-3 mb-8">
            <span class="h-1.5 w-6 bg-emerald-600 rounded-full"></span>
            Shipping details
          </h3>

          <form @submit.prevent="handleCheckout" class="space-y-6">
            <!-- For Patient (Optional) -->
            <div class="w-full space-y-1.5">
              <label class="block text-sm font-bold text-gray-600 dark:text-slate-400">
                For Patient Profile <span class="text-gray-400 text-xs">(Optional)</span>
              </label>
              <select
                v-model="selectedPatientId"
                class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
              >
                <option value="">Order for General Use</option>
                <option v-for="pat in myPatients" :key="pat.id" :value="pat.id">
                  {{ pat.full_name }} ({{ pat.relation }})
                </option>
              </select>
            </div>

            <!-- Phone Number -->
            <FormField
              id="phone_number"
              label="Contact Phone"
              placeholder="e.g. +1-555-0199"
              v-model="phone_number"
              :error="formErrors.phone_number"
              required
            />

            <!-- Shipping Address -->
            <FormField
              id="shipping_address"
              label="Shipping Address"
              placeholder="Street Address, City, Zip Code"
              v-model="shippingAddress"
              :error="formErrors.shipping_address"
              required
            />

            <!-- Confirm Button -->
            <button
              type="submit"
              :disabled="isSubmitting"
              class="w-full py-4 bg-emerald-600 text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-lg shadow-emerald-500/20 hover:bg-emerald-700 disabled:opacity-60 transition-all flex items-center justify-center gap-2 active:scale-95"
            >
              <div
                v-if="isSubmitting"
                class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"
              ></div>
              {{ isSubmitting ? 'Placing Order...' : 'Confirm Checkout' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
