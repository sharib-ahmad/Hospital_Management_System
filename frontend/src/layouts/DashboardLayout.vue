<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import ThemeToggle from '../components/ThemeToggle.vue'
import api from '../utils/axios'

const auth = useAuthStore()
const cartStore = useCartStore()
const router = useRouter()
const isSidebarOpen = ref(false)

// Notifications state
const notifications = ref<any[]>([])
const isNotificationsOpen = ref(false)
const notificationContainer = ref<HTMLElement | null>(null)
let pollingInterval: any = null

const fetchNotifications = async () => {
  if (!auth.user) return
  try {
    const res = await api.get('/notifications')
    notifications.value = res.data.data || []
  } catch (err) {
    console.error('Failed to fetch notifications', err)
  }
}

const unreadCount = computed(() => {
  return notifications.value.filter((n: any) => !n.is_read).length
})

const toggleNotifications = () => {
  isNotificationsOpen.value = !isNotificationsOpen.value
  if (isNotificationsOpen.value) {
    fetchNotifications()
  }
}

const handleClickOutside = (event: MouseEvent) => {
  if (
    isNotificationsOpen.value &&
    notificationContainer.value &&
    !notificationContainer.value.contains(event.target as Node)
  ) {
    isNotificationsOpen.value = false
  }
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'billing':
      return `<svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/></svg>`
    case 'order':
      return `<svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>`
    case 'appointment':
      return `<svg class="w-4 h-4 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`
    case 'application':
      return `<svg class="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>`
    case 'vitals':
      return `<svg class="w-4 h-4 text-rose-600 dark:text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>`
    default:
      return `<svg class="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>`
  }
}

const getCategoryBgColor = (category: string) => {
  switch (category) {
    case 'billing':
      return 'bg-blue-50 dark:bg-blue-950/20 border-blue-100/50 dark:border-blue-900/10'
    case 'order':
      return 'bg-purple-50 dark:bg-purple-950/20 border-purple-100/50 dark:border-purple-900/10'
    case 'appointment':
      return 'bg-emerald-50 dark:bg-emerald-950/20 border-emerald-100/50 dark:border-emerald-900/10'
    case 'application':
      return 'bg-amber-50 dark:bg-amber-950/20 border-amber-100/50 dark:border-amber-900/10'
    case 'vitals':
      return 'bg-rose-50 dark:bg-rose-950/20 border-rose-100/50 dark:border-rose-900/10'
    default:
      return 'bg-gray-50 dark:bg-slate-800 border-gray-100/50 dark:border-slate-700/10'
  }
}

const markRead = async (id: number) => {
  try {
    await api.put(`/notifications/${id}/read`)
    const idx = notifications.value.findIndex((n: any) => n.id === id)
    if (idx !== -1) notifications.value[idx].is_read = true
  } catch (err) {
    console.error('Failed to mark notification read', err)
  }
}

const markAllRead = async () => {
  try {
    await api.put('/notifications/read-all')
    notifications.value.forEach((n: any) => (n.is_read = true))
  } catch (err) {
    console.error('Failed to mark all notifications read', err)
  }
}

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'billing':
      return 'bg-blue-500'
    case 'order':
      return 'bg-purple-500'
    case 'appointment':
      return 'bg-emerald-500'
    case 'application':
      return 'bg-amber-500'
    case 'vitals':
      return 'bg-rose-500'
    default:
      return 'bg-gray-400'
  }
}

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'landing' })
}

const handleNavClick = () => {
  if (typeof window !== 'undefined' && window.innerWidth < 1024) {
    isSidebarOpen.value = false
  }
}

const handleResize = () => {
  if (window.innerWidth >= 1024) {
    isSidebarOpen.value = true
  } else {
    isSidebarOpen.value = false
  }
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
  document.addEventListener('click', handleClickOutside)
  if (auth.user) {
    fetchNotifications()
    pollingInterval = setInterval(fetchNotifications, 15000)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('click', handleClickOutside)
  if (pollingInterval) clearInterval(pollingInterval)
})

const navigation = {
  admin: [
    {
      name: 'Overview',
      href: '/admin',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    },
    {
      name: 'Users',
      href: '/admin/users',
      icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    },
    {
      name: 'Departments',
      href: '/admin/departments',
      icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    },
    {
      name: 'Applications',
      href: '/applications/management',
      icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    },
  ],
  doctor: [
    {
      name: 'Dashboard',
      href: '/doctor',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    },
    {
      name: 'Appointments',
      href: '/doctor/appointments',
      icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    },
    {
      name: 'Approve Patients',
      href: '/applications/management',
      icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    },
    {
      name: 'My Profile',
      href: '/doctor/profile',
      icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    },
  ],
  nurse: [
    {
      name: 'Dashboard',
      href: '/nurse',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    },
    {
      name: 'Patients',
      href: '/nurse/patients',
      icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    },
    {
      name: 'Approve Applications',
      href: '/applications/management',
      icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    },
    {
      name: 'My Profile',
      href: '/nurse/profile',
      icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    },
  ],
  pharmacist: [
    {
      name: 'Medicines',
      href: '/pharmacist/medicines',
      icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z',
    },
    {
      name: 'Orders',
      href: '/pharmacist/orders',
      icon: 'M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z',
    },
    {
      name: 'My Profile',
      href: '/pharmacist/profile',
      icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    },
  ],
  user: [
    {
      name: 'Welcome',
      href: '/user',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    },
    {
      name: 'Appointments',
      href: '/user/appointments',
      icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    },
    {
      name: 'Medical Records',
      href: '/user/records',
      icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    },
    {
      name: 'MediStore',
      href: '/store',
      icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z',
    },
    {
      name: 'My Basket',
      href: '/store/basket',
      icon: 'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z',
    },
    {
      name: 'Apply for Staff',
      href: '/apply',
      icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
    },
  ],
}

const currentNav = navigation[auth.user?.role as keyof typeof navigation] || navigation.user
</script>

<template>
  <div class="min-h-screen bg-[#fcfcfd] dark:bg-[#0b0f1a] transition-colors duration-500">
    <!-- Backdrop for mobile -->
    <div
      v-if="isSidebarOpen"
      @click="isSidebarOpen = false"
      class="fixed inset-0 z-40 bg-gray-900/60 backdrop-blur-md lg:hidden transition-opacity"
    ></div>

    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-50 w-72 bg-white dark:bg-slate-900 border-r border-gray-100 dark:border-slate-800/50 transition-all duration-500 transform lg:translate-x-0"
      :class="isSidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'"
    >
      <div class="h-full flex flex-col p-6">
        <!-- Logo -->
        <RouterLink :to="{ name: 'landing' }" class="flex items-center gap-3 px-4 mb-10 group">
          <div
            class="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:rotate-6 transition-transform"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-white"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="m12 14 4-4" />
              <path d="M3.34 19a10 10 0 1 1 17.32 0" />
            </svg>
          </div>
          <span class="text-xl font-black text-gray-900 dark:text-white tracking-tighter"
            >MediFlow</span
          >
        </RouterLink>

        <!-- Navigation -->
        <nav class="flex-1 space-y-2 overflow-y-auto -mx-2 px-2">
          <p
            class="px-4 text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-4"
          >
            Main Menu
          </p>
          <RouterLink
            v-for="item in currentNav"
            :key="item.name"
            :to="item.href"
            @click="handleNavClick"
            class="flex items-center gap-3 px-4 py-3.5 text-sm font-bold rounded-2xl transition-all group"
            :class="
              $route.path === item.href
                ? 'bg-emerald-600 text-white shadow-xl shadow-emerald-500/25'
                : 'text-gray-500 hover:text-gray-900 dark:text-slate-400 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-slate-800/50'
            "
          >
            <svg
              class="h-5 w-5 transition-transform group-hover:scale-110"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                :d="item.icon"
              />
            </svg>
            {{ item.name }}
            <span
              v-if="item.name === 'My Basket' && cartStore.cartCount > 0"
              class="ml-auto px-2 py-0.5 text-[10px] font-black bg-rose-500 text-white rounded-full transition-all animate-pulse"
            >
              {{ cartStore.cartCount }}
            </span>
          </RouterLink>
        </nav>

        <!-- Sidebar Footer -->
        <div class="pt-6 border-t border-gray-100 dark:border-slate-800/50 mt-auto">
          <button
            @click="handleLogout"
            class="flex w-full items-center gap-3 px-4 py-3.5 text-sm font-black text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-2xl transition-all group"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 transition-transform group-hover:-translate-x-1"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Sign Out
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div
      class="transition-all duration-500 min-h-screen flex flex-col"
      :class="isSidebarOpen ? 'lg:pl-72' : 'pl-0'"
    >
      <!-- Top Bar -->
      <header
        class="h-20 sticky top-0 z-40 glass border-b border-gray-100 dark:border-slate-800/50"
      >
        <div class="h-full px-6 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <button
              @click="toggleSidebar"
              class="p-2.5 text-gray-500 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-xl transition-colors lg:hidden"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
            <h2
              class="hidden sm:block text-sm font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
            >
              Workspace / {{ $route.name?.toString().replace('-', ' ') }}
            </h2>
          </div>

          <div class="flex items-center gap-4 sm:gap-8">
            <!-- Notification Bell -->
            <div class="relative" ref="notificationContainer">
              <button
                @click="toggleNotifications"
                class="p-2.5 text-gray-500 hover:text-gray-900 dark:text-slate-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-800 rounded-xl transition-all relative"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
                <span
                  v-if="unreadCount > 0"
                  class="absolute top-1.5 right-1.5 h-3 w-3 bg-rose-500 rounded-full border border-white dark:border-slate-900 animate-pulse"
                ></span>
              </button>

              <!-- Dropdown -->
              <div
                v-if="isNotificationsOpen"
                class="absolute right-0 mt-3 sm:w-96 w-80 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border border-gray-100 dark:border-slate-800/80 rounded-2xl shadow-premium p-4 z-50 animate-in fade-in slide-in-from-top-4"
              >
                <div
                  class="flex items-center justify-between border-b border-gray-100 dark:border-slate-800/80 pb-3 mb-3"
                >
                  <h3
                    class="text-xs font-black text-gray-900 dark:text-white uppercase tracking-wider"
                  >
                    Notifications ({{ unreadCount }})
                  </h3>
                  <button
                    v-if="unreadCount > 0"
                    @click="markAllRead"
                    class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest hover:underline"
                  >
                    Mark all read
                  </button>
                </div>

                <div class="max-h-80 overflow-y-auto space-y-2.5 pr-1 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-gray-100 dark:[&::-webkit-scrollbar-thumb]:bg-slate-800">
                  <div
                    v-for="n in notifications.slice(0, 15)"
                    :key="n.id"
                    class="p-3 rounded-2xl border transition-all text-left flex items-start gap-3 relative group hover:bg-gray-50/50 dark:hover:bg-slate-800/20"
                    :class="
                      n.is_read
                        ? 'bg-transparent border-gray-100/50 dark:border-slate-800/30 opacity-70'
                        : 'bg-emerald-500/5 border-emerald-500/10'
                    "
                  >
                    <div
                      :class="`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center border ${getCategoryBgColor(n.category)}`"
                      v-html="getCategoryIcon(n.category)"
                    ></div>
                    <div class="flex-1 min-w-0">
                      <h4 class="text-xs font-bold text-gray-900 dark:text-white truncate">
                        {{ n.title }}
                      </h4>
                      <p
                        class="text-[11px] text-gray-500 dark:text-slate-400 mt-0.5 leading-relaxed"
                      >
                        {{ n.message }}
                      </p>
                      <span class="text-[9px] text-gray-400 dark:text-slate-500 block mt-1">
                        {{ n.created_at }}
                      </span>
                    </div>
                    <button
                      v-if="!n.is_read"
                      @click="markRead(n.id)"
                      class="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all rounded-md"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-3.5 w-3.5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        stroke-width="3"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </button>
                  </div>

                  <div
                    v-if="notifications.length === 0"
                    class="py-8 text-center text-xs text-gray-400 dark:text-slate-500 font-medium"
                  >
                    No notifications
                  </div>
                </div>
              </div>
            </div>

            <ThemeToggle />
            <div class="h-8 w-px bg-gray-200 dark:bg-slate-800"></div>
            <div class="flex items-center gap-4 group cursor-pointer">
              <div class="text-right hidden xs:block">
                <p class="text-sm font-black text-gray-900 dark:text-white leading-tight">
                  {{ auth.user?.username }}
                </p>
                <p
                  class="text-[10px] text-emerald-600 dark:text-emerald-400 font-black uppercase tracking-widest"
                >
                  {{ auth.user?.role }}
                </p>
              </div>
              <div
                class="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 font-black text-lg shadow-sm border border-emerald-100 dark:border-emerald-500/20 group-hover:scale-105 transition-transform"
              >
                {{ auth.user?.username ? auth.user.username.charAt(0).toUpperCase() : '?' }}
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Body -->
      <main class="p-6 sm:p-10 flex-1 max-w-[1600px] mx-auto w-full">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<style>
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes slide-in-from-bottom-4 {
  from {
    transform: translateY(1rem);
  }
  to {
    transform: translateY(0);
  }
}
@keyframes slide-in-from-top-4 {
  from {
    transform: translateY(-1rem);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
.animate-in {
  animation-duration: 0.3s;
  animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
  animation-fill-mode: both;
}
.fade-in {
  animation-name: fade-in;
}
.slide-in-from-bottom-4 {
  animation-name: slide-in-from-bottom-4;
}
.slide-in-from-top-4 {
  animation-name: slide-in-from-top-4;
}
</style>
