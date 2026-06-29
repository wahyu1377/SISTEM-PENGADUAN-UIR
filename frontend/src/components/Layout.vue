<template>
  <div class="min-h-screen bg-slate-50 flex">
    <!-- Sidebar -->
    <UserSidebar />

    <!-- Main Content -->
    <main class="flex-1 min-w-0">
      <!-- Top Bar -->
      <header class="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-6">
        <div class="flex items-center gap-4">
          <!-- Mobile menu button placeholder -->
        </div>
        <div class="flex items-center gap-4">
          <span class="text-sm text-slate-600">{{ userName }}</span>
          <button
            @click="logout"
            class="p-2 text-slate-400 hover:text-slate-600 transition-colors"
            title="Logout"
          >
            <LogOut class="w-5 h-5" />
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <div class="p-6">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import UserSidebar from './UserSidebar.vue'
import { LogOut } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.name || 'Mahasiswa')

onMounted(async () => {
  if (!authStore.user) {
    await authStore.checkAuth()
  }
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>