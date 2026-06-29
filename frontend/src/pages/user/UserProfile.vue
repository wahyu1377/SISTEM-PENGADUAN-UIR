<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-white mb-2">Profil Saya</h1>
      <p class="text-slate-400">Kelola informasi akun dan keamanan Anda</p>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="mb-6 p-4 bg-emerald-500/20 border border-emerald-500/50 rounded-lg">
      <p class="text-emerald-400 text-sm">{{ successMessage }}</p>
    </div>
    <div v-if="errorMessage" class="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
      <p class="text-red-400 text-sm">{{ errorMessage }}</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column: Profile Info & Edit Form -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Profile Info Card -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
          <div class="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-white">Informasi Profil</h2>
            <button
              v-if="!isEditing"
              @click="startEditing"
              class="flex items-center gap-2 px-3 py-1.5 text-sm text-sky-400 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <Edit2 :size="16" />
              Edit Profil
            </button>
          </div>

          <!-- View Mode -->
          <div v-if="!isEditing" class="p-6">
            <div class="flex items-start gap-6">
              <!-- Avatar -->
              <div class="w-20 h-20 rounded-full bg-sky-600 flex items-center justify-center flex-shrink-0">
                <span class="text-2xl font-bold text-white">{{ userInitial }}</span>
              </div>

              <!-- Info -->
              <div class="flex-1 space-y-4">
                <div>
                  <label class="text-xs text-slate-500 uppercase tracking-wider">Nama Lengkap</label>
                  <p class="text-white font-medium mt-1">{{ profile.name }}</p>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label class="text-xs text-slate-500 uppercase tracking-wider">Email</label>
                    <p class="text-white font-medium mt-1">{{ profile.email }}</p>
                  </div>
                  <div>
                    <label class="text-xs text-slate-500 uppercase tracking-wider">NPM</label>
                    <p class="text-white font-medium mt-1">{{ profile.npm || '-' }}</p>
                  </div>
                </div>
                <div>
                  <label class="text-xs text-slate-500 uppercase tracking-wider">Role</label>
                  <p class="text-white font-medium mt-1 capitalize">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-sky-500/20 text-sky-400">
                      {{ profile.role === 'mahasiswa' ? 'Mahasiswa' : 'Administrator' }}
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Edit Mode -->
          <div v-else class="p-6">
            <form @submit.prevent="handleUpdateProfile" class="space-y-4">
              <div>
                <label class="block text-sm text-slate-300 mb-2">Nama Lengkap</label>
                <input
                  v-model="editForm.name"
                  type="text"
                  class="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-colors"
                  placeholder="Masukkan nama lengkap"
                />
              </div>

              <div>
                <label class="block text-sm text-slate-300 mb-2">Email</label>
                <input
                  v-model="editForm.email"
                  type="email"
                  class="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-colors"
                  placeholder="Masukkan email"
                  disabled
                />
                <p class="text-xs text-slate-500 mt-1">Email tidak dapat diubah</p>
              </div>

              <div>
                <label class="block text-sm text-slate-300 mb-2">NPM</label>
                <input
                  v-model="editForm.npm"
                  type="text"
                  class="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-colors"
                  placeholder="Masukkan NPM"
                />
              </div>

              <div class="flex items-center gap-3 pt-4">
                <button
                  type="submit"
                  :disabled="isUpdating"
                  class="px-4 py-2 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
                >
                  <Loader2 v-if="isUpdating" :size="16" class="animate-spin" />
                  Simpan Perubahan
                </button>
                <button
                  type="button"
                  @click="cancelEditing"
                  class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Batal
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Change Password Card -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
          <div class="px-6 py-4 border-b border-slate-700">
            <h2 class="text-lg font-semibold text-white">Ubah Password</h2>
            <p class="text-sm text-slate-400 mt-1">Pastikan password Anda sulit ditebak</p>
          </div>

          <div class="p-6">
            <form @submit.prevent="handleChangePassword" class="space-y-4">
              <div>
                <label class="block text-sm text-slate-300 mb-2">Password Saat Ini</label>
                <div class="relative">
                  <input
                    v-model="passwordForm.current_password"
                    :type="showCurrentPassword ? 'text' : 'password'"
                    class="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-colors pr-10"
                    placeholder="Masukkan password saat ini"
                  />
                  <button
                    type="button"
                    @click="showCurrentPassword = !showCurrentPassword"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                  >
                    <EyeOff v-if="showCurrentPassword" :size="18" />
                    <Eye v-else :size="18" />
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm text-slate-300 mb-2">Password Baru</label>
                  <div class="relative">
                    <input
                      v-model="passwordForm.new_password"
                      :type="showNewPassword ? 'text' : 'password'"
                      class="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-colors pr-10"
                      placeholder="Minimal 8 karakter"
                    />
                    <button
                      type="button"
                      @click="showNewPassword = !showNewPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                    >
                      <EyeOff v-if="showNewPassword" :size="18" />
                      <Eye v-else :size="18" />
                    </button>
                  </div>
                </div>

                <div>
                  <label class="block text-sm text-slate-300 mb-2">Konfirmasi Password</label>
                  <div class="relative">
                    <input
                      v-model="passwordForm.confirm_password"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      class="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-colors pr-10"
                      placeholder="Ulangi password baru"
                    />
                    <button
                      type="button"
                      @click="showConfirmPassword = !showConfirmPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                    >
                      <EyeOff v-if="showConfirmPassword" :size="18" />
                      <Eye v-else :size="18" />
                    </button>
                  </div>
                </div>
              </div>

              <!-- Password Strength Indicator -->
              <div v-if="passwordForm.new_password">
                <div class="flex items-center gap-2 mb-2">
                  <div class="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      :class="passwordStrength.color"
                      :style="{ width: passwordStrength.width }"
                      class="h-full transition-all duration-300"
                    ></div>
                  </div>
                  <span class="text-xs" :class="passwordStrength.textColor">{{ passwordStrength.label }}</span>
                </div>
              </div>

              <button
                type="submit"
                :disabled="isChangingPassword || !isPasswordFormValid"
                class="px-4 py-2 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
              >
                <Loader2 v-if="isChangingPassword" :size="16" class="animate-spin" />
                Ubah Password
              </button>
            </form>
          </div>
        </div>
      </div>

      <!-- Right Column: Stats & Quick Info -->
      <div class="space-y-6">
        <!-- Account Stats -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
          <div class="px-6 py-4 border-b border-slate-700">
            <h2 class="text-lg font-semibold text-white">Statistik Akun</h2>
          </div>
          <div class="p-6 space-y-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center">
                  <FileText :size="18" class="text-sky-400" />
                </div>
                <span class="text-sm text-slate-300">Total Pengaduan</span>
              </div>
              <span class="text-lg font-semibold text-white">{{ stats.totalComplaints }}</span>
            </div>

            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                  <CheckCircle :size="18" class="text-emerald-400" />
                </div>
                <span class="text-sm text-slate-300">Selesai</span>
              </div>
              <span class="text-lg font-semibold text-emerald-400">{{ stats.resolvedComplaints }}</span>
            </div>

            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                  <Clock :size="18" class="text-amber-400" />
                </div>
                <span class="text-sm text-slate-300">Pending</span>
              </div>
              <span class="text-lg font-semibold text-amber-400">{{ stats.pendingComplaints }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
          <div class="px-6 py-4 border-b border-slate-700">
            <h2 class="text-lg font-semibold text-white">Aksi Cepat</h2>
          </div>
          <div class="p-4 space-y-2">
            <router-link
              to="/complaints/new"
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
            >
              <PlusCircle :size="18" />
              Buat Pengaduan Baru
            </router-link>
            <router-link
              to="/history"
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
            >
              <History :size="18" />
              Lihat Riwayat
            </router-link>
          </div>
        </div>

        <!-- Member Since -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div class="flex items-center gap-3 mb-3">
            <Calendar :size="18" class="text-slate-400" />
            <span class="text-sm text-slate-400">Anggota Sejak</span>
          </div>
          <p class="text-lg font-semibold text-white">{{ memberSince }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authService, complaintService } from '@/services/api'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'
import {
  Edit2,
  Eye,
  EyeOff,
  Loader2,
  FileText,
  CheckCircle,
  Clock,
  PlusCircle,
  History,
  Calendar
} from 'lucide-vue-next'

const authStore = useAuthStore()

// State
const profile = ref({
  id: '',
  name: '',
  email: '',
  npm: '',
  role: '',
  created_at: ''
})

const editForm = ref({
  name: '',
  email: '',
  npm: ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const isEditing = ref(false)
const isUpdating = ref(false)
const isChangingPassword = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const stats = ref({
  totalComplaints: 0,
  resolvedComplaints: 0,
  pendingComplaints: 0
})

// Computed
const userInitial = computed(() => profile.value.name?.charAt(0).toUpperCase() || 'U')

const memberSince = computed(() => {
  if (!profile.value.created_at) return '-'
  return format(new Date(profile.value.created_at), 'dd MMMM yyyy', { locale: id })
})

const isPasswordFormValid = computed(() => {
  return (
    passwordForm.value.current_password.length >= 1 &&
    passwordForm.value.new_password.length >= 8 &&
    passwordForm.value.new_password === passwordForm.value.confirm_password
  )
})

const passwordStrength = computed(() => {
  const password = passwordForm.value.new_password
  if (!password) return { width: '0%', label: '', color: '', textColor: '' }

  let strength = 0
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++
  if (/[A-Z]/.test(password)) strength++
  if (/[0-9]/.test(password)) strength++
  if (/[^A-Za-z0-9]/.test(password)) strength++

  const levels = [
    { width: '20%', label: 'Sangat Lemah', color: 'bg-red-500', textColor: 'text-red-400' },
    { width: '40%', label: 'Lemah', color: 'bg-orange-500', textColor: 'text-orange-400' },
    { width: '60%', label: 'Sedang', color: 'bg-yellow-500', textColor: 'text-yellow-400' },
    { width: '80%', label: 'Kuat', color: 'bg-emerald-500', textColor: 'text-emerald-400' },
    { width: '100%', label: 'Sangat Kuat', color: 'bg-sky-500', textColor: 'text-sky-400' }
  ]

  return levels[Math.min(strength, 4)]
})

// Methods
const loadProfile = async () => {
  try {
    const response = await authService.getMe()
    profile.value = response.data
    editForm.value = {
      name: response.data.name,
      email: response.data.email,
      npm: response.data.npm || ''
    }
  } catch (error) {
    showError('Gagal memuat profil')
  }
}

const loadStats = async () => {
  try {
    const response = await complaintService.getMyComplaints({ per_page: 1 })
    const complaints = response.data.data || []

    // Get counts from response
    stats.value.totalComplaints = response.data.total || complaints.length

    // For simplicity, count from current page (in real app, add specific endpoint)
    stats.value.resolvedComplaints = complaints.filter(c => c.status === 'selesai').length
    stats.value.pendingComplaints = complaints.filter(c => c.status === 'pending' || c.status === 'diproses').length
  } catch (error) {
    // Stats are non-critical, just log
    console.error('Failed to load stats:', error)
  }
}

const startEditing = () => {
  editForm.value = {
    name: profile.value.name,
    email: profile.value.email,
    npm: profile.value.npm || ''
  }
  isEditing.value = true
}

const cancelEditing = () => {
  isEditing.value = false
}

const handleUpdateProfile = async () => {
  if (!editForm.value.name.trim()) {
    showError('Nama tidak boleh kosong')
    return
  }

  isUpdating.value = true
  clearMessages()

  try {
    await authService.updateProfile({
      name: editForm.value.name,
      npm: editForm.value.npm
    })

    profile.value.name = editForm.value.name
    profile.value.npm = editForm.value.npm

    // Update auth store
    authStore.user = { ...authStore.user, name: editForm.value.name, npm: editForm.value.npm }

    isEditing.value = false
    showSuccess('Profil berhasil diperbarui')
  } catch (error) {
    showError(error.response?.data?.detail || 'Gagal memperbarui profil')
  } finally {
    isUpdating.value = false
  }
}

const handleChangePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    showError('Password baru tidak cocok')
    return
  }

  if (passwordForm.value.new_password.length < 8) {
    showError('Password minimal 8 karakter')
    return
  }

  isChangingPassword.value = true
  clearMessages()

  try {
    await authService.changePassword({
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password
    })

    // Reset form
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }

    showSuccess('Password berhasil diubah')
  } catch (error) {
    showError(error.response?.data?.detail || 'Gagal mengubah password')
  } finally {
    isChangingPassword.value = false
  }
}

const showSuccess = (message) => {
  successMessage.value = message
  errorMessage.value = ''
  setTimeout(() => { successMessage.value = '' }, 5000)
}

const showError = (message) => {
  errorMessage.value = message
  successMessage.value = ''
  setTimeout(() => { errorMessage.value = '' }, 5000)
}

const clearMessages = () => {
  successMessage.value = ''
  errorMessage.value = ''
}

// Lifecycle
onMounted(() => {
  loadProfile()
  loadStats()
})
</script>