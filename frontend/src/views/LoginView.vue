<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '../layouts/AuthLayout.vue'
import FormField from '../components/FormField.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const errors = ref({
  username: '',
  password: '',
})
const isLoading = ref(false)

const validate = () => {
  let isValid = true
  errors.value = { username: '', password: '' }

  if (!username.value) {
    errors.value.username = 'Username is required'
    isValid = false
  } else if (username.value.length < 5) {
    errors.value.username = 'Username must be at least 5 characters'
    isValid = false
  }

  if (!password.value) {
    errors.value.password = 'Password is required'
    isValid = false
  }

  return isValid
}

const handleLogin = async () => {
  if (!validate()) return

  isLoading.value = true
  const success = await auth.login({
    username: username.value,
    password: password.value,
  })

  if (success) {
    router.push({ name: `${auth.user?.role}-portal` })
  }
  isLoading.value = false
}
</script>

<template>
  <AuthLayout>
    <div class="mb-10">
      <h2 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight leading-none">
        Welcome Back
      </h2>
      <p class="text-sm text-gray-500 dark:text-slate-400 mt-2 font-medium">
        Enter your credentials to access the workspace.
      </p>
    </div>

    <form @submit.prevent="handleLogin" class="space-y-4">
      <FormField
        id="username"
        v-model="username"
        label="User Handle"
        placeholder="e.g. johndoe_md"
        :error="errors.username"
        required
        autocomplete="username"
      />

      <FormField
        id="password"
        v-model="password"
        label="Secure Password"
        type="password"
        placeholder="••••••••"
        :error="errors.password"
        required
        autocomplete="current-password"
      >
        <template #label-right>
          <a
            href="#"
            class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 uppercase tracking-widest transition-colors"
          >
            Reset?
          </a>
        </template>
      </FormField>

      <div class="flex items-center pb-2">
        <input
          id="remember-me"
          name="remember-me"
          type="checkbox"
          class="h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 dark:border-slate-600 rounded bg-white dark:bg-slate-700"
        />
        <label
          for="remember-me"
          class="ml-2 block text-xs font-bold text-gray-500 dark:text-slate-400 uppercase tracking-widest transition-colors"
        >
          Remember session
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
          {{ isLoading ? 'Authenticating...' : 'Authorize Session' }}
        </button>
      </div>
    </form>

    <div class="mt-10 text-center border-t border-gray-100 dark:border-white/5 pt-8">
      <p class="text-xs font-bold text-gray-500 dark:text-slate-400 transition-colors uppercase tracking-widest">
        New to MediFlow?
        <router-link
          :to="{ name: 'register' }"
          class="font-black text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 transition-colors"
          >Create Identity</router-link
        >
      </p>
    </div>
  </AuthLayout>
</template>
