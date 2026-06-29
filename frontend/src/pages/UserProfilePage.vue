<template>
  <UserLayout>
    <div class="p-6">
      <!-- Profile Header -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6 mb-6">
        <div class="flex items-center gap-6">
          <div class="w-20 h-20 rounded-full bg-sky-600 flex items-center justify-center">
            <span class="text-3xl font-bold text-white">{{ userInitial }}</span>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-white">{{ form.name || 'Pengguna' }}</h1>
            <p class="text-slate-400">{{ user?.email }}</p>
            <span class="inline-block mt-2 px-3 py-1 bg-sky-600/20 text-sky-400 rounded-full text-sm">
              {{ user?.role || 'Mahasiswa' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Profile Form -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6 mb-6">
        <h2 class="text-lg font-semibold text-white mb-6">Informasi Profil</h2>

        <!-- Success Message -->
        <div v-if="showSuccess" class="mb-4 p-3 rounded-lg bg-emerald-600/20 text-emerald-400 text-sm">
          Profil berhasil diperbarui!
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-4 p-3 rounded-lg bg-red-600/20 text-red-400 text-sm">
          {{ error }}
        </div>

        <form @submit.prevent="handleUpdateProfile">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Name -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Nama Lengkap</label>
              <input
                v-model="form.name"
                type="text"
                class="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-sky-500"
                placeholder="Masukkan nama lengkap"
              />
            </div>
            <!-- Email (disabled) -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Email</label>
              <input
                :value="user?.email"
                type="email"
                disabled
                class="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-slate-400 cursor-not-allowed"
              />
              <p class="text-xs text-slate-500 mt-1">Email tidak dapat diubah</p>
            </div>
            <!-- NPM -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">NPM</label>
              <input
                v-model="form.npm"
                type="text"
                class="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-sky-500"
                placeholder="Masukkan NPM"
              />
            </div>
            <!-- Role (disabled) -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Role</label>
              <input
                :value="user?.role === 'admin' ? 'Administrator' : 'Mahasiswa'"
                type="text"
                disabled
                class="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-slate-400 cursor-not-allowed"
              />
            </div>
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="mt-6 px-6 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {{ loading ? 'Menyimpan...' : 'Simpan Perubahan' }}
          </button>
        </form>
      </div>

      <!-- Change Password Section -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
        <h2 class="text-lg font-semibold text-white mb-6">Ubah Password</h2>

        <!-- Success Message -->
        <div v-if="passwordSuccess" class="mb-4 p-3 rounded-lg bg-emerald-600/20 text-emerald-400 text-sm">
          Password berhasil diubah!
        </div>

        <!-- Error Message -->
        <div v-if="passwordError" class="mb-4 p-3 rounded-lg bg-red-600/20 text-red-400 text-sm">
          {{ passwordError }}
        </div>

        <form @submit.prevent="handleChangePassword">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Password Saat Ini</label>
              <div class="relative">
                <input
                  v-model="passwordForm.current_password"
                  :type="showCurrentPassword ? 'text' : 'password'"
                  class="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-sky-500 pr-12"
                  placeholder="Masukkan password saat ini"
                />
                <button
                  type="button"
                  @click="showCurrentPassword = !showCurrentPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  <Eye v-if="showCurrentPassword" class="w-5 h-5" />
                  <EyeOff v-else class="w-5 h-5" />
                </button>
              </div>
            </div>
            <div></div>
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Password Baru</label>
              <div class="relative">
                <input
                  v-model="passwordForm.new_password"
                  :type="showNewPassword ? 'text' : 'password'"
                  class="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-sky-500 pr-12"
                  placeholder="Minimal 8 karakter"
                />
                <button
                  type="button"
                  @click="showNewPassword = !showNewPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  <Eye v-if="showNewPassword" class="w-5 h-5" />
                  <EyeOff v-else class="w-5 h-5" />
                </button>
              </div>
              <!-- Password Strength -->
              <div class="mt-2">
                <div class="flex gap-1">
                  <div
                    v-for="i in 4"
                    :key="i"
                    :class="getPasswordStrength >= i ? strengthColor : 'bg-slate-700'"
                    class="h-1 flex-1 rounded-full transition-colors"
                  ></div>
                </div>
                <p class="text-xs mt-1" :class="strengthTextColor">{{ strengthLabel }}</p>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Konfirmasi Password Baru</label>
              <div class="relative">
                <input
                  v-model="passwordForm.new_password_confirmation"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-sky-500 pr-12"
                  placeholder="Ulangi password baru"
                />
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  <Eye v-if="showConfirmPassword" class="w-5 h-5" />
                  <EyeOff v-else class="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
          <button
            type="submit"
            :disabled="passwordLoading"
            class="mt-6 px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {{ passwordLoading ? 'Menyimpan...' : 'Ubah Password' }}
          </button>
        </form>
      </div>
    </div>
  </UserLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/api'
import UserLayout from '@/components/UserLayout.vue'
import { Eye, EyeOff } from 'lucide-vue-next'

const authStore = useAuthStore()

const user = computed(() => authStore.user)
const userInitial = computed(() => {
  const name = user.value?.name
  if (!name || name.length === 0) return 'U'
  return name.charAt(0).toUpperCase()
})

const form = ref({
  name: '',
  npm: ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  new_password_confirmation: ''
})

// Password visibility toggles
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Loading states
const loading = ref(false)
const passwordLoading = ref(false)

// Success/Error messages
const showSuccess = ref(false)
const error = ref('')
const passwordSuccess = ref(false)
const passwordError = ref('')

// Password strength
const getPasswordStrength = computed(() => {
  const pwd = passwordForm.value.new_password
  if (!pwd) return 0
  let strength = 0
  if (pwd.length >= 8) strength++
  if (/[A-Z]/.test(pwd)) strength++
  if (/[0-9]/.test(pwd)) strength++
  if (/[^A-Za-z0-9]/.test(pwd)) strength++
  return strength
})

const strengthColor = computed(() => {
  const s = getPasswordStrength.value
  if (s <= 1) return 'bg-red-500'
  if (s <= 2) return 'bg-amber-500'
  if (s <= 3) return 'bg-sky-500'
  return 'bg-emerald-500'
})

const strengthLabel = computed(() => {
  const s = getPasswordStrength.value
  if (s === 0) return ''
  if (s <= 1) return 'Lemah'
  if (s <= 2) return 'Sedang'
  if (s <= 3) return 'Cukup Kuat'
  return 'Kuat'
})

const strengthTextColor = computed(() => {
  const s = getPasswordStrength.value
  if (s <= 1) return 'text-red-400'
  if (s <= 2) return 'text-amber-400'
  if (s <= 3) return 'text-sky-400'
  return 'text-emerald-400'
})

onMounted(() => {
  if (user.value) {
    form.value = {
      name: user.value.name || '',
      npm: user.value.npm || ''
    }
  }
})

const handleUpdateProfile = async () => {
  error.value = ''
  loading.value = true
  try {
    const response = await authService.updateProfile(form.value)
    authStore.user = response.data
    showSuccess.value = true
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Gagal memperbarui profil'
    setTimeout(() => {
      error.value = ''
    }, 5000)
  } finally {
    loading.value = false
  }
}

const handleChangePassword = async () => {
  passwordError.value = ''

  if (passwordForm.value.new_password !== passwordForm.value.new_password_confirmation) {
    passwordError.value = 'Password baru tidak cocok'
    return
  }

  if (passwordForm.value.new_password.length < 8) {
    passwordError.value = 'Password minimal 8 karakter'
    return
  }

  passwordLoading.value = true
  try {
    await authService.changePassword({
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password,
      new_password_confirmation: passwordForm.value.new_password_confirmation
    })
    passwordSuccess.value = true
    passwordForm.value = {
      current_password: '',
      new_password: '',
      new_password_confirmation: ''
    }
    setTimeout(() => {
      passwordSuccess.value = false
    }, 3000)
  } catch (e) {
    passwordError.value = e.response?.data?.detail || 'Gagal mengubah password'
    setTimeout(() => {
      passwordError.value = ''
    }, 5000)
  } finally {
    passwordLoading.value = false
  }
}
</script>