<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()

const stats = ref([
  {
    name: "Today's Appointments",
    value: '...',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    color: 'bg-emerald-600',
  },
  {
    name: 'My Patients',
    value: '...',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    color: 'bg-teal-600',
  },
  {
    name: 'Pending Patient Apps',
    value: '...',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'bg-emerald-500',
  },
  {
    name: 'Next Shift',
    value: '...',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-12 0 9 9 0 0112 0z',
    color: 'bg-teal-500',
  },
])

const loadStats = async () => {
  try {
    const appRes = await api.get('/applications')
    const pendingApps = (appRes.data.data || []).filter((a: any) => a.status === 'pending').length

    stats.value[0].value = 'Coming Soon'
    stats.value[1].value = 'Coming Soon'
    stats.value[2].value = pendingApps.toString()
    stats.value[3].value = 'Coming Soon'
  } catch (error) {
    notification.error('Failed to load dashboard statistics')
    stats.value.forEach((s) => (s.value = 'N/A'))
  }
}

onMounted(loadStats)
</script>

<template>
  <PortalBase role="doctor" title="Doctor Dashboard" :stats="stats" />
</template>
