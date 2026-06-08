<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'

const isOpen = ref(false)
const searchQuery = ref('')
const selectedIndex = ref(0)
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// Toggle palette on Ctrl+K or Cmd+K
const handleKeyDown = (event: KeyboardEvent) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    isOpen.value = !isOpen.value
  } else if (event.key === 'Escape') {
    isOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

watch(isOpen, (newVal) => {
  if (newVal) {
    searchQuery.value = ''
    selectedIndex.value = 0
  }
})

// Define available commands based on user role
const allCommands = computed(() => {
  const role = authStore.user?.role
  const list = [
    {
      id: 'theme-toggle',
      name: 'Toggle Theme (Light / Dark)',
      description: 'Switch application color theme',
      category: 'System',
      action: () => {
        themeStore.toggleTheme()
        isOpen.value = false
      }
    },
    {
      id: 'store',
      name: 'Go to MediStore Pharmacy',
      description: 'Browse medications and purchase',
      category: 'Navigation',
      action: () => {
        router.push('/store')
        isOpen.value = false
      }
    },
    {
      id: 'logout',
      name: 'Logout from System',
      description: 'End your current session',
      category: 'Account',
      action: () => {
        authStore.logout()
        router.push('/login')
        isOpen.value = false
      }
    }
  ]

  // Add role-specific navigation
  if (role === 'admin') {
    list.push(
      {
        id: 'admin-portal',
        name: 'Go to Admin Dashboard',
        description: 'Manage users, departments, and configuration',
        category: 'Navigation',
        action: () => { router.push('/admin'); isOpen.value = false }
      },
      {
        id: 'admin-departments',
        name: 'Manage Departments',
        description: 'Edit hospital department configurations',
        category: 'Admin',
        action: () => { router.push('/admin/departments'); isOpen.value = false }
      },
      {
        id: 'admin-users',
        name: 'Manage System Users',
        description: 'Approve profiles or deactivate users',
        category: 'Admin',
        action: () => { router.push('/admin/users'); isOpen.value = false }
      },
      {
        id: 'application-management',
        name: 'Review Applications',
        description: 'Approve/reject staff and patient registrations',
        category: 'Admin',
        action: () => { router.push('/applications/management'); isOpen.value = false }
      }
    )
  } else if (role === 'doctor') {
    list.push(
      {
        id: 'doctor-portal',
        name: 'Go to Doctor Dashboard',
        description: 'Manage assigned patients and consultations',
        category: 'Navigation',
        action: () => { router.push('/doctor'); isOpen.value = false }
      },
      {
        id: 'doctor-appointments',
        name: 'My Appointments List',
        description: 'View schedule and check consulting patients',
        category: 'Doctor',
        action: () => { router.push('/doctor/appointments'); isOpen.value = false }
      },
      {
        id: 'doctor-profile',
        name: 'My Professional Profile',
        description: 'View shift hours, license and registration details',
        category: 'Doctor',
        action: () => { router.push('/doctor/profile'); isOpen.value = false }
      }
    )
  } else if (role === 'nurse') {
    list.push(
      {
        id: 'nurse-portal',
        name: 'Go to Nurse Dashboard',
        description: 'View vitals capture queue and patients list',
        category: 'Navigation',
        action: () => { router.push('/nurse'); isOpen.value = false }
      },
      {
        id: 'nurse-profile',
        name: 'My Nurse Profile',
        description: 'View nurse shift details and qualifications',
        category: 'Nurse',
        action: () => { router.push('/nurse/profile'); isOpen.value = false }
      }
    )
  } else if (role === 'user') {
    list.push(
      {
        id: 'user-portal',
        name: 'Go to Patient Dashboard',
        description: 'Book consultations and view registered patient profiles',
        category: 'Navigation',
        action: () => { router.push('/user'); isOpen.value = false }
      },
      {
        id: 'user-appointments',
        name: 'My Booked Appointments',
        description: 'View status or cancel upcoming visits',
        category: 'Patient',
        action: () => { router.push('/user/appointments'); isOpen.value = false }
      },
      {
        id: 'user-records',
        name: 'My Medical Records & Prescriptions',
        description: 'Download clinical summaries and order medicines',
        category: 'Patient',
        action: () => { router.push('/user/records'); isOpen.value = false }
      }
    )
  }

  return list
})

// Filter commands based on search query
const filteredCommands = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return allCommands.value
  return allCommands.value.filter(
    (c) => c.name.toLowerCase().includes(query) || c.description.toLowerCase().includes(query)
  )
})

// Handle keyboard navigation inside list
const navigateList = (direction: 'up' | 'down') => {
  if (filteredCommands.value.length === 0) return
  if (direction === 'down') {
    selectedIndex.value = (selectedIndex.value + 1) % filteredCommands.value.length
  } else {
    selectedIndex.value =
      (selectedIndex.value - 1 + filteredCommands.value.length) % filteredCommands.value.length
  }
}

const triggerCommand = () => {
  const cmd = filteredCommands.value[selectedIndex.value]
  if (cmd) {
    cmd.action()
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4">
    <!-- Dark glassmorphic background overlay -->
    <div
      class="fixed inset-0 bg-slate-900/60 dark:bg-slate-950/80 backdrop-blur-md transition-opacity duration-300"
      @click="isOpen = false"
    ></div>

    <!-- Main palette container -->
    <div
      class="relative w-full max-w-lg bg-white/90 dark:bg-slate-900/90 border border-gray-100 dark:border-slate-800 rounded-3xl shadow-premium overflow-hidden transition-all transform duration-300 backdrop-blur-lg flex flex-col max-h-[50vh]"
    >
      <!-- Search header -->
      <div class="flex items-center border-b border-gray-100 dark:border-slate-800 p-4 gap-3">
        <span class="text-gray-400 text-lg">🔍</span>
        <input
          v-model="searchQuery"
          ref="searchInput"
          type="text"
          placeholder="Search commands (e.g. 'Theme', 'Dashboard')..."
          class="w-full bg-transparent border-none outline-none text-sm text-gray-800 dark:text-slate-100 placeholder-gray-400 dark:placeholder-slate-500 font-medium"
          @keydown.down.prevent="navigateList('down')"
          @keydown.up.prevent="navigateList('up')"
          @keydown.enter.prevent="triggerCommand"
        />
        <span class="px-2 py-0.5 rounded bg-gray-100 dark:bg-slate-800 text-[10px] text-gray-400 font-black tracking-widest uppercase">
          ESC
        </span>
      </div>

      <!-- Commands list -->
      <div class="overflow-y-auto p-2 flex-1 space-y-1">
        <div
          v-if="filteredCommands.length === 0"
          class="py-8 text-center text-xs text-gray-400 dark:text-slate-500 font-bold uppercase tracking-wider"
        >
          No matching commands found
        </div>
        <div
          v-else
          v-for="(cmd, index) in filteredCommands"
          :key="cmd.id"
          :class="`p-3.5 rounded-2xl cursor-pointer transition-all flex items-center justify-between gap-4 ${
            index === selectedIndex
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/10'
              : 'hover:bg-gray-50 dark:hover:bg-slate-800/40 text-gray-700 dark:text-slate-300'
          }`"
          @mouseenter="selectedIndex = index"
          @click="cmd.action()"
        >
          <div class="min-w-0">
            <p
              :class="`text-xs font-black tracking-wide uppercase ${
                index === selectedIndex ? 'text-white' : 'text-gray-900 dark:text-white'
              }`"
            >
              {{ cmd.name }}
            </p>
            <p
              :class="`text-[10px] truncate mt-0.5 ${
                index === selectedIndex ? 'text-emerald-100' : 'text-gray-400 dark:text-slate-500'
              }`"
            >
              {{ cmd.description }}
            </p>
          </div>
          <span
            :class="`px-2.5 py-0.5 rounded text-[8px] font-black uppercase tracking-widest ${
              index === selectedIndex
                ? 'bg-white/20 text-white'
                : 'bg-gray-100 dark:bg-slate-800 text-gray-400 dark:text-slate-500'
            }`"
          >
            {{ cmd.category }}
          </span>
        </div>
      </div>

      <!-- Footer navigation hints -->
      <div class="bg-gray-50 dark:bg-slate-800/20 border-t border-gray-100 dark:border-slate-800 px-4 py-2.5 flex items-center justify-between text-[9px] font-bold text-gray-400 dark:text-slate-500 uppercase tracking-widest">
        <div class="flex items-center gap-4">
          <span class="flex items-center gap-1">
            <span class="px-1.5 py-0.5 rounded bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 shadow-sm">↑↓</span> Navigate
          </span>
          <span class="flex items-center gap-1">
            <span class="px-1.5 py-0.5 rounded bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 shadow-sm">↵</span> Execute
          </span>
        </div>
        <div>
          <span>Press <span class="px-1.5 py-0.5 rounded bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 shadow-sm">⌘K</span> to toggle</span>
        </div>
      </div>
    </div>
  </div>
</template>
