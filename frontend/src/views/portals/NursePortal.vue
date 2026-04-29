<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()

const stats = ref([
  {
    name: 'Pending Vitals',
    value: '...',
    icon: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3',
    color: 'bg-blue-600',
  },
  {
    name: 'Pending Patient Apps',
    value: '...',
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    color: 'bg-green-600',
  },
  {
    name: 'Patients in Ward',
    value: '...',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'bg-indigo-600',
  },
  {
    name: 'Shift Status',
    value: '...',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-12 0 9 9 0 0112 0z',
    color: 'bg-purple-600',
  },
])

const loadStats = async () => {
  try {
    const appRes = await api.get('/applications')
    const pendingApps = (appRes.data.data || []).filter((a: any) => a.status === 'pending').length
    
    stats.value[0].value = 'Coming Soon'
    stats.value[1].value = pendingApps.toString()
    stats.value[2].value = 'Coming Soon'
    stats.value[3].value = 'Coming Soon'
  } catch (error) {
    notification.error('Failed to load dashboard statistics')
    stats.value.forEach(s => s.value = 'N/A')
  }
}

onMounted(loadStats)
</script>

<template>
  <PortalBase role="nurse" title="Nurse Dashboard" :stats="stats" />
</template>
