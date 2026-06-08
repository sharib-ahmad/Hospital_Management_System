<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'
import api from '../utils/axios'
import FormField from './FormField.vue'

const authStore = useAuthStore()
const notification = useNotificationStore()

interface EventItem {
  id: number
  title: string
  description?: string
  event_date: string
  event_type: string
  location?: string
}

const events = ref<EventItem[]>([])
const isLoading = ref(true)
const showCreateModal = ref(false)
const isSubmitting = ref(false)

const newEvent = ref({
  title: '',
  description: '',
  event_date: '',
  event_type: 'meeting',
  location: '',
})

const isAdmin = computed(() => authStore.user?.role === 'admin')

const loadEvents = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/events')
    events.value = res.data.data || res.data || []
  } catch (err) {
    console.error('Failed to load events', err)
  } finally {
    isLoading.value = false
  }
}

const handleCreateEvent = async () => {
  if (!newEvent.value.title.trim()) {
    notification.error('Title is required')
    return
  }
  if (!newEvent.value.event_date) {
    notification.error('Date and time are required')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      ...newEvent.value,
      event_date: new Date(newEvent.value.event_date).toISOString(),
    }
    await api.post('/events', payload)
    notification.success('Event created successfully')
    showCreateModal.value = false
    newEvent.value = {
      title: '',
      description: '',
      event_date: '',
      event_type: 'meeting',
      location: '',
    }
    await loadEvents()
  } catch (err: any) {
    notification.error(err.response?.data?.message || 'Failed to create event')
  } finally {
    isSubmitting.value = false
  }
}

const handleDeleteEvent = async (id: number) => {
  if (!confirm('Are you sure you want to delete this event?')) return
  try {
    await api.delete(`/events/${id}`)
    notification.success('Event deleted successfully')
    await loadEvents()
  } catch (err: any) {
    notification.error(err.response?.data?.message || 'Failed to delete event')
  }
}

const formatEventMonth = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short' }).toUpperCase()
  } catch {
    return 'EVENT'
  }
}

const formatEventDay = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { day: '2-digit' })
  } catch {
    return '00'
  }
}

const formatEventTime = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

const getEventTypeColor = (type: string) => {
  switch (type?.toLowerCase()) {
    case 'meeting':
      return 'bg-blue-600'
    case 'occasion':
      return 'bg-indigo-600'
    case 'ceremony':
      return 'bg-emerald-600'
    default:
      return 'bg-purple-600'
  }
}

const minDateTime = computed(() => {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  const localNow = new Date(now.getTime() - offset * 60 * 1000)
  return localNow.toISOString().slice(0, 16)
})

onMounted(loadEvents)
</script>

<template>
  <div
    class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 p-8 shadow-premium"
  >
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-base font-black text-gray-900 dark:text-white uppercase tracking-widest">
        Upcoming Events
      </h3>
      <button
        v-if="isAdmin"
        @click="showCreateModal = true"
        class="p-2 bg-emerald-50 hover:bg-emerald-100 dark:bg-slate-800 dark:hover:bg-slate-700 text-emerald-600 dark:text-emerald-400 rounded-xl transition-all border border-emerald-100/30"
        title="Create Event"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="3"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <div
        class="animate-spin rounded-full h-6 w-6 border-[3px] border-emerald-600 border-t-transparent"
      ></div>
    </div>

    <!-- Empty state -->
    <div v-else-if="events.length === 0" class="text-center py-8">
      <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">No upcoming events</p>
    </div>

    <!-- Events list -->
    <div v-else class="space-y-4">
      <div
        v-for="event in events"
        :key="event.id"
        class="flex items-start justify-between p-4 rounded-2xl bg-gray-50/50 dark:bg-slate-800/30 border border-gray-100/50 dark:border-slate-700/30 group"
      >
        <div class="flex items-center gap-4">
          <div
            :class="`w-10 h-10 rounded-xl flex flex-col items-center justify-center text-white font-bold leading-none ${getEventTypeColor(
              event.event_type,
            )}`"
          >
            <span class="text-[9px]">{{ formatEventMonth(event.event_date) }}</span>
            <span class="text-sm mt-0.5">{{ formatEventDay(event.event_date) }}</span>
          </div>
          <div>
            <p class="text-xs font-black text-gray-900 dark:text-white">{{ event.title }}</p>
            <p class="text-[10px] text-gray-500 font-bold uppercase tracking-tighter mt-1">
              {{ formatEventTime(event.event_date) }}
              <span v-if="event.location"> • {{ event.location }}</span>
            </p>
            <span
              :class="`inline-block mt-2 px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest text-white ${getEventTypeColor(
                event.event_type,
              )}`"
            >
              {{ event.event_type }}
            </span>
          </div>
        </div>

        <button
          v-if="isAdmin"
          @click="handleDeleteEvent(event.id)"
          class="p-1.5 text-gray-400 hover:text-rose-500 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/20 rounded-lg transition-all opacity-0 group-hover:opacity-100"
          title="Delete Event"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Create Event Modal (Admin Only) -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto"
      @click.self="showCreateModal = false"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-[2rem] border border-gray-100 dark:border-slate-800 max-w-md w-full p-6 sm:p-10 shadow-premium-xl max-h-[90vh] overflow-y-auto"
      >
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
            Create Event
          </h3>
          <button
            @click="showCreateModal = false"
            class="w-10 h-10 rounded-full bg-gray-50 dark:bg-slate-800 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-slate-200 transition-colors"
          >
            ✕
          </button>
        </div>

        <form @submit.prevent="handleCreateEvent" class="space-y-6">
          <FormField
            id="event-title"
            label="Event Title"
            placeholder="e.g. Annual Doctor Ceremony"
            v-model="newEvent.title"
            required
          />

          <div class="space-y-1.5">
            <label class="block text-sm font-semibold text-gray-700 dark:text-slate-300">
              Event Type
            </label>
            <select
              v-model="newEvent.event_type"
              class="block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-gray-900 dark:text-white sm:text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 transition-all"
            >
              <option value="meeting">Meeting</option>
              <option value="occasion">Occasion</option>
              <option value="ceremony">Ceremony</option>
              <option value="other">Other</option>
            </select>
          </div>

          <FormField
            id="event-date"
            label="Event Date & Time"
            type="datetime-local"
            v-model="newEvent.event_date"
            :min="minDateTime"
            required
          />

          <FormField
            id="event-location"
            label="Location"
            placeholder="e.g. Conference Hall A"
            v-model="newEvent.location"
          />

          <div class="space-y-1.5">
            <label class="block text-sm font-semibold text-gray-700 dark:text-slate-300">
              Description
            </label>
            <textarea
              v-model="newEvent.description"
              rows="3"
              placeholder="Provide brief details about the event..."
              class="block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-gray-900 dark:text-white sm:text-sm outline-none focus:ring-4 focus:ring-emerald-500/10 transition-all resize-none"
            ></textarea>
          </div>

          <div class="flex gap-4 pt-2">
            <button
              type="button"
              @click="showCreateModal = false"
              class="flex-1 py-3.5 bg-gray-50 dark:bg-slate-800 text-gray-600 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-xl hover:bg-gray-100 transition-all border border-gray-200 dark:border-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isSubmitting"
              class="flex-1 py-3.5 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 shadow-lg transition-all disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {{ isSubmitting ? 'Creating...' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
