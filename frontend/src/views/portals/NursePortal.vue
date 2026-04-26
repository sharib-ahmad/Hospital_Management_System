<script setup lang="ts">
import PortalBase from './PortalBase.vue'
const stats = [
  {
    name: 'Pending Vitals',
    value: '12',
    icon: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3',
    color: 'bg-blue-600',
  },
  {
    name: 'Active Ward',
    value: 'B-101',
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    color: 'bg-green-600',
  },
  {
    name: 'Patients in Ward',
    value: '15',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'bg-indigo-600',
  },
  {
    name: 'Shift Status',
    value: 'Active',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-12 0 9 9 0 0112 0z',
    color: 'bg-purple-600',
  },
]
</script>
<template>
  <PortalBase role="nurse" title="Nurse Dashboard" :stats="stats" />
</template>
