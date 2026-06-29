import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: { guest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: () => import('@/pages/UserProfilePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/complaints/new',
    name: 'NewComplaint',
    component: () => import('@/pages/NewComplaintPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/pages/History.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/complaints/:id',
    name: 'ComplaintDetail',
    component: () => import('@/pages/ComplaintDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  // Admin routes
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/pages/admin/DashboardPage.vue'),
    meta: { requiresAuth: true, admin: true }
  },
  {
    path: '/admin/complaints',
    name: 'AdminComplaints',
    component: () => import('@/pages/admin/ComplaintsPage.vue'),
    meta: { requiresAuth: true, admin: true }
  },
  {
    path: '/admin/complaints/:id',
    name: 'AdminComplaintDetail',
    component: () => import('@/pages/admin/AdminComplaintDetail.vue'),
    meta: { requiresAuth: true, admin: true }
  },
  {
    path: '/admin/documents',
    name: 'AdminDocuments',
    component: () => import('@/pages/admin/DocumentsPage.vue'),
    meta: { requiresAuth: true, admin: true }
  },
  {
    path: '/admin/statistics',
    name: 'AdminStatistics',
    component: () => import('@/pages/admin/StatisticsPage.vue'),
    meta: { requiresAuth: true, admin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  const isAdmin = authStore.isAdmin

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && isAuthenticated) {
    next('/dashboard')
  } else if (to.meta.admin && !isAdmin) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
