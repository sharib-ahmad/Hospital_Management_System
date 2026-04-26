import { defineStore } from 'pinia'
import { ref, watch, onMounted } from 'vue'

export type Theme = 'light' | 'dark' | 'system'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'system')

  const applyTheme = (newTheme: Theme) => {
    const root = window.document.documentElement

    let isDark = false
    if (newTheme === 'system') {
      isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    } else {
      isDark = newTheme === 'dark'
    }

    if (isDark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }

    localStorage.setItem('theme', newTheme)
  }

  // Watch for changes and apply
  watch(theme, (newTheme) => {
    applyTheme(newTheme)
  })

  // Listen for system theme changes
  onMounted(() => {
    applyTheme(theme.value)

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (theme.value === 'system') {
        applyTheme('system')
      }
    })
  })

  const toggleTheme = () => {
    if (theme.value === 'light') theme.value = 'dark'
    else if (theme.value === 'dark') theme.value = 'system'
    else theme.value = 'light'
  }

  return {
    theme,
    toggleTheme,
    applyTheme,
  }
})
