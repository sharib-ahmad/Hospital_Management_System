<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '../layouts/AuthLayout.vue'
import FormField from '../components/FormField.vue'
import { useAuthStore } from '../stores/auth'
import api from '../utils/axios'
import { useNotificationStore } from '../stores/notification'

const auth = useAuthStore()
const router = useRouter()
const notification = useNotificationStore()

const username = ref('')
const password = ref('')
const errors = ref({
  username: '',
  password: '',
})
const isLoading = ref(false)

// Reset Password Modal State
const showResetModal = ref(false)
const isResetting = ref(false)
const resetForm = ref({
  username: '',
  email: '',
  newPassword: '',
})
const resetErrors = ref({
  username: '',
  email: '',
  newPassword: '',
})

const openResetModal = () => {
  resetForm.value = { username: '', email: '', newPassword: '' }
  resetErrors.value = { username: '', email: '', newPassword: '' }
  showResetModal.value = true
}

const validateResetForm = () => {
  let isValid = true
  resetErrors.value = { username: '', email: '', newPassword: '' }

  if (!resetForm.value.username.trim()) {
    resetErrors.value.username = 'Username is required'
    isValid = false
  }
  if (!resetForm.value.email.trim()) {
    resetErrors.value.email = 'Email is required'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(resetForm.value.email)) {
    resetErrors.value.email = 'Enter a valid email address'
    isValid = false
  }
  if (!resetForm.value.newPassword) {
    resetErrors.value.newPassword = 'New password is required'
    isValid = false
  } else if (resetForm.value.newPassword.length < 6) {
    resetErrors.value.newPassword = 'Password must be at least 6 characters'
    isValid = false
  }

  return isValid
}

const handleResetPassword = async () => {
  if (!validateResetForm()) return

  isResetting.value = true
  try {
    const payload = {
      username: resetForm.value.username,
      email: resetForm.value.email,
      new_password: resetForm.value.newPassword,
    }
    await api.post('/auth/reset-password', payload)
    notification.success('Password reset successfully. You can now login.')
    showResetModal.value = false
  } catch (error: any) {
    const msg = error.response?.data?.message || 'Failed to reset password'
    notification.error(msg)
  } finally {
    isResetting.value = false
  }
}

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
            @click.prevent="openResetModal"
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
      <p
        class="text-xs font-bold text-gray-500 dark:text-slate-400 transition-colors uppercase tracking-widest"
      >
        New to MediFlow?
        <router-link
          :to="{ name: 'register' }"
          class="font-black text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 transition-colors"
          >Create Identity</router-link
        >
      </p>
    </div>
  </AuthLayout>

  <!-- Reset Password Modal -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="showResetModal"
        class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
        @click.self="showResetModal = false"
      >
        <Transition name="slide-up">
          <div
            v-if="showResetModal"
            class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-10 shadow-premium-xl overflow-y-auto max-h-[90vh]"
          >
            <!-- Modal Header -->
            <div class="flex items-center justify-between mb-8">
              <div>
                <h2 class="text-2xl font-black text-gray-900 dark:text-white">Reset Password</h2>
                <p class="text-sm text-gray-500 dark:text-slate-400 mt-1 font-medium">
                  Provide your username and registered email to secure a new password.
                </p>
              </div>
              <button
                @click="showResetModal = false"
                class="w-10 h-10 flex items-center justify-center rounded-2xl bg-gray-100 dark:bg-slate-800 text-gray-500 dark:text-slate-400 hover:bg-gray-200 dark:hover:bg-slate-700 transition-all"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Form -->
            <form @submit.prevent="handleResetPassword" class="space-y-5">
              <FormField
                id="reset-username"
                v-model="resetForm.username"
                label="User Handle"
                placeholder="e.g. johndoe_md"
                :error="resetErrors.username"
                required
              />

              <FormField
                id="reset-email"
                v-model="resetForm.email"
                label="Registered Email"
                type="email"
                placeholder="e.g. john@example.com"
                :error="resetErrors.email"
                required
              />

              <FormField
                id="reset-new-password"
                v-model="resetForm.newPassword"
                label="New Secure Password"
                type="password"
                placeholder="•••••••• (min 6 characters)"
                :error="resetErrors.newPassword"
                required
              />

              <!-- Action Buttons -->
              <div class="flex gap-4 pt-4">
                <button
                  type="button"
                  @click="showResetModal = false"
                  class="flex-1 py-3.5 rounded-2xl border border-gray-200 dark:border-slate-700 text-gray-700 dark:text-slate-300 text-[10px] font-black uppercase tracking-widest hover:bg-gray-50 dark:hover:bg-slate-800 transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="isResetting"
                  class="flex-1 py-3.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 active:scale-95"
                >
                  <div
                    v-if="isResetting"
                    class="animate-spin rounded-full h-4 w-4 border-[2px] border-white border-t-transparent"
                  ></div>
                  {{ isResetting ? 'Saving...' : 'Reset Password' }}
                </button>
              </div>
            </form>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}
</style>
