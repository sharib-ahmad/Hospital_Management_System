<script setup lang="ts">
import { RouterLink } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-slate-900 transition-colors duration-300">
    <!-- Navigation -->
    <nav
      class="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-gray-100 dark:border-slate-800"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 text-white"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="m12 14 4-4" />
                <path d="M3.34 19a10 10 0 1 1 17.32 0" />
              </svg>
            </div>
            <span class="text-xl font-bold text-gray-900 dark:text-white tracking-tight"
              >MediFlow <span class="text-blue-700 dark:text-blue-400">HMS</span></span
            >
          </div>
          <div class="hidden md:flex items-center gap-8">
            <a
              href="#features"
              class="text-sm font-medium text-gray-700 dark:text-slate-300 hover:text-blue-700 dark:hover:text-blue-400 transition-colors"
              >Features</a
            >
            <a
              href="#services"
              class="text-sm font-medium text-gray-700 dark:text-slate-300 hover:text-blue-700 dark:hover:text-blue-400 transition-colors"
              >Services</a
            >
            <a
              href="#roles"
              class="text-sm font-medium text-gray-700 dark:text-slate-300 hover:text-blue-700 dark:hover:text-blue-400 transition-colors"
              >Portals</a
            >
          </div>
          <div class="flex items-center gap-4">
            <ThemeToggle />
            <template v-if="!auth.isAuthenticated">
              <RouterLink
                :to="{ name: 'login' }"
                class="text-sm font-semibold text-gray-800 dark:text-slate-200 hover:text-blue-700 dark:hover:text-blue-400"
                >Log in</RouterLink
              >
              <RouterLink
                :to="{ name: 'register' }"
                class="bg-blue-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:bg-blue-700 transition-all shadow-md hover:shadow-lg active:scale-95"
              >
                Get Started
              </RouterLink>
            </template>
            <template v-else>
              <RouterLink
                :to="{ name: `${auth.user?.role}-portal` }"
                class="bg-blue-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:bg-blue-700 transition-all shadow-md hover:shadow-lg active:scale-95"
              >
                Dashboard
              </RouterLink>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <main>
      <!-- Hero Section -->
      <header class="relative pt-20 pb-32 overflow-hidden">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div class="text-center">
            <div
              class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs font-bold uppercase tracking-wider mb-6"
            >
              <span class="relative flex h-2 w-2">
                <span
                  class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"
                ></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-700"></span>
              </span>
              Next Gen Health Management
            </div>
            <h1
              class="text-5xl md:text-7xl font-extrabold text-gray-900 dark:text-white mb-8 leading-tight"
            >
              Streamlining Healthcare <br />
              <span
                class="text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-indigo-700 dark:from-blue-400 dark:to-indigo-400"
                >for Everyone.</span
              >
            </h1>
            <p
              class="text-xl text-gray-700 dark:text-slate-300 mb-10 max-w-2xl mx-auto leading-relaxed"
            >
              A comprehensive, modular Hospital Management System designed to connect patients,
              doctors, and staff seamlessly. Replace paperwork with digital efficiency.
            </p>

            <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
              <RouterLink
                :to="{ name: 'register' }"
                class="w-full sm:w-auto bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-blue-700 transition-all shadow-xl hover:shadow-blue-200 active:scale-95"
              >
                Book an Appointment
              </RouterLink>
              <a
                href="#features"
                class="w-full sm:w-auto bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 border border-gray-200 dark:border-slate-700 px-8 py-4 rounded-xl text-lg font-bold hover:bg-gray-50 dark:hover:bg-slate-700 transition-all active:scale-95"
              >
                Explore Features
              </a>
            </div>
          </div>
        </div>

        <!-- Background elements -->
        <div
          class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-0 pointer-events-none"
        >
          <div
            class="absolute top-20 left-10 w-72 h-72 bg-blue-100 dark:bg-blue-900/20 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"
          ></div>
          <div
            class="absolute top-40 right-10 w-72 h-72 bg-indigo-100 dark:bg-indigo-900/20 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"
          ></div>
          <div
            class="absolute -bottom-20 left-40 w-72 h-72 bg-sky-100 dark:bg-sky-900/20 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"
          ></div>
        </div>
      </header>

      <!-- Stats Section -->
      <section class="py-12 bg-blue-700">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div class="text-center text-white">
              <div class="text-3xl font-bold mb-1">50+</div>
              <div class="text-blue-100 text-sm">Specialized Doctors</div>
            </div>
            <div class="text-center text-white">
              <div class="text-3xl font-bold mb-1">10k+</div>
              <div class="text-blue-100 text-sm">Happy Patients</div>
            </div>
            <div class="text-center text-white">
              <div class="text-3xl font-bold mb-1">15+</div>
              <div class="text-blue-100 text-sm">Departments</div>
            </div>
            <div class="text-center text-white">
              <div class="text-3xl font-bold mb-1">24/7</div>
              <div class="text-blue-100 text-sm">Emergency Support</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Role Portals -->
      <section id="roles" class="py-24 bg-gray-50 dark:bg-slate-900/50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-16">
            <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Portals Designed for You
            </h2>
            <p class="text-gray-700 dark:text-slate-400">
              Access your personalized workspace based on your role.
            </p>
          </div>

          <div class="grid md:grid-cols-3 gap-8">
            <!-- Patient Portal -->
            <div
              class="group bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all border border-gray-100 dark:border-slate-700"
            >
              <div
                class="w-14 h-14 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-8 w-8"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Patient Portal</h3>
              <p class="text-gray-700 dark:text-slate-400 mb-6">
                Book appointments, view medical history, and track your prescriptions with ease.
              </p>
              <RouterLink
                :to="{ name: 'login' }"
                class="inline-flex items-center text-green-700 dark:text-green-400 font-bold hover:gap-2 transition-all"
              >
                Access Portal
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5 ml-1"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </RouterLink>
            </div>

            <!-- Doctor Portal -->
            <div
              class="group bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all border border-gray-100 dark:border-slate-700"
            >
              <div
                class="w-14 h-14 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-8 w-8"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Doctor Portal</h3>
              <p class="text-gray-700 dark:text-slate-400 mb-6">
                Manage patient consultations, update medical records, and view your daily schedule.
              </p>
              <RouterLink
                :to="{ name: 'login' }"
                class="inline-flex items-center text-blue-700 dark:text-blue-400 font-bold hover:gap-2 transition-all"
              >
                Access Portal
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5 ml-1"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </RouterLink>
            </div>

            <!-- Admin/Staff Portal -->
            <div
              class="group bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all border border-gray-100 dark:border-slate-700"
            >
              <div
                class="w-14 h-14 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-8 w-8"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <line x1="9" y1="3" x2="9" y2="21" />
                  <line x1="15" y1="3" x2="15" y2="21" />
                  <line x1="3" y1="9" x2="21" y2="9" />
                  <line x1="3" y1="15" x2="21" y2="15" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Staff Portal</h3>
              <p class="text-gray-700 dark:text-slate-400 mb-6">
                Handle registrations, billing, and manage overall hospital resources and
                departments.
              </p>
              <RouterLink
                :to="{ name: 'login' }"
                class="inline-flex items-center text-purple-700 dark:text-purple-400 font-bold hover:gap-2 transition-all"
              >
                Access Portal
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5 ml-1"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </RouterLink>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer
      class="bg-white dark:bg-slate-900 border-t border-gray-100 dark:border-slate-800 pt-16 pb-8"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-4 gap-12 mb-12">
          <div class="col-span-1 md:col-span-1">
            <div class="flex items-center gap-2 mb-6">
              <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5 text-white"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="m12 14 4-4" />
                  <path d="M3.34 19a10 10 0 1 1 17.32 0" />
                </svg>
              </div>
              <span class="text-xl font-bold text-gray-900 dark:text-white">MediFlow</span>
            </div>
            <p class="text-gray-700 dark:text-slate-400 text-sm leading-relaxed">
              Leading the digital transformation in healthcare management. Quality care starts with
              quality systems.
            </p>
          </div>
          <div>
            <h4 class="font-bold text-gray-900 dark:text-white mb-6">System</h4>
            <ul class="space-y-4 text-sm text-gray-700 dark:text-slate-400">
              <li>
                <a href="#" class="hover:text-blue-700 dark:hover:text-blue-400">Departments</a>
              </li>
              <li><a href="#" class="hover:text-blue-700 dark:hover:text-blue-400">Doctors</a></li>
              <li><a href="#" class="hover:text-blue-700 dark:hover:text-blue-400">Services</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-bold text-gray-900 dark:text-white mb-6">Support</h4>
            <ul class="space-y-4 text-sm text-gray-700 dark:text-slate-400">
              <li>
                <a href="#" class="hover:text-blue-700 dark:hover:text-blue-400">Help Center</a>
              </li>
              <li>
                <a href="#" class="hover:text-blue-700 dark:hover:text-blue-400">Contact Us</a>
              </li>
              <li>
                <a href="#" class="hover:text-blue-700 dark:hover:text-blue-400">Privacy Policy</a>
              </li>
            </ul>
          </div>
          <div>
            <h4 class="font-bold text-gray-900 dark:text-white mb-6">Contact</h4>
            <ul class="space-y-4 text-sm text-gray-700 dark:text-slate-400">
              <li class="flex items-center gap-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"
                  />
                </svg>
                +1 (555) 000-0000
              </li>
              <li class="flex items-center gap-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"
                  />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
                contact@mediflow.com
              </li>
            </ul>
          </div>
        </div>
        <div
          class="border-t border-gray-100 dark:border-slate-800 pt-8 flex flex-col md:row justify-between items-center gap-4"
        >
          <p class="text-xs text-gray-500 dark:text-slate-500">
            © 2026 MediFlow HMS. All rights reserved.
          </p>
          <div class="flex gap-6">
            <!-- Social icons placeholder -->
            <div class="w-5 h-5 bg-gray-200 dark:bg-slate-800 rounded-full"></div>
            <div class="w-5 h-5 bg-gray-200 dark:bg-slate-800 rounded-full"></div>
            <div class="w-5 h-5 bg-gray-200 dark:bg-slate-800 rounded-full"></div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.animate-blob {
  animation: blob 7s infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}
.animation-delay-4000 {
  animation-delay: 4s;
}

@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}
</style>
