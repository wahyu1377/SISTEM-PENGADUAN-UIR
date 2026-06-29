<template>
  <div class="min-h-screen bg-slate-900 flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-950 text-white flex-shrink-0 flex flex-col fixed h-screen">
      <!-- Logo -->
      <div class="p-6 border-b border-slate-800">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-sky-600 flex items-center justify-center">
            <Shield class="w-6 h-6" />
          </div>
          <div>
            <h1 class="font-bold text-white">Admin Panel</h1>
            <p class="text-xs text-slate-400">Sistem Pengaduan UIR</p>
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

      <!-- User Info -->
      <div class="p-4 border-t border-slate-800">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center">
            <User class="w-4 h-4 text-slate-300" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ userName }}</p>
            <p class="text-xs text-slate-400">Administrator</p>
          </div>
          <button
            @click="logout"
            class="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut class="w-4 h-4" />
          </button>
        </div>
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
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard,
  FileText,
  BookOpen,
  BarChart3,
  Shield,
  User,
  LogOut
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'

const route = useRoute()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.name || 'Admin')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())
const currentDate = computed(() => format(new Date(), 'dd MMM yyyy', { locale: id }))

const pageTitle = computed(() => {
  const titles = {
    '/admin': 'Dashboard',
    '/admin/complaints': 'Kelola Pengaduan',
    '/admin/documents': 'Dokumen RAG',
    '/admin/statistics': 'Statistik'
  }
  return titles[route.path] || 'Dashboard'
})

const navItems = [
  { path: '/admin', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/admin/complaints', label: 'Kelola Pengaduan', icon: FileText },
  { path: '/admin/documents', label: 'Dokumen RAG', icon: BookOpen },
  { path: '/admin/statistics', label: 'Statistik', icon: BarChart3 }
]

const isActive = (path) => {
  if (path === '/admin') return route.path === '/admin'
  return route.path.startsWith(path)
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.checkAuth()
  }
})

const logout = () => {
  authStore.logout()
  window.location.href = '/login'
}
</script>
