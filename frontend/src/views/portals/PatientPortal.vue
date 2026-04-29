<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PortalBase from './PortalBase.vue'
import api from '../../utils/axios'
import { useNotificationStore } from '../../stores/notification'

const notification = useNotificationStore()

const stats = ref([
  {
    name: 'My Appointments',
    value: '...',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    color: 'bg-blue-600',
  },
  {
    name: 'Prescriptions',
    value: '...',
    icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
    color: 'bg-green-600',
  },
  {
    name: 'Medical Reports',
    value: '...',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'bg-indigo-600',
  },
  {
    name: 'Health Score',
    value: '...',
    icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
    color: 'bg-red-600',
  },
])

const loadStats = async () => {
  // We don't have endpoints for these yet, so we just set them to "Coming Soon" 
  // or fetch any relevant basic info later when endpoints are ready.
  stats.value.forEach(s => s.value = 'Coming Soon')
}

onMounted(loadStats)
</script>

<template>
  <PortalBase role="patient" title="My Health Portal" :stats="stats" />
</template>
