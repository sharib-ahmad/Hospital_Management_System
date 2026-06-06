<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import DashboardLayout from '../../layouts/DashboardLayout.vue'
import { useNotificationStore } from '../../stores/notification'
import api from '../../utils/axios'

interface Medicine {
  id: string
  name: string
  description: string
  category: string
  price: number
  stock: number
  manufacturer: string
}

const notification = useNotificationStore()
const medicines = ref<Medicine[]>([])
const isLoading = ref(true)
const searchQuery = ref('')
const categoryFilter = ref('')
const isModalOpen = ref(false)
const isEditing = ref(false)
const isDeleteConfirmOpen = ref(false)
const deletingId = ref<string | null>(null)
const isSubmitting = ref(false)

const categories = [
  'Antibiotic',
  'Pain Relief',
  'Supplements',
  'Cold & Flu',
  'Heart Health',
  'Other',
]

const form = ref({
  name: '',
  description: '',
  category: '',
  price: 0,
  stock: 0,
  manufacturer: '',
})
const editingId = ref<string | null>(null)

watch(isModalOpen, (val) => {
  if (val) document.body.classList.add('overflow-hidden')
  else document.body.classList.remove('overflow-hidden')
})

watch(isDeleteConfirmOpen, (val) => {
  if (val) document.body.classList.add('overflow-hidden')
  else document.body.classList.remove('overflow-hidden')
})

const loadMedicines = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/medistore/medicines')
    medicines.value = res.data.data || []
  } catch {
    notification.error('Failed to load medicines')
  } finally {
    isLoading.value = false
  }
}

onMounted(loadMedicines)

// ── Stats ──────────────────────────────────────────────────────────────────
const totalStock = computed(() => medicines.value.reduce((s, m) => s + (m.stock ?? 0), 0))
const outOfStock = computed(() => medicines.value.filter((m) => m.stock === 0).length)
const uniqueCategories = computed(() => new Set(medicines.value.map((m) => m.category)).size)

// ── Filtered list ──────────────────────────────────────────────────────────
const filteredMedicines = computed(() => {
  let list = medicines.value
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(
      (m) =>
        m.name.toLowerCase().includes(q) ||
        m.manufacturer?.toLowerCase().includes(q) ||
        m.category?.toLowerCase().includes(q),
    )
  }
  if (categoryFilter.value) {
    list = list.filter((m) => m.category === categoryFilter.value)
  }
  return list
})

// ── Helpers ────────────────────────────────────────────────────────────────
const formatPrice = (p: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(p)

const stockBarColor = (stock: number) => {
  if (stock > 20) return 'bg-emerald-500'
  if (stock >= 5) return 'bg-amber-500'
  return 'bg-rose-500'
}

const stockBarWidth = (stock: number) => {
  const pct = Math.min((stock / 100) * 100, 100)
  return `${pct}%`
}

const stockLabel = (stock: number) => {
  if (stock === 0)
    return {
      text: 'Out of Stock',
      cls: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400',
    }
  if (stock < 5)
    return {
      text: 'Critical',
      cls: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400',
    }
  if (stock <= 20)
    return {
      text: 'Low',
      cls: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    }
  return {
    text: 'In Stock',
    cls: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  }
}

const categoryBadgeColor = (cat: string) => {
  const map: Record<string, string> = {
    Antibiotic: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    'Pain Relief': 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    Supplements: 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400',
    'Cold & Flu': 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400',
    'Heart Health': 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400',
    Other: 'bg-gray-100 text-gray-700 dark:bg-slate-700 dark:text-slate-300',
  }
  return map[cat] || map['Other']
}

// ── Create / Edit ──────────────────────────────────────────────────────────
const openCreate = () => {
  isEditing.value = false
  editingId.value = null
  form.value = { name: '', description: '', category: '', price: 0, stock: 0, manufacturer: '' }
  isModalOpen.value = true
}

const openEdit = (med: Medicine) => {
  isEditing.value = true
  editingId.value = med.id
  form.value = {
    name: med.name,
    description: med.description,
    category: med.category,
    price: med.price,
    stock: med.stock,
    manufacturer: med.manufacturer,
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const submitForm = async () => {
  if (!form.value.name || !form.value.category) {
    notification.error('Name and Category are required')
    return
  }
  isSubmitting.value = true
  try {
    if (isEditing.value && editingId.value) {
      await api.put(`/medistore/medicines/${editingId.value}`, form.value)
      notification.success('Medicine updated successfully')
    } else {
      await api.post('/medistore/medicines', form.value)
      notification.success('Medicine created successfully')
    }
    closeModal()
    await loadMedicines()
  } catch (err: any) {
    notification.error(err.response?.data?.message || 'Failed to save medicine')
  } finally {
    isSubmitting.value = false
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
const openDelete = (id: string) => {
  deletingId.value = id
  isDeleteConfirmOpen.value = true
}

const closeDelete = () => {
  isDeleteConfirmOpen.value = false
  deletingId.value = null
}

const confirmDelete = async () => {
  if (!deletingId.value) return
  isSubmitting.value = true
  try {
    await api.delete(`/medistore/medicines/${deletingId.value}`)
    notification.success('Medicine deleted')
    closeDelete()
    await loadMedicines()
  } catch (err: any) {
    notification.error(err.response?.data?.message || 'Failed to delete medicine')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <DashboardLayout>
    <!-- ── Header ──────────────────────────────────────────────────────── -->
    <div class="mb-12 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">
            Medicine Management
          </h1>
          <span
            class="px-3 py-1 bg-violet-50 dark:bg-violet-900/30 text-violet-700 dark:text-violet-400 text-[10px] font-black uppercase tracking-widest rounded-full border border-violet-200/50 dark:border-violet-500/20"
          >
            Pharmacist Portal
          </span>
        </div>
        <p class="text-gray-500 dark:text-slate-400 font-medium">
          Manage pharmacy inventory, stock levels, and medicine catalog.
        </p>
      </div>
      <button
        @click="openCreate"
        class="px-8 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/20 hover:-translate-y-1 transition-all active:scale-95 uppercase tracking-widest text-xs flex items-center justify-center gap-3 shrink-0"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="3"
        >
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        Add Medicine
      </button>
    </div>

    <!-- ── Stats ───────────────────────────────────────────────────────── -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
      <!-- Total Medicines -->
      <div
        class="glass p-6 rounded-[2rem] border border-white/40 dark:border-white/5 shadow-premium group"
      >
        <div class="flex items-center justify-between">
          <div>
            <p
              class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
            >
              Total Medicines
            </p>
            <p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter">
              {{ medicines.length }}
            </p>
          </div>
          <div
            class="w-12 h-12 bg-emerald-50 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center text-emerald-600 group-hover:rotate-6 transition-transform"
          >
            <svg
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- Total Stock -->
      <div
        class="glass p-6 rounded-[2rem] border border-white/40 dark:border-white/5 shadow-premium group"
      >
        <div class="flex items-center justify-between">
          <div>
            <p
              class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
            >
              Total Stock
            </p>
            <p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter">
              {{ totalStock.toLocaleString() }}
            </p>
          </div>
          <div
            class="w-12 h-12 bg-teal-50 dark:bg-teal-900/30 rounded-2xl flex items-center justify-center text-teal-600 group-hover:rotate-6 transition-transform"
          >
            <svg
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- Out of Stock -->
      <div
        class="glass p-6 rounded-[2rem] border border-white/40 dark:border-white/5 shadow-premium group"
      >
        <div class="flex items-center justify-between">
          <div>
            <p
              class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
            >
              Out of Stock
            </p>
            <p class="text-3xl font-black text-rose-500 dark:text-rose-400 tracking-tighter">
              {{ outOfStock }}
            </p>
          </div>
          <div
            class="w-12 h-12 bg-rose-50 dark:bg-rose-900/30 rounded-2xl flex items-center justify-center text-rose-500 group-hover:rotate-6 transition-transform"
          >
            <svg
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- Categories -->
      <div
        class="glass p-6 rounded-[2rem] border border-white/40 dark:border-white/5 shadow-premium group"
      >
        <div class="flex items-center justify-between">
          <div>
            <p
              class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest mb-1"
            >
              Categories
            </p>
            <p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter">
              {{ uniqueCategories }}
            </p>
          </div>
          <div
            class="w-12 h-12 bg-purple-50 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center text-purple-600 group-hover:rotate-6 transition-transform"
          >
            <svg
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Search + Filter ─────────────────────────────────────────────── -->
    <div
      class="glass rounded-[2.5rem] border border-white/40 dark:border-white/5 p-8 shadow-premium mb-8"
    >
      <div class="flex flex-col sm:flex-row gap-4">
        <!-- Search -->
        <div class="relative flex-1">
          <svg
            class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search medicines, manufacturer..."
            class="appearance-none block w-full pl-12 pr-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
          />
        </div>
        <!-- Category filter -->
        <select
          v-model="categoryFilter"
          class="appearance-none block sm:w-52 px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
        >
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>
    </div>

    <!-- ── Loading ─────────────────────────────────────────────────────── -->
    <div v-if="isLoading" class="flex justify-center items-center py-32">
      <div
        class="animate-spin rounded-full h-10 w-10 border-[3px] border-emerald-600 border-t-transparent"
      ></div>
    </div>

    <!-- ── Empty State ─────────────────────────────────────────────────── -->
    <div
      v-else-if="filteredMedicines.length === 0"
      class="border-2 border-dashed border-gray-200 dark:border-slate-700/50 rounded-[2.5rem] p-16 text-center"
    >
      <svg
        class="mx-auto h-16 w-16 text-gray-300 dark:text-slate-600 mb-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
        />
      </svg>
      <h3 class="text-xl font-black text-gray-900 dark:text-white mb-2">No medicines found</h3>
      <p class="text-gray-500 dark:text-slate-400 mb-8">
        {{
          searchQuery || categoryFilter
            ? 'Try adjusting your search or filters.'
            : 'Add your first medicine to the inventory.'
        }}
      </p>
      <button
        v-if="!searchQuery && !categoryFilter"
        @click="openCreate"
        class="px-6 py-3 bg-emerald-600 text-white font-black rounded-2xl text-sm uppercase tracking-widest hover:-translate-y-1 transition-all shadow-lg shadow-emerald-500/20"
      >
        Add First Medicine
      </button>
    </div>

    <!-- ── Medicine Grid ────────────────────────────────────────────────── -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
      <div
        v-for="med in filteredMedicines"
        :key="med.id"
        class="glass rounded-[2rem] border border-white/40 dark:border-white/5 p-6 shadow-premium hover:-translate-y-1 transition-all duration-300 flex flex-col gap-4"
      >
        <!-- Name + Category -->
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1 min-w-0">
            <h3 class="font-black text-gray-900 dark:text-white text-lg leading-tight truncate">
              {{ med.name }}
            </h3>
            <span
              :class="categoryBadgeColor(med.category)"
              class="inline-block mt-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest border border-transparent"
            >
              {{ med.category }}
            </span>
          </div>
          <span
            :class="stockLabel(med.stock).cls"
            class="shrink-0 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest"
          >
            {{ stockLabel(med.stock).text }}
          </span>
        </div>

        <!-- Description -->
        <p class="text-sm text-gray-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
          {{ med.description || 'No description provided.' }}
        </p>

        <!-- Stock bar -->
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <span
              class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
              >Stock Level</span
            >
            <span class="text-sm font-black text-gray-700 dark:text-slate-300"
              >{{ med.stock }} units</span
            >
          </div>
          <div class="h-2 bg-gray-100 dark:bg-slate-700/50 rounded-full overflow-hidden">
            <div
              :class="stockBarColor(med.stock)"
              class="h-full rounded-full transition-all duration-500"
              :style="{ width: stockBarWidth(med.stock) }"
            ></div>
          </div>
        </div>

        <!-- Price + Manufacturer -->
        <div class="flex items-center justify-between pt-1">
          <div>
            <p
              class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
            >
              Price
            </p>
            <p class="text-xl font-black text-emerald-600 dark:text-emerald-400">
              {{ formatPrice(med.price) }}
            </p>
          </div>
          <div class="text-right">
            <p
              class="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-widest"
            >
              Manufacturer
            </p>
            <p class="text-sm font-bold text-gray-700 dark:text-slate-300 max-w-[120px] truncate">
              {{ med.manufacturer || '—' }}
            </p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 pt-2 border-t border-gray-100 dark:border-slate-700/30">
          <button
            @click="openEdit(med)"
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-900/40 font-black text-xs uppercase tracking-widest transition-all"
          >
            <svg
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            Edit
          </button>
          <button
            @click="openDelete(med.id)"
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400 hover:bg-rose-100 dark:hover:bg-rose-900/40 font-black text-xs uppercase tracking-widest transition-all"
          >
            <svg
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
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- Create / Edit Modal                                                 -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div
        v-if="isModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
        @click.self="closeModal"
      >
        <div
          class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-lg w-full p-10 shadow-premium-xl overflow-y-auto max-h-[90vh]"
        >
          <!-- Modal header -->
          <div class="flex items-center justify-between mb-8">
            <div>
              <h2 class="text-2xl font-black text-gray-900 dark:text-white">
                {{ isEditing ? 'Edit Medicine' : 'Add Medicine' }}
              </h2>
              <p class="text-sm text-gray-500 dark:text-slate-400 mt-1">
                {{
                  isEditing
                    ? 'Update the medicine details below.'
                    : 'Fill in the details to add a new medicine.'
                }}
              </p>
            </div>
            <button
              @click="closeModal"
              class="p-2 rounded-xl text-gray-400 hover:text-gray-600 dark:hover:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Form -->
          <form @submit.prevent="submitForm" class="space-y-5">
            <!-- Name -->
            <div>
              <label
                class="block text-xs font-black text-gray-700 dark:text-slate-300 uppercase tracking-widest mb-2"
              >
                Medicine Name <span class="text-rose-500">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                placeholder="e.g. Amoxicillin 500mg"
                required
                class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
              />
            </div>

            <!-- Description -->
            <div>
              <label
                class="block text-xs font-black text-gray-700 dark:text-slate-300 uppercase tracking-widest mb-2"
              >
                Description
              </label>
              <textarea
                v-model="form.description"
                placeholder="Brief description of the medicine..."
                rows="3"
                class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 resize-none"
              ></textarea>
            </div>

            <!-- Category -->
            <div>
              <label
                class="block text-xs font-black text-gray-700 dark:text-slate-300 uppercase tracking-widest mb-2"
              >
                Category <span class="text-rose-500">*</span>
              </label>
              <select
                v-model="form.category"
                required
                class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
              >
                <option value="" disabled>Select a category</option>
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <!-- Price + Stock -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label
                  class="block text-xs font-black text-gray-700 dark:text-slate-300 uppercase tracking-widest mb-2"
                >
                  Price (USD)
                </label>
                <input
                  v-model.number="form.price"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
                />
              </div>
              <div>
                <label
                  class="block text-xs font-black text-gray-700 dark:text-slate-300 uppercase tracking-widest mb-2"
                >
                  Stock (units)
                </label>
                <input
                  v-model.number="form.stock"
                  type="number"
                  min="0"
                  step="1"
                  placeholder="0"
                  class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
                />
              </div>
            </div>

            <!-- Manufacturer -->
            <div>
              <label
                class="block text-xs font-black text-gray-700 dark:text-slate-300 uppercase tracking-widest mb-2"
              >
                Manufacturer
              </label>
              <input
                v-model="form.manufacturer"
                type="text"
                placeholder="e.g. Pfizer Inc."
                class="appearance-none block w-full px-4 py-3.5 border border-gray-200 dark:border-slate-700/50 rounded-2xl shadow-sm transition-all sm:text-sm outline-none bg-white dark:bg-slate-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
              />
            </div>

            <!-- Buttons -->
            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="closeModal"
                class="flex-1 py-3.5 rounded-2xl border border-gray-200 dark:border-slate-700/50 text-gray-600 dark:text-slate-400 font-black text-sm uppercase tracking-widest hover:bg-gray-50 dark:hover:bg-slate-800 transition-all"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="flex-1 py-3.5 rounded-2xl bg-emerald-600 text-white font-black text-sm uppercase tracking-widest shadow-lg shadow-emerald-500/20 hover:-translate-y-0.5 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <span
                  v-if="isSubmitting"
                  class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"
                ></span>
                {{ isSubmitting ? 'Saving...' : isEditing ? 'Update' : 'Add Medicine' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- Delete Confirmation Modal                                           -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div
        v-if="isDeleteConfirmOpen"
        class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-slate-900/60 backdrop-blur-sm"
        @click.self="closeDelete"
      >
        <div
          class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-gray-100 dark:border-slate-800 max-w-md w-full p-10 shadow-premium-xl text-center"
        >
          <div
            class="w-16 h-16 bg-rose-100 dark:bg-rose-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6 text-rose-500"
          >
            <svg
              class="h-8 w-8"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </div>
          <h3 class="text-2xl font-black text-gray-900 dark:text-white mb-2">Delete Medicine?</h3>
          <p class="text-gray-500 dark:text-slate-400 mb-8">
            This action is permanent and cannot be undone. The medicine will be removed from the
            inventory.
          </p>
          <div class="flex gap-3">
            <button
              @click="closeDelete"
              class="flex-1 py-3.5 rounded-2xl border border-gray-200 dark:border-slate-700/50 text-gray-600 dark:text-slate-400 font-black text-sm uppercase tracking-widest hover:bg-gray-50 dark:hover:bg-slate-800 transition-all"
            >
              Cancel
            </button>
            <button
              @click="confirmDelete"
              :disabled="isSubmitting"
              class="flex-1 py-3.5 rounded-2xl bg-rose-500 text-white font-black text-sm uppercase tracking-widest shadow-lg shadow-rose-500/20 hover:-translate-y-0.5 transition-all disabled:opacity-60 flex items-center justify-center gap-2"
            >
              <span
                v-if="isSubmitting"
                class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"
              ></span>
              {{ isSubmitting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </DashboardLayout>
</template>
