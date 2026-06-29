<template>
  <aside class="w-64 bg-white border-r border-slate-200 flex flex-col">
    <!-- Logo -->
    <div class="p-6 border-b border-slate-200">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-sky-100 flex items-center justify-center">
          <FileText class="w-6 h-6 text-sky-600" />
        </div>
        <div>
          <h1 class="font-bold text-slate-900">Pengaduan</h1>
          <p class="text-xs text-slate-500">Sistem Pengaduan UIR</p>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-4">
      <ul class="space-y-1">
        <li v-for="item in navItems" :key="item.path">
          <router-link
            :to="item.path"
            class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors"
            :class="isActive(item.path)
              ? 'bg-sky-50 text-sky-700 border-l-4 border-sky-600 -ml-1 pl-5'
              : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'"
          >
            <component :is="item.icon" :size="18" />
            {{ item.label }}
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- User Info & Logout -->
    <div class="p-4 border-t border-slate-200">
      <div class="flex items-center gap-3 mb-3">
        <div class="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center">
          <User class="w-4 h-4 text-sky-600" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-900 truncate">{{ userName }}</p>
          <p class="text-xs text-slate-500">Mahasiswa</p>
        </div>
      </div>
      <button
        @click="handleLogout"
        class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
      >
        <LogOut :size="18" />
        Keluar
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard,
  FileText,
  PlusCircle,
  History,
  User,
  LogOut
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.name || 'Mahasiswa')

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/complaints/new', label: 'Buat Pengaduan', icon: PlusCircle },
  { path: '/history', label: 'Riwayat', icon: History }
]

const isActive = (path) => {
  if (path === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(path)
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>