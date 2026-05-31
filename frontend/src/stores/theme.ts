import { defineStore } from 'pinia'
import { ref, watch, onMounted } from 'vue'

export type Theme = 'system' | 'opposite'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'system')
  const isDark = ref(false)

  const applyTheme = (newTheme: Theme) => {
    const root = window.document.documentElement
    const systemIsDark = window.matchMedia('(prefers-color-scheme: dark)').matches

    isDark.value = newTheme === 'system' ? systemIsDark : !systemIsDark

    if (isDark.value) {
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

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', () => {
      applyTheme(theme.value)
    })
  })

  const toggleTheme = () => {
    theme.value = theme.value === 'system' ? 'opposite' : 'system'
  }

  return {
    theme,
    isDark,
    toggleTheme,
    applyTheme,
  }
})
