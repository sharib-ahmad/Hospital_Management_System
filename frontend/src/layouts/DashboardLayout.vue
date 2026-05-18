<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ThemeToggle from '../components/ThemeToggle.vue'

const auth = useAuthStore()
const router = useRouter()
const isSidebarOpen = ref(false)

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
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
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
  ],
  nurse: [
    {
      name: 'Dashboard',
      href: '/nurse',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    },
    {
      name: 'Approve Applications',
      href: '/applications/management',
      icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    },
  ],
  user: [
    {
      name: 'Welcome',
      href: '/user',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
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
                {{ auth.user?.username ? auth.user.username[0].toUpperCase() : '?' }}
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
.animate-in {
  animation-duration: 0.5s;
  animation-fill-mode: both;
}
.fade-in {
  animation-name: fade-in;
}
.slide-in-from-bottom-4 {
  animation-name: slide-in-from-bottom-4;
}
</style>
