<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  id: string
  label: string
  modelValue: string | number
  type?: string
  placeholder?: string
  error?: string
  disabled?: boolean
  required?: boolean
  helpText?: string
  autocomplete?: string
  min?: string | number
  max?: string | number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  error: '',
  disabled: false,
  required: false,
  helpText: '',
  autocomplete: 'off',
  min: '',
  max: '',
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const isPasswordVisible = ref(false)
const isFocused = ref(false)
const isDropdownOpen = ref(false)
const activeTab = ref<'date' | 'time'>('date')

const formFieldRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)
const pickerCardRef = ref<HTMLElement | null>(null)

const isPassword = computed(() => props.type === 'password')
const isDateTime = computed(() => {
  return props.type === 'date' || props.type === 'datetime-local' || props.type === 'time'
})

const inputType = computed(() => {
  if (isPassword.value) {
    return isPasswordVisible.value ? 'text' : 'password'
  }
  if (isDateTime.value) {
    return 'text'
  }
  return props.type
})

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value
}

// ───────── Bounding Rect Fixed Positioning ─────────
const pickerStyle = ref<Record<string, string>>({
  position: 'fixed',
  top: '0px',
  left: '0px',
  width: '360px',
  zIndex: '9999',
})

const isCentered = ref(false)

const updatePickerPosition = () => {
  if (!isDropdownOpen.value || !inputRef.value) return

  const rect = inputRef.value.getBoundingClientRect()
  const viewportHeight = window.innerHeight
  const viewportWidth = window.innerWidth

  // Use actual measured height if the card element is rendered, otherwise use precise fallbacks
  let pickerHeight = 385 // fallback for standard date picker
  if (props.type === 'time') {
    pickerHeight = 250
  } else if (props.type === 'datetime-local') {
    pickerHeight = activeTab.value === 'date' ? 435 : 260
  }

  if (pickerCardRef.value) {
    const measuredHeight =
      pickerCardRef.value.getBoundingClientRect().height || pickerCardRef.value.offsetHeight
    if (measuredHeight > 0) {
      pickerHeight = measuredHeight
    }
  }

  // Center as a modal if:
  // 1. Mobile screen (width < 768)
  // 2. Viewport is shorter than the picker card height plus a safety margin
  // 3. Or if the input is positioned such that the picker overflows both top and bottom
  const overflowsBottom = rect.bottom + pickerHeight > viewportHeight
  const overflowsTop = rect.top - pickerHeight < 0

  if (
    viewportWidth < 768 ||
    viewportHeight < pickerHeight + 40 ||
    (overflowsBottom && overflowsTop)
  ) {
    isCentered.value = true
    pickerStyle.value = {
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      width: 'calc(100vw - 2rem)',
      maxWidth: '360px',
      maxHeight: '90vh',
      overflowY: 'auto',
      zIndex: '9999',
    }
  } else {
    isCentered.value = false
    // Desktop Viewport: Anchor under input with overflow flips
    let pickerTop = rect.bottom + 8
    let pickerLeft = rect.left

    // Flip Upwards if it overflows the bottom and fits at the top
    if (overflowsBottom && !overflowsTop) {
      pickerTop = rect.top - pickerHeight - 8
    }

    // Shift left if it overflows the right edge
    if (pickerLeft + 360 > viewportWidth) {
      pickerLeft = Math.max(16, rect.right - 360)
    }

    pickerStyle.value = {
      position: 'fixed',
      top: `${pickerTop}px`,
      left: `${pickerLeft}px`,
      transform: 'none',
      width: '360px',
      maxWidth: 'none',
      maxHeight: 'none',
      overflowY: 'visible',
      zIndex: '9999',
    }
  }
}

// ───────── Custom Calendar Picker Logic ─────────
const monthNames = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
]

const weekdayNames = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth())
const selectedDay = ref<number | null>(null)
const selectedHour = ref(12)
const selectedMinute = ref(0)
const selectedAmPm = ref('PM')

const yearsList = computed(() => {
  const currentY = new Date().getFullYear()
  const list = []
  for (let i = currentY - 100; i <= currentY + 15; i++) {
    list.push(i)
  }
  return list
})

const daysInMonth = (year: number, month: number) => {
  return new Date(year, month + 1, 0).getDate()
}

const startDayOfWeek = (year: number, month: number) => {
  return new Date(year, month, 1).getDay()
}

const initializeCalendar = () => {
  if (props.modelValue) {
    try {
      const valStr = String(props.modelValue)
      if (props.type === 'time') {
        const parts = valStr.split(':')
        if (parts.length >= 2) {
          const hStr = parts[0] || '0'
          const mStr = parts[1] || '0'
          let h = parseInt(hStr)
          selectedAmPm.value = h >= 12 ? 'PM' : 'AM'
          h = h % 12
          selectedHour.value = h === 0 ? 12 : h
          selectedMinute.value = Math.round(parseInt(mStr) / 5) * 5
          if (selectedMinute.value >= 60) selectedMinute.value = 55
        }
      } else {
        const d = new Date(valStr)
        if (!isNaN(d.getTime())) {
          currentYear.value = d.getFullYear()
          currentMonth.value = d.getMonth()
          selectedDay.value = d.getDate()

          let h = d.getHours()
          selectedAmPm.value = h >= 12 ? 'PM' : 'AM'
          h = h % 12
          selectedHour.value = h === 0 ? 12 : h
          selectedMinute.value = Math.round(d.getMinutes() / 5) * 5
          if (selectedMinute.value >= 60) selectedMinute.value = 55
        }
      }
    } catch (e) {}
  } else {
    const today = new Date()
    currentYear.value = today.getFullYear()
    currentMonth.value = today.getMonth()
    selectedDay.value = today.getDate()
  }
}

const gridDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value

  const totalDays = daysInMonth(year, month)
  const startDay = startDayOfWeek(year, month)

  const days = []

  const prevMonthIndex = month === 0 ? 11 : month - 1
  const prevYear = month === 0 ? year - 1 : year
  const prevTotalDays = daysInMonth(prevYear, prevMonthIndex)

  for (let i = startDay - 1; i >= 0; i--) {
    days.push({
      day: prevTotalDays - i,
      isCurrent: false,
      month: prevMonthIndex,
      year: prevYear,
    })
  }

  for (let i = 1; i <= totalDays; i++) {
    days.push({
      day: i,
      isCurrent: true,
      month,
      year,
    })
  }

  const nextMonthIndex = month === 11 ? 0 : month + 1
  const nextYear = month === 11 ? year + 1 : year
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    days.push({
      day: i,
      isCurrent: false,
      month: nextMonthIndex,
      year: nextYear,
    })
  }

  return days
})

const isDayDisabled = (item: { day: number; month: number; year: number }) => {
  if (!props.min) return false
  try {
    const cellDate = new Date(item.year, item.month, item.day, 23, 59, 59)
    const minDate = new Date(String(props.min))
    if (!isNaN(minDate.getTime())) {
      const d1 = new Date(cellDate.getFullYear(), cellDate.getMonth(), cellDate.getDate())
      const d2 = new Date(minDate.getFullYear(), minDate.getMonth(), minDate.getDate())
      return d1 < d2
    }
  } catch (e) {}
  return false
}

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

const selectDay = (item: { day: number; month: number; year: number; isCurrent: boolean }) => {
  if (isDayDisabled(item)) return
  if (!item.isCurrent) {
    currentYear.value = item.year
    currentMonth.value = item.month
  }
  selectedDay.value = item.day
  updateValue()
}

const selectTime = () => {
  if (props.type === 'time') {
    let h = selectedHour.value
    if (selectedAmPm.value === 'PM' && h < 12) h += 12
    if (selectedAmPm.value === 'AM' && h === 12) h = 0
    const hourStr = String(h).padStart(2, '0')
    const minuteStr = String(selectedMinute.value).padStart(2, '0')
    emit('update:modelValue', `${hourStr}:${minuteStr}`)
  } else {
    updateValue()
  }
}

const updateValue = () => {
  if (selectedDay.value === null) return
  const yearStr = String(currentYear.value)
  const monthStr = String(currentMonth.value + 1).padStart(2, '0')
  const dayStr = String(selectedDay.value).padStart(2, '0')

  if (props.type === 'date') {
    emit('update:modelValue', `${yearStr}-${monthStr}-${dayStr}`)
  } else if (props.type === 'datetime-local') {
    let h = selectedHour.value
    if (selectedAmPm.value === 'PM' && h < 12) h += 12
    if (selectedAmPm.value === 'AM' && h === 12) h = 0
    const hourStr = String(h).padStart(2, '0')
    const minuteStr = String(selectedMinute.value).padStart(2, '0')
    emit('update:modelValue', `${yearStr}-${monthStr}-${dayStr}T${hourStr}:${minuteStr}`)
  }
}

// Format date for displaying nicely inside input
const formattedValue = computed(() => {
  if (!props.modelValue) return ''
  try {
    const val = String(props.modelValue)
    if (props.type === 'date') {
      const d = new Date(val)
      if (isNaN(d.getTime())) return val
      return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
    } else if (props.type === 'datetime-local') {
      const d = new Date(val)
      if (isNaN(d.getTime())) return val
      return d.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } else if (props.type === 'time') {
      const parts = val.split(':')
      if (parts.length >= 2) {
        const hStr = parts[0] || '0'
        const mStr = parts[1] || '0'
        let h = parseInt(hStr)
        const ampm = h >= 12 ? 'PM' : 'AM'
        h = h % 12
        if (h === 0) h = 12
        return `${String(h).padStart(2, '0')}:${mStr} ${ampm}`
      }
      return val
    }
  } catch (e) {}
  return String(props.modelValue)
})

const handleInputClick = () => {
  if (props.disabled) return
  if (isDateTime.value) {
    initializeCalendar()
    if (props.type === 'time') {
      activeTab.value = 'time'
    } else {
      activeTab.value = 'date'
    }
    isDropdownOpen.value = !isDropdownOpen.value
    if (isDropdownOpen.value) {
      setTimeout(updatePickerPosition, 0)
    }
  }
}

const switchTab = (tab: 'date' | 'time') => {
  activeTab.value = tab
  setTimeout(updatePickerPosition, 0)
}

const handleInput = (event: Event) => {
  if (isDateTime.value) return
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

// Click outside close listener
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as Node
  // If clicked inside input field or within the teleported card, keep open
  if (formFieldRef.value && formFieldRef.value.contains(target)) return
  if (pickerCardRef.value && pickerCardRef.value.contains(target)) return
  closeDropdown()
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', updatePickerPosition)
  window.addEventListener('scroll', updatePickerPosition, true)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', updatePickerPosition)
  window.removeEventListener('scroll', updatePickerPosition, true)
})
</script>

<template>
  <div ref="formFieldRef" class="w-full space-y-1.5 relative">
    <!-- Label -->
    <div class="flex justify-between items-center px-0.5">
      <label
        :for="id"
        class="block text-sm font-bold transition-colors"
        :class="[
          error ? 'text-red-500' : 'text-gray-600 dark:text-slate-400',
          isFocused && !error ? 'text-emerald-600 dark:text-emerald-400' : '',
        ]"
      >
        {{ label }}
        <span v-if="required" class="text-red-500 ml-0.5">*</span>
      </label>
      <slot name="label-right"></slot>
    </div>

    <!-- Input Container -->
    <div class="relative group">
      <input
        ref="inputRef"
        :id="id"
        :type="inputType"
        :value="isDateTime ? formattedValue : modelValue"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @click="handleInputClick"
        :readonly="isDateTime"
        :placeholder="isDateTime ? placeholder || 'Choose date & time' : placeholder"
        :disabled="disabled"
        :required="required"
        :autocomplete="autocomplete"
        class="appearance-none block w-full px-4 py-3.5 border rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 dark:disabled:bg-slate-800"
        :class="[
          error
            ? 'border-red-500 focus:ring-4 focus:ring-red-500/10'
            : 'border-gray-200 dark:border-slate-700/50 focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-500/10 dark:focus:ring-emerald-400/10',
          isPassword || isDateTime ? 'pr-11' : '',
          isDateTime
            ? 'cursor-pointer hover:border-emerald-400 dark:hover:border-emerald-500/50 font-medium'
            : '',
        ]"
      />

      <!-- Password Eye Button -->
      <button
        v-if="isPassword"
        type="button"
        @click="togglePasswordVisibility"
        tabindex="-1"
        class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-slate-300 transition-colors"
      >
        <svg
          v-if="isPasswordVisible"
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
          />
          <line x1="1" y1="1" x2="23" y2="23" />
        </svg>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      </button>

      <!-- Custom Styled Calendar / Time Icon -->
      <button
        v-if="isDateTime"
        type="button"
        @click="handleInputClick"
        tabindex="-1"
        class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 group-hover:text-emerald-500 dark:group-hover:text-emerald-400 transition-colors pointer-events-none"
      >
        <svg
          v-if="type === 'time'"
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <svg
          v-else-if="type === 'datetime-local'"
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3" />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M8 2h8m-8 4h8M4 11h16M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </button>
    </div>

    <!-- Backdrop Blur Overlay for Mobile & Adaptive Centered Desktop Modals -->
    <Teleport to="body">
      <div
        v-if="isDropdownOpen && !disabled && isCentered"
        class="fixed inset-0 bg-slate-950/40 backdrop-blur-sm z-[9998] transition-opacity duration-300"
        @click="closeDropdown"
      ></div>
    </Teleport>

    <!-- Teleported Premium Calendar Dropdown Card -->
    <Teleport to="body">
      <div
        v-if="isDropdownOpen && !disabled"
        ref="pickerCardRef"
        :style="pickerStyle"
        class="bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-3xl p-5 shadow-2xl backdrop-blur-xl bg-opacity-95 dark:bg-opacity-95 overflow-hidden animate-in fade-in duration-200"
      >
        <!-- Segmented Tab Switcher (For DateTime Fields only) -->
        <div
          v-if="type === 'datetime-local'"
          class="flex p-1 bg-gray-100/80 dark:bg-slate-800/80 rounded-2xl mb-4 border border-gray-200/20 dark:border-slate-800/30"
        >
          <button
            type="button"
            @click="switchTab('date')"
            class="flex-1 py-2 text-xs font-black rounded-xl transition-all duration-200"
            :class="
              activeTab === 'date'
                ? 'bg-white dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
                : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
            "
          >
            Select Date
          </button>
          <button
            type="button"
            @click="switchTab('time')"
            class="flex-1 py-2 text-xs font-black rounded-xl transition-all duration-200"
            :class="
              activeTab === 'time'
                ? 'bg-white dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
                : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
            "
          >
            Select Time
          </button>
        </div>

        <!-- DATE TAB SECTION -->
        <div v-if="activeTab === 'date' && type !== 'time'" class="space-y-4">
          <!-- Calendar Header (Month / Year Navigation) -->
          <div
            class="flex items-center justify-between pb-2 border-b border-gray-100 dark:border-slate-800/50"
          >
            <button
              type="button"
              @click="prevMonth"
              class="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-xl text-gray-500 dark:text-slate-400 hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <div class="flex items-center gap-1 font-black">
              <select
                v-model="currentMonth"
                class="bg-transparent font-black text-sm outline-none border-none cursor-pointer text-gray-800 dark:text-slate-200 hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors focus:ring-0"
              >
                <option
                  v-for="(mName, idx) in monthNames"
                  :key="idx"
                  :value="idx"
                  class="dark:bg-slate-900 text-gray-800 dark:text-slate-200"
                >
                  {{ mName }}
                </option>
              </select>
              <select
                v-model="currentYear"
                class="bg-transparent font-black text-sm outline-none border-none cursor-pointer text-gray-800 dark:text-slate-200 hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors focus:ring-0"
              >
                <option
                  v-for="y in yearsList"
                  :key="y"
                  :value="y"
                  class="dark:bg-slate-900 text-gray-800 dark:text-slate-200"
                >
                  {{ y }}
                </option>
              </select>
            </div>

            <button
              type="button"
              @click="nextMonth"
              class="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-xl text-gray-500 dark:text-slate-400 hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- Weekdays Header -->
          <div class="grid grid-cols-7 gap-1 text-center mb-1">
            <span
              v-for="wd in weekdayNames"
              :key="wd"
              class="text-[10px] font-black uppercase tracking-wider text-gray-400 dark:text-slate-500 py-1"
            >
              {{ wd }}
            </span>
          </div>

          <!-- Days Grid (Sleek Compact Size) -->
          <div class="grid grid-cols-7 gap-1">
            <button
              v-for="(item, idx) in gridDays"
              :key="idx"
              type="button"
              @click="selectDay(item)"
              :disabled="isDayDisabled(item)"
              class="h-8 w-8 mx-auto rounded-full text-xs font-bold flex items-center justify-center transition-all duration-200 disabled:opacity-20 disabled:cursor-not-allowed disabled:hover:bg-transparent"
              :class="[
                !item.isCurrent
                  ? 'text-gray-300 dark:text-slate-600'
                  : 'text-gray-700 dark:text-slate-300',
                selectedDay === item.day &&
                currentMonth === item.month &&
                currentYear === item.year &&
                item.isCurrent
                  ? 'bg-emerald-600 text-white font-black scale-105 shadow-lg shadow-emerald-600/25'
                  : 'hover:bg-gray-100 dark:hover:bg-slate-800/80 active:scale-90',
                new Date().getDate() === item.day &&
                new Date().getMonth() === item.month &&
                new Date().getFullYear() === item.year
                  ? 'border border-emerald-500 text-emerald-600 dark:text-emerald-400 font-extrabold'
                  : '',
              ]"
            >
              {{ item.day }}
            </button>
          </div>
        </div>

        <!-- TIME TAB SECTION -->
        <div v-if="activeTab === 'time' && type !== 'date'" class="space-y-4">
          <h4
            class="text-xs font-black uppercase tracking-widest text-gray-400 dark:text-slate-500 pl-1 mb-1"
          >
            Choose Dial Values
          </h4>

          <div
            class="flex items-center justify-between gap-3 bg-gray-50 dark:bg-slate-800/40 p-3 rounded-2xl border border-gray-100 dark:border-slate-800/40"
          >
            <!-- Hour Select -->
            <div class="flex items-center gap-1.5 flex-1 pl-1">
              <label class="text-[9px] font-black uppercase text-gray-400 dark:text-slate-500"
                >Hour</label
              >
              <select
                v-model="selectedHour"
                @change="selectTime"
                class="flex-1 bg-transparent text-sm font-black text-gray-800 dark:text-slate-200 outline-none border-none cursor-pointer focus:ring-0 py-0 pl-1 pr-4"
              >
                <option
                  v-for="h in 12"
                  :key="h"
                  :value="h"
                  class="dark:bg-slate-900 text-gray-800 dark:text-slate-200"
                >
                  {{ String(h).padStart(2, '0') }}
                </option>
              </select>
            </div>

            <div class="text-gray-300 dark:text-slate-700 font-black text-sm">:</div>

            <!-- Minute Select -->
            <div class="flex items-center gap-1.5 flex-1 pl-1">
              <label class="text-[9px] font-black uppercase text-gray-400 dark:text-slate-500"
                >Min</label
              >
              <select
                v-model="selectedMinute"
                @change="selectTime"
                class="flex-1 bg-transparent text-sm font-black text-gray-800 dark:text-slate-200 outline-none border-none cursor-pointer focus:ring-0 py-0 pl-1 pr-4"
              >
                <option
                  v-for="m in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]"
                  :key="m"
                  :value="m"
                  class="dark:bg-slate-900 text-gray-800 dark:text-slate-200"
                >
                  {{ String(m).padStart(2, '0') }}
                </option>
              </select>
            </div>

            <!-- AM / PM Pill Selector -->
            <div
              class="flex rounded-xl bg-gray-200/50 dark:bg-slate-800 p-0.5 border border-gray-100/50 dark:border-slate-800/30"
            >
              <button
                type="button"
                @click="
                  selectedAmPm = 'AM'
                  selectTime()
                "
                class="px-2.5 py-1.5 text-[9px] font-black rounded-lg transition-all"
                :class="
                  selectedAmPm === 'AM'
                    ? 'bg-white dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
                    : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
                "
              >
                AM
              </button>
              <button
                type="button"
                @click="
                  selectedAmPm = 'PM'
                  selectTime()
                "
                class="px-2.5 py-1.5 text-[9px] font-black rounded-lg transition-all"
                :class="
                  selectedAmPm === 'PM'
                    ? 'bg-white dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
                    : 'text-gray-400 hover:text-gray-600 dark:hover:text-slate-300'
                "
              >
                PM
              </button>
            </div>
          </div>
        </div>

        <!-- Action Footer -->
        <div class="mt-5 flex justify-end gap-2">
          <button
            type="button"
            @click="closeDropdown"
            class="px-5 py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-emerald-600/25 active:scale-95 transition-all w-full flex items-center justify-center gap-2"
          >
            Confirm Selection
          </button>
        </div>
      </div>
    </Teleport>

    <!-- Error Message or Help Text -->
    <div class="min-h-[1.25rem] px-1 transition-all duration-200">
      <p
        v-if="error"
        class="text-xs font-medium text-red-500 flex items-center gap-1 animate-in fade-in slide-in-from-top-1"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-3 w-3"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        {{ error }}
      </p>
      <p v-else-if="helpText" class="text-xs text-gray-500 dark:text-slate-400">
        {{ helpText }}
      </p>
    </div>
  </div>
</template>

<style scoped>
/* Standard animations inside component */
.animate-in {
  animation: animate-in 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes animate-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
