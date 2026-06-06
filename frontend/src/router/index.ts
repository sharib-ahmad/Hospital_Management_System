import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LandingView from '../views/LandingView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import NotFoundView from '../views/NotFoundView.vue'

// Portals
import AdminPortal from '../views/portals/AdminPortal.vue'
import DoctorPortal from '../views/portals/DoctorPortal.vue'
import DoctorAppointments from '../views/portals/DoctorAppointments.vue'
import NursePortal from '../views/portals/NursePortal.vue'
import UserPortal from '../views/portals/UserPortal.vue'

// Admin Pages
import DepartmentManagement from '../views/admin/DepartmentManagement.vue'
import UserManagement from '../views/admin/UserManagement.vue'
import ApplicationManagement from '../views/ApplicationManagement.vue'

// Application Pages
import ApplyForRole from '../views/ApplyForRole.vue'
import RegisterPatient from '../views/RegisterPatient.vue'

// MediStore Pharmacy Pages
import MediStore from '../views/MediStore.vue'
import MyBasket from '../views/MyBasket.vue'
import OrderManagement from '../views/admin/OrderManagement.vue'
import MedicineManagement from '../views/admin/MedicineManagement.vue'

// Profile & Standalone Pages
import DoctorProfile from '../views/doctor/DoctorProfile.vue'
import NurseProfile from '../views/nurse/NurseProfile.vue'
import PharmacistProfile from '../views/pharmacist/PharmacistProfile.vue'
import UserAppointments from '../views/user/UserAppointments.vue'
import UserMedicalRecords from '../views/user/UserMedicalRecords.vue'
import PatientVitalsDetailView from '../views/PatientVitalsDetailView.vue'

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
      path: '/admin/users',
      name: 'admin-users',
      component: UserManagement,
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/applications/management',
      name: 'application-management',
      component: ApplicationManagement,
      meta: { requiresAuth: true, roles: ['admin', 'doctor', 'nurse'] },
    },
    {
      path: '/doctor',
      name: 'doctor-portal',
      component: DoctorPortal,
      meta: { requiresAuth: true, role: 'doctor' },
    },
    {
      path: '/doctor/appointments',
      name: 'doctor-appointments',
      component: DoctorAppointments,
      meta: { requiresAuth: true, role: 'doctor' },
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
    {
      path: '/register-patient',
      name: 'register-patient',
      component: RegisterPatient,
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/store',
      name: 'medistore',
      component: MediStore,
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/store/basket',
      name: 'my-basket',
      component: MyBasket,
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/pharmacist',
      name: 'pharmacist-portal',
      redirect: '/pharmacist/medicines',
      meta: { requiresAuth: true, role: 'pharmacist' },
    },
    {
      path: '/pharmacist/orders',
      name: 'pharmacist-orders',
      component: OrderManagement,
      meta: { requiresAuth: true, role: 'pharmacist' },
    },
    {
      path: '/pharmacist/medicines',
      name: 'pharmacist-medicines',
      component: MedicineManagement,
      meta: { requiresAuth: true, role: 'pharmacist' },
    },
    {
      path: '/pharmacist/profile',
      name: 'pharmacist-profile',
      component: PharmacistProfile,
      meta: { requiresAuth: true, role: 'pharmacist' },
    },
    {
      path: '/doctor/profile',
      name: 'doctor-profile',
      component: DoctorProfile,
      meta: { requiresAuth: true, role: 'doctor' },
    },
    {
      path: '/doctor/records',
      name: 'doctor-records',
      component: DoctorPortal,
      meta: { requiresAuth: true, role: 'doctor' },
    },
    {
      path: '/nurse/patients',
      name: 'nurse-patients',
      component: NursePortal,
      meta: { requiresAuth: true, role: 'nurse' },
    },
    {
      path: '/nurse/profile',
      name: 'nurse-profile',
      component: NurseProfile,
      meta: { requiresAuth: true, role: 'nurse' },
    },
    {
      path: '/user/appointments',
      name: 'user-appointments',
      component: UserAppointments,
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/user/records',
      name: 'user-records',
      component: UserMedicalRecords,
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/patients/:id',
      name: 'patient-details-stats',
      component: PatientVitalsDetailView,
      meta: { requiresAuth: true },
    },
    // Catch-all 404
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
    },
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login' })
  } else if (
    (to.meta.role && auth.user?.role !== to.meta.role) ||
    (to.meta.roles && !Array.isArray(to.meta.roles)
      ? false
      : (to.meta.roles as string[])?.length > 0 &&
        !(to.meta.roles as string[]).includes(auth.user?.role || ''))
  ) {
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
