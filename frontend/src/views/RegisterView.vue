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
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white transition-colors">
        Create an account
      </h2>
      <p class="text-sm text-gray-600 dark:text-slate-400 mt-1 transition-colors">
        Join MediFlow and start managing your health digitally.
      </p>
    </div>

    <form @submit.prevent="handleRegister" class="space-y-1">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-4">
        <FormField
          id="full_name"
          v-model="formData.full_name"
          label="Full Name"
          placeholder="John Doe"
          :error="errors.full_name"
          required
        />
        <FormField
          id="username"
          v-model="formData.username"
          label="Username"
          placeholder="johndoe123"
          :error="errors.username"
          required
        />
      </div>

      <FormField
        id="email"
        v-model="formData.email"
        type="email"
        label="Email Address"
        placeholder="john@example.com"
        :error="errors.email"
        required
      />

      <FormField
        id="phone_number"
        v-model="formData.phone_number"
        type="tel"
        label="Phone Number"
        placeholder="+1 (555) 000-0000"
        :error="errors.phone_number"
        required
      />

      <FormField
        id="address"
        v-model="formData.address"
        label="Address"
        placeholder="123 Main St, City"
        :error="errors.address"
        required
      />

      <FormField
        id="pincode"
        v-model="formData.pincode"
        label="Pincode"
        placeholder="123456"
        :error="errors.pincode"
        required
      />

      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-4">
        <FormField
          id="password"
          v-model="formData.password"
          type="password"
          label="Password"
          placeholder="••••••••"
          :error="errors.password"
          required
          autocomplete="new-password"
        />
        <FormField
          id="confirm_password"
          v-model="formData.confirm_password"
          type="password"
          label="Confirm Password"
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
          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-slate-600 rounded bg-white dark:bg-slate-700"
        />
        <label
          for="terms"
          class="ml-2 block text-sm text-gray-700 dark:text-slate-400 transition-colors"
        >
          I agree to the
          <a
            href="#"
            class="text-blue-600 dark:text-blue-400 font-bold hover:text-blue-500 transition-colors"
            >Terms</a
          >
          and
          <a
            href="#"
            class="text-blue-600 dark:text-blue-400 font-bold hover:text-blue-500 transition-colors"
            >Privacy Policy</a
          >
        </label>
      </div>

      <div class="pt-2">
        <button
          :disabled="isLoading"
          type="submit"
          class="w-full flex justify-center py-3.5 px-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all active:scale-95 disabled:opacity-70 disabled:active:scale-100"
        >
          <svg
            v-if="isLoading"
            class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
          {{ isLoading ? 'Creating account...' : 'Create account' }}
        </button>
      </div>
    </form>

    <div class="mt-8 text-center border-t border-gray-100 dark:border-slate-700 pt-6">
      <p class="text-sm text-gray-600 dark:text-slate-400 transition-colors">
        Already have an account?
        <router-link
          :to="{ name: 'login' }"
          class="font-bold text-blue-600 dark:text-blue-400 hover:text-blue-500 transition-colors"
          >Sign in instead</router-link
        >
      </p>
    </div>
  </AuthLayout>
</template>
