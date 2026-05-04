<script setup lang="ts">
import { RouterLink } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const footerLinks = [
  { title: 'System', links: ['Departments', 'Doctors', 'Services', 'Patient Care'] },
  { title: 'Company', links: ['About Us', 'Careers', 'Security', 'Compliance'] },
  { title: 'Support', links: ['Help Center', 'API Status', 'Privacy', 'Terms'] }
]
</script>

<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-[#06141b] transition-colors duration-500 selection:bg-emerald-100 selection:text-emerald-900">
    <!-- Navigation -->
    <nav class="sticky top-0 z-50 glass border-b border-white/40 dark:border-white/5">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-20 items-center">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20 rotate-3 group hover:rotate-0 transition-transform cursor-pointer">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="m12 14 4-4" />
                <path d="M3.34 19a10 10 0 1 1 17.32 0" />
              </svg>
            </div>
            <span class="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
              Medi<span class="text-emerald-600">Flow</span>
            </span>
          </div>
          
          <div class="hidden md:flex items-center gap-10">
            <a href="#features" class="text-sm font-bold text-gray-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all uppercase tracking-widest">Features</a>
            <a href="#services" class="text-sm font-bold text-gray-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all uppercase tracking-widest">Services</a>
            <a href="#roles" class="text-sm font-bold text-gray-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all uppercase tracking-widest">Portals</a>
          </div>

          <div class="flex items-center gap-6">
            <ThemeToggle />
            <div class="h-6 w-px bg-gray-200 dark:bg-slate-800"></div>
            <template v-if="!auth.isAuthenticated">
              <RouterLink :to="{ name: 'login' }" class="text-sm font-bold text-gray-900 dark:text-white hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors uppercase tracking-widest">Login</RouterLink>
              <RouterLink :to="{ name: 'register' }" class="bg-emerald-600 text-white px-7 py-3 rounded-2xl text-sm font-black hover:bg-emerald-700 transition-all shadow-xl shadow-emerald-500/25 hover:-translate-y-0.5 active:scale-95 uppercase tracking-widest">
                Join Now
              </RouterLink>
            </template>
            <template v-else>
              <RouterLink :to="{ name: `${auth.user?.role}-portal` }" class="bg-emerald-600 text-white px-7 py-3 rounded-2xl text-sm font-black hover:bg-emerald-700 transition-all shadow-xl shadow-emerald-500/25 hover:-translate-y-0.5 active:scale-95 uppercase tracking-widest">
                Dashboard
              </RouterLink>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <main>
      <!-- Hero Section -->
      <header class="relative pt-32 pb-48 overflow-hidden">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div class="text-center">
            <div class="inline-flex items-center gap-3 px-4 py-2 rounded-2xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 text-[10px] font-black uppercase tracking-[0.2em] mb-10 border border-emerald-100/50 dark:border-emerald-500/20">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
              </span>
              Modern HealthcareOS
            </div>
            
            <h1 class="text-6xl md:text-8xl font-black text-gray-900 dark:text-white mb-10 leading-[0.9] tracking-tighter">
              Healthcare <br />
              <span class="text-transparent bg-clip-text bg-gradient-to-br from-emerald-600 via-teal-600 to-emerald-400 dark:from-emerald-400 dark:to-teal-400">Simplified.</span>
            </h1>
            
            <p class="text-lg text-gray-500 dark:text-slate-400 mb-14 max-w-2xl mx-auto leading-relaxed font-medium">
              Experience the next generation of hospital management. A seamless ecosystem connecting patients, doctors, and staff through intuitive digital workflows.
            </p>

            <div class="flex flex-col sm:flex-row items-center justify-center gap-6">
              <RouterLink :to="{ name: 'register' }" class="group w-full sm:w-auto bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-10 py-5 rounded-2xl text-lg font-black hover:shadow-2xl transition-all hover:-translate-y-1 active:scale-95 flex items-center justify-center gap-3">
                Get Started
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </RouterLink>
              <a href="#features" class="w-full sm:w-auto glass text-gray-900 dark:text-white border border-white/40 dark:border-white/5 px-10 py-5 rounded-2xl text-lg font-black hover:bg-gray-50 dark:hover:bg-slate-800 transition-all hover:-translate-y-1 active:scale-95 shadow-sm">
                Explore Platform
              </a>
            </div>
          </div>
        </div>

        <!-- Decorative Blobs -->
        <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 pointer-events-none">
          <div class="absolute top-20 left-[10%] w-[500px] h-[500px] bg-emerald-200/30 dark:bg-emerald-600/10 rounded-full mix-blend-multiply filter blur-[120px] animate-blob"></div>
          <div class="absolute bottom-20 right-[10%] w-[500px] h-[500px] bg-teal-200/30 dark:bg-teal-600/10 rounded-full mix-blend-multiply filter blur-[120px] animate-blob animation-delay-2000"></div>
          <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-100/20 dark:bg-emerald-600/5 rounded-full mix-blend-multiply filter blur-[120px] animate-blob animation-delay-4000"></div>
        </div>
      </header>

      <!-- Trusted By Section -->
      <section class="py-20 border-y border-gray-100 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p class="text-center text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-12">Empowering Global Healthcare Leaders</p>
          <div class="flex flex-wrap justify-center items-center gap-12 md:gap-24 opacity-50 grayscale hover:grayscale-0 transition-all duration-700">
            <div class="text-2xl font-black text-gray-900 dark:text-white flex items-center gap-2 italic">
              <div class="w-6 h-6 bg-red-500 rounded"></div> HEALTH+
            </div>
            <div class="text-2xl font-black text-gray-900 dark:text-white flex items-center gap-2 italic">
              <div class="w-6 h-6 bg-blue-500 rounded-full"></div> LIFECARE
            </div>
            <div class="text-2xl font-black text-gray-900 dark:text-white flex items-center gap-2 italic">
              <div class="w-6 h-6 bg-green-500 rotate-45"></div> MEDX
            </div>
            <div class="text-2xl font-black text-gray-900 dark:text-white flex items-center gap-2 italic">
              <div class="w-6 h-6 bg-emerald-500 rounded-lg"></div> VITALITY
            </div>
          </div>
        </div>
      </section>

      <!-- Portals Grid -->
      <section id="roles" class="py-32">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex flex-col md:flex-row md:items-end justify-between mb-20 gap-8">
            <div class="max-w-2xl">
              <h2 class="text-5xl font-black text-gray-900 dark:text-white mb-6 tracking-tight leading-none">Custom Experience <br/> For Every Role.</h2>
              <p class="text-lg text-gray-500 dark:text-slate-400 font-medium">Deeply integrated portals designed to empower every stakeholder in the healthcare ecosystem.</p>
            </div>
            <div class="flex gap-4">
              <div class="h-14 w-14 rounded-2xl bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
            </div>
          </div>

          <div class="grid md:grid-cols-3 gap-10">
            <!-- Patient Portal -->
            <div class="group glass p-10 rounded-[2.5rem] shadow-premium hover:shadow-premium-xl transition-all duration-500 border border-white/40 dark:border-white/5 flex flex-col h-full">
              <div class="w-16 h-16 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-3xl flex items-center justify-center mb-10 group-hover:-rotate-6 transition-transform">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 class="text-2xl font-black text-gray-900 dark:text-white mb-4">Patient Portal</h3>
              <p class="text-gray-500 dark:text-slate-400 mb-10 font-medium leading-relaxed">Book appointments, view medical history, and track prescriptions with complete transparency.</p>
              <div class="mt-auto">
                <RouterLink :to="{ name: 'login' }" class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-black uppercase text-xs tracking-[0.2em] group/link">
                  Enter Workspace
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 group-hover/link:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7" /></svg>
                </RouterLink>
              </div>
            </div>

            <!-- Doctor Portal -->
            <div class="group glass p-10 rounded-[2.5rem] shadow-premium hover:shadow-premium-xl transition-all duration-500 border border-white/40 dark:border-white/5 flex flex-col h-full">
              <div class="w-16 h-16 bg-teal-100 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400 rounded-3xl flex items-center justify-center mb-10 group-hover:rotate-6 transition-transform">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 class="text-2xl font-black text-gray-900 dark:text-white mb-4">Doctor Portal</h3>
              <p class="text-gray-500 dark:text-slate-400 mb-10 font-medium leading-relaxed">Advanced clinical tools to manage consultations, schedules, and complex medical records efficiently.</p>
              <div class="mt-auto">
                <RouterLink :to="{ name: 'login' }" class="flex items-center gap-2 text-teal-600 dark:text-teal-400 font-black uppercase text-xs tracking-[0.2em] group/link">
                  Enter Workspace
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 group-hover/link:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7" /></svg>
                </RouterLink>
              </div>
            </div>

            <!-- Admin Portal -->
            <div class="group glass p-10 rounded-[2.5rem] shadow-premium hover:shadow-premium-xl transition-all duration-500 border border-white/40 dark:border-white/5 flex flex-col h-full">
              <div class="w-16 h-16 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-3xl flex items-center justify-center mb-10 group-hover:-rotate-6 transition-transform">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
              </div>
              <h3 class="text-2xl font-black text-gray-900 dark:text-white mb-4">Admin Portal</h3>
              <p class="text-gray-500 dark:text-slate-400 mb-10 font-medium leading-relaxed">Full system governance including resource orchestration, staff management, and analytics.</p>
              <div class="mt-auto">
                <RouterLink :to="{ name: 'login' }" class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-black uppercase text-xs tracking-[0.2em] group/link">
                  Enter Workspace
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 group-hover/link:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7" /></svg>
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="glass border-t border-white/40 dark:border-white/5 pt-24 pb-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-4 gap-16 mb-24">
          <div class="col-span-1 md:col-span-1">
            <div class="flex items-center gap-3 mb-8">
              <div class="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m12 14 4-4" />
                  <path d="M3.34 19a10 10 0 1 1 17.32 0" />
                </svg>
              </div>
              <span class="text-2xl font-black text-gray-900 dark:text-white">MediFlow</span>
            </div>
            <p class="text-gray-500 dark:text-slate-400 text-sm leading-relaxed font-medium">
              Architecting the digital foundation of modern healthcare. Built for performance, security, and human care.
            </p>
          </div>
          
          <div v-for="col in footerLinks" :key="col.title">
            <h4 class="text-xs font-black text-gray-900 dark:text-white uppercase tracking-[0.2em] mb-8">{{ col.title }}</h4>
            <ul class="space-y-4">
              <li v-for="link in col.links" :key="link">
                <a href="#" class="text-sm font-bold text-gray-500 dark:text-slate-500 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors">{{ link }}</a>
              </li>
            </ul>
          </div>
        </div>
        
        <div class="border-t border-white/40 dark:border-white/5 pt-12 flex flex-col md:flex-row justify-between items-center gap-8">
          <p class="text-[10px] font-black text-gray-400 dark:text-slate-600 uppercase tracking-[0.2em]">
            © 2026 MediFlow Systems Inc. All rights reserved.
          </p>
          <div class="flex gap-8">
            <a href="#" class="text-gray-400 hover:text-emerald-600 transition-colors">
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
            </a>
            <a href="#" class="text-gray-400 hover:text-emerald-600 transition-colors">
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            </a>
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
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
</style>
