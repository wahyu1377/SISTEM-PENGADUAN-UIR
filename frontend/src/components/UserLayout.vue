<template>
  <div class="min-h-screen bg-slate-900 flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-950 text-white flex-shrink-0 flex flex-col fixed h-screen">
      <!-- Logo -->
      <div class="p-6 border-b border-slate-800">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-sky-600 flex items-center justify-center">
            <FileText class="w-6 h-6" />
          </div>
          <div>
            <h1 class="font-bold text-white">Pengaduan</h1>
            <p class="text-xs text-slate-400">Mahasiswa UIR</p>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 overflow-y-auto">
        <ul class="space-y-1">
          <li v-for="item in navItems" :key="item.path">
            <router-link
              :to="item.path"
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors"
              :class="isActive(item.path)
                ? 'bg-sky-600 text-white'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'"
            >
              <component :is="item.icon" :size="18" />
              {{ item.label }}
            </router-link>
          </li>
        </ul>
      </nav>

      <!-- User Info & Logout -->
      <div class="p-4 border-t border-slate-800">
        <router-link
          to="/profile"
          class="flex items-center gap-3 mb-3 p-2 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <div class="w-8 h-8 rounded-full bg-sky-600 flex items-center justify-center">
            <span class="text-sm font-medium text-white">{{ userInitial }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ userName }}</p>
            <p class="text-xs text-slate-400">Lihat Profil</p>
          </div>
        </router-link>
        <button
          @click="handleLogout"
          class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/20 transition-colors"
        >
          <LogOut :size="18" />
          Keluar
        </button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 ml-64">
      <!-- Top Header Bar -->
      <header class="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6 sticky top-0 z-10">
        <div class="flex items-center gap-4">
          <h2 class="text-lg font-semibold text-white">{{ pageTitle }}</h2>
        </div>
        <div class="flex items-center gap-4">
          <span class="text-sm text-slate-400">{{ currentDate }}</span>
          <div class="w-8 h-8 rounded-full bg-sky-600 flex items-center justify-center">
            <span class="text-sm font-medium text-white">{{ userInitial }}</span>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="bg-slate-900 min-h-[calc(100vh-4rem)]">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard,
  FileText,
  PlusCircle,
  History,
  LogOut,
  UserCircle
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.name || 'Mahasiswa')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())
const currentDate = computed(() => format(new Date(), 'dd MMM yyyy', { locale: id }))

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': 'Dashboard',
    '/profile': 'Profil Saya',
    '/complaints/new': 'Buat Pengaduan',
    '/history': 'Riwayat'
  }
  if (route.path.startsWith('/complaints/') && route.path !== '/complaints/new') {
    return 'Detail Pengaduan'
  }
  return titles[route.path] || 'Dashboard'
})

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/profile', label: 'Profil', icon: UserCircle },
  { path: '/complaints/new', label: 'Buat Pengaduan', icon: PlusCircle },
  { path: '/history', label: 'Riwayat', icon: History }
]

const isActive = (path) => {
  if (path === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(path)
}

// Frontend production URL
const FRONTEND_URL = 'https://uir-complaints-frontend.onrender.com'

// Simple logout using full URL - most reliable method
const handleLogout = () => {
  // Clear all auth data first
  localStorage.removeItem('token')
  authStore.user = null
  authStore.token = null

  // Use full URL to ensure correct navigation
  window.location.replace(FRONTEND_URL + '/login')
}

// Skip auth check on mount to avoid unnecessary API calls
onMounted(async () => {
  // Don't auto-check auth on mount - let the route guards handle it
})
</script>
