import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LandingView from '../views/LandingView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

// Portals
import AdminPortal from '../views/portals/AdminPortal.vue'
import DoctorPortal from '../views/portals/DoctorPortal.vue'
import PatientPortal from '../views/portals/PatientPortal.vue'
import NursePortal from '../views/portals/NursePortal.vue'
import UserPortal from '../views/portals/UserPortal.vue'

// Admin Pages
import DepartmentManagement from '../views/admin/DepartmentManagement.vue'
import ApplicationManagement from '../views/ApplicationManagement.vue'

// Application Pages
import ApplyForRole from '../views/ApplyForRole.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    // Role Portals
    {
      path: '/admin',
      name: 'admin-portal',
      component: AdminPortal,
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/departments',
      name: 'admin-departments',
      component: DepartmentManagement,
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/applications',
      name: 'admin-applications',
      component: ApplicationManagement,
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/doctor',
      name: 'doctor-portal',
      component: DoctorPortal,
      meta: { requiresAuth: true, role: 'doctor' },
    },
    {
      path: '/patient',
      name: 'patient-portal',
      component: PatientPortal,
      meta: { requiresAuth: true, role: 'patient' },
    },
    {
      path: '/nurse',
      name: 'nurse-portal',
      component: NursePortal,
      meta: { requiresAuth: true, role: 'nurse' },
    },
    {
      path: '/user',
      name: 'user-portal',
      component: UserPortal,
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/apply',
      name: 'apply',
      component: ApplyForRole,
      meta: { requiresAuth: true, role: 'user' },
    },
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.meta.role && auth.user?.role !== to.meta.role) {
    // Simple role check - redirect to their own portal if they try to access wrong one
    if (auth.isAuthenticated) {
      next({ name: `${auth.user?.role}-portal` })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
