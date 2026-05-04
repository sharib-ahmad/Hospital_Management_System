<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '../layouts/AuthLayout.vue'
import FormField from '../components/FormField.vue'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'

const auth = useAuthStore()
const notification = useNotificationStore()
const router = useRouter()

const formData = ref({
  username: '',
  full_name: '',
  email: '',
  password: '',
  confirm_password: '',
  address: '',
  phone_number: '',
  pincode: '',
})

const isLoading = ref(false)

const errors = ref({
  username: '',
  full_name: '',
  email: '',
  password: '',
  confirm_password: '',
  address: '',
  phone_number: '',
  pincode: '',
})

const validate = () => {
  let isValid = true
  errors.value = {
    username: '',
    full_name: '',
    email: '',
    password: '',
    confirm_password: '',
    address: '',
    phone_number: '',
    pincode: '',
  }

  if (formData.value.username.length < 5) {
    errors.value.username = 'Username must be at least 5 characters'
    isValid = false
  }

  if (formData.value.full_name.length < 3) {
    errors.value.full_name = 'Full name must be at least 3 characters'
    isValid = false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.value.email)) {
    errors.value.email = 'Please enter a valid email address'
    isValid = false
  }

  if (formData.value.password.length < 6) {
    errors.value.password = 'Password must be at least 6 characters'
    isValid = false
  }

  if (formData.value.password !== formData.value.confirm_password) {
    errors.value.confirm_password = 'Passwords do not match'
    isValid = false
  }

  if (!formData.value.phone_number) {
    errors.value.phone_number = 'Phone number is required'
    isValid = false
  }

  return isValid
}

const handleRegister = async () => {
  if (!validate()) return

  isLoading.value = true

  // Create a copy of the data without confirm_password
  const { confirm_password, ...submitData } = formData.value

  const success = await auth.register(submitData)

  if (success) {
    router.push({ name: 'login' })
  }
  isLoading.value = false
}
</script>

<template>
  <AuthLayout>
    <div class="mb-10">
      <h2 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight leading-none">
        Join the Network
      </h2>
      <p class="text-sm text-gray-500 dark:text-slate-400 mt-2 font-medium transition-colors">
        Create your digital identity and start managing healthcare seamlessly.
      </p>
    </div>

    <form @submit.prevent="handleRegister" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          id="full_name"
          v-model="formData.full_name"
          label="Display Name"
          placeholder="John Doe"
          :error="errors.full_name"
          required
        />
        <FormField
          id="username"
          v-model="formData.username"
          label="Unique Handle"
          placeholder="johndoe123"
          :error="errors.username"
          required
        />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          id="email"
          v-model="formData.email"
          type="email"
          label="Email Address"
          placeholder="john@hospital.com"
          :error="errors.email"
          required
        />
        <FormField
          id="phone_number"
          v-model="formData.phone_number"
          type="tel"
          label="Contact Number"
          placeholder="+1 (555) 000-0000"
          :error="errors.phone_number"
          required
        />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          id="address"
          v-model="formData.address"
          label="Residential City"
          placeholder="New York, NY"
          :error="errors.address"
          required
        />
        <FormField
          id="pincode"
          v-model="formData.pincode"
          label="Postal Code"
          placeholder="10001"
          :error="errors.pincode"
          required
        />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          id="password"
          v-model="formData.password"
          type="password"
          label="New Password"
          placeholder="••••••••"
          :error="errors.password"
          required
          autocomplete="new-password"
        />
        <FormField
          id="confirm_password"
          v-model="formData.confirm_password"
          type="password"
          label="Confirm Selection"
          placeholder="••••••••"
          :error="errors.confirm_password"
          required
          autocomplete="new-password"
        />
      </div>

      <div class="flex items-center py-2">
        <input
          id="terms"
          type="checkbox"
          required
          class="h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 dark:border-slate-600 rounded bg-white dark:bg-slate-700"
        />
        <label
          for="terms"
          class="ml-2 block text-xs font-bold text-gray-500 dark:text-slate-400 transition-colors uppercase tracking-widest"
        >
          I accept the
          <a
            href="#"
            class="text-emerald-600 dark:text-emerald-400 font-black hover:text-emerald-500 transition-colors"
            >Agreement</a
          >
          and
          <a
            href="#"
            class="text-emerald-600 dark:text-emerald-400 font-black hover:text-emerald-500 transition-colors"
            >Privacy</a
          >
        </label>
      </div>

      <div class="pt-2">
        <button
          :disabled="isLoading"
          type="submit"
          class="w-full flex justify-center py-4 px-4 border border-transparent rounded-2xl shadow-xl shadow-emerald-500/20 text-xs font-black uppercase tracking-[0.2em] text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-4 focus:ring-emerald-500/20 transition-all active:scale-95 disabled:opacity-70 disabled:active:scale-100"
        >
          <svg
            v-if="isLoading"
            class="animate-spin -ml-1 mr-3 h-4 w-4 text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          {{ isLoading ? 'Initializing...' : 'Confirm Registration' }}
        </button>
      </div>
    </form>

    <div class="mt-10 text-center border-t border-gray-100 dark:border-white/5 pt-8">
      <p class="text-xs font-bold text-gray-500 dark:text-slate-400 transition-colors uppercase tracking-widest">
        Already have an identity?
        <router-link
          :to="{ name: 'login' }"
          class="font-black text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 transition-colors"
          >Sign In</router-link
        >
      </p>
    </div>
  </AuthLayout>
</template>
