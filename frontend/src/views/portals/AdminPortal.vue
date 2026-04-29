<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()

const stats = ref([
  {
    name: 'Total Departments',
    value: '...',
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    color: 'bg-blue-600',
  },
  {
    name: 'Active Doctors',
    value: '...',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'bg-indigo-600',
  },
  {
    name: 'Active Nurses',
    value: '...',
    icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    color: 'bg-teal-600',
  },
  {
    name: 'Pending Apps',
    value: '...',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'bg-purple-600',
  },
])

const loadStats = async () => {
  try {
    const [deptRes, docRes, nurseRes, appRes] = await Promise.all([
      api.get('/departments'),
      api.get('/doctors'),
      api.get('/nurses'),
      api.get('/applications'),
    ])

    stats.value[0].value = (deptRes.data.data?.length || 0).toString()
    stats.value[1].value = (docRes.data.data?.length || 0).toString()
    stats.value[2].value = (nurseRes.data.data?.length || 0).toString()
    
    const pendingApps = (appRes.data.data || []).filter((a: any) => a.status === 'pending').length
    stats.value[3].value = pendingApps.toString()
  } catch (error) {
    notification.error('Failed to load dashboard statistics')
    stats.value.forEach(s => s.value = 'N/A')
  }
}

onMounted(loadStats)
</script>

<template>
  <PortalBase role="admin" title="Admin Overview" :stats="stats" />
</template>
