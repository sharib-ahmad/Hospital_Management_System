<script setup lang="ts">
import { ref, computed } from 'vue'

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
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  error: '',
  disabled: false,
  required: false,
  helpText: '',
  autocomplete: 'off',
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const isPasswordVisible = ref(false)
const isFocused = ref(false)

const isPassword = computed(() => props.type === 'password')
const inputType = computed(() => {
  if (isPassword.value) {
    return isPasswordVisible.value ? 'text' : 'password'
  }
  return props.type
})

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value
}

const handleInput = (event: Event) => {
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
</script>

<template>
  <div class="w-full space-y-1.5">
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

      <!-- Optional Right-aligned info/link (slot) -->
      <slot name="label-right"></slot>
    </div>

    <!-- Input Container -->
    <div class="relative group">
      <input
        :id="id"
        :type="inputType"
        :value="modelValue"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :autocomplete="autocomplete"
        class="appearance-none block w-full px-4 py-3.5 border rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 dark:disabled:bg-slate-800"
        :class="[
          error
            ? 'border-red-500 focus:ring-4 focus:ring-red-500/10'
            : 'border-gray-200 dark:border-slate-700/50 focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-500/10 dark:focus:ring-emerald-400/10',
        ]"
      />

      <!-- Password Toggle Button -->
      <button
        v-if="isPassword"
        type="button"
        @click="togglePasswordVisibility"
        tabindex="-1"
        class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-slate-300 transition-colors"
      >
        <!-- Eye Off Icon -->
        <svg
          v-if="isPasswordVisible"
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
          />
          <line x1="1" y1="1" x2="23" y2="23" />
        </svg>
        <!-- Eye Icon -->
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      </button>
    </div>

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
