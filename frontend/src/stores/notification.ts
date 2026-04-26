import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: number
  message: string
  type: ToastType
  timeout?: number
}

export const useNotificationStore = defineStore('notification', () => {
  const toasts = ref<Toast[]>([])
  let nextId = 0

  const addToast = (message: string, type: ToastType = 'info', timeout = 5000) => {
    const id = nextId++
    toasts.value.push({ id, message, type, timeout })

    if (timeout > 0) {
      setTimeout(() => {
        removeToast(id)
      }, timeout)
    }
  }

  const removeToast = (id: number) => {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  return {
    toasts,
    addToast,
    removeToast,
    success: (msg: string) => addToast(msg, 'success'),
    error: (msg: string) => addToast(msg, 'error'),
    warning: (msg: string) => addToast(msg, 'warning'),
    info: (msg: string) => addToast(msg, 'info'),
  }
})
