<script setup lang="ts">
import PortalBase from './PortalBase.vue'
const stats = [
  {
    name: "Today's Appointments",
    value: '8',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    color: 'bg-blue-600',
  },
  {
    name: 'My Patients',
    value: '124',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    color: 'bg-green-600',
  },
  {
    name: 'Pending Records',
    value: '3',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'bg-yellow-600',
  },
  {
    name: 'Next Shift',
    value: '08:00 AM',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-12 0 9 9 0 0112 0z',
    color: 'bg-indigo-600',
  },
]
</script>
<template>
  <PortalBase role="doctor" title="Doctor Dashboard" :stats="stats" />
</template>
