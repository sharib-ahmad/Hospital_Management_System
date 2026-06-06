import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const instance = axios.create({
  baseURL: '/api',
  withCredentials: true, // Critical for sending/receiving cookies
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRefreshing = false
let failedQueue: any[] = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })

  failedQueue = []
}

// Request interceptor
instance.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken && !config.url?.includes('/auth/refresh')) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response interceptor
instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()

    // Parse and enhance backend validation errors
    if (error.response && error.response.data) {
      const data = error.response.data
      if (data.errors && Array.isArray(data.errors) && data.errors.length > 0) {
        // Format backend validation errors into a single readable string
        const formattedErrors = data.errors
          .map((err: any) => {
            const location = err.loc && err.loc.length > 0 ? err.loc.join('.') : 'Field'
            return `${location}: ${err.msg}`
          })
          .join(' | ')

        // Override the default message with the detailed one
        error.response.data.message = `${data.message ? data.message + ' - ' : ''}${formattedErrors}`
      }
    }

    // If error is 401 and we haven't retried yet
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest._isRetry &&
      !originalRequest.url?.includes('/auth/login')
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return instance(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const newToken = await authStore.refreshAccessToken()
        if (newToken) {
          processQueue(null, newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return instance(originalRequest)
        }
      } catch (refreshError) {
        processQueue(refreshError, null)
        authStore.logout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)

export default instance
