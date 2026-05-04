<script setup lang="ts">
import PortalBase from './PortalBase.vue'
const stats = [
  {
    name: 'Profile Status',
    value: 'Pending',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    color: 'bg-emerald-600',
  },
  {
    name: 'Active Applications',
    value: '0',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'bg-teal-600',
  },
]
</script>
<template>
  <PortalBase role="user" title="Welcome to MediFlow" :stats="stats" />
</template>
