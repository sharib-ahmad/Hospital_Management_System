import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useNotificationStore } from './notification'
import api from '../utils/axios'

interface User {
  id: string
  username: string
  email: string
  role: string
}

export const useAuthStore = defineStore('auth', () => {
  const notification = useNotificationStore()

  // Tokens are now mostly in cookies, but we keep accessToken in memory for the Bearer header
  const accessToken = ref('')
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(
    () => !!accessToken.value || !!localStorage.getItem('is_logged_in'),
  )

  async function login(credentials: any) {
    try {
      const response = await api.post('/auth/login', credentials)
      const result = response.data

      accessToken.value = result.data.access_token
      user.value = result.data.user

      // We still save user info in localStorage for persistence across reloads
      // but NOT the sensitive tokens.
      // We use a flag 'is_logged_in' to know we should try a silent refresh on reload.
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('is_logged_in', 'true')

      notification.success('Welcome back, ' + user.value?.username)
      return true
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'Login failed'
      notification.error(message)
      return false
    }
  }

  async function register(userData: any) {
    try {
      await api.post('/auth/register', userData)
      notification.success('Registration successful! Please login.')
      return true
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'Registration failed'
      notification.error(message)
      return false
    }
  }

  async function refreshAccessToken() {
    try {
      // The refresh token is sent automatically by the browser via HttpOnly cookie
      const response = await api.post('/auth/refresh', {}, {
        _isRetry: true, // Custom flag for interceptor
      } as any)

      accessToken.value = response.data.data.access_token
      return accessToken.value
    } catch (err) {
      logout()
      return null
    }
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch (e) {
      console.error('Logout failed on server', e)
    } finally {
      accessToken.value = ''
      user.value = null
      localStorage.removeItem('user')
      localStorage.removeItem('is_logged_in')
      notification.info('Logged out successfully')
    }
  }

  return {
    accessToken,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    refreshAccessToken,
  }
})
