import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Try to refresh token on app start if they were logged in
const authStore = useAuthStore()
if (localStorage.getItem('is_logged_in')) {
  authStore.refreshAccessToken()
}

app.mount('#app')
