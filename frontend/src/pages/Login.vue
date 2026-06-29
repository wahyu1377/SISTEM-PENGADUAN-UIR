<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 py-12 px-4">
    <div class="max-w-md w-full">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-slate-900">Sistem Pengaduan Mahasiswa</h1>
        <p class="mt-2 text-sm text-slate-500">Universitas Islam Riau</p>
      </div>

      <!-- Card -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <!-- Tabs -->
        <div class="flex border-b border-slate-200">
          <button
            @click="tab = 'login'"
            :class="tab === 'login'
              ? 'border-sky-600 text-sky-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'"
            class="flex-1 py-4 text-center text-sm font-medium border-b-2 transition-colors"
          >
            Masuk
          </button>
          <button
            @click="tab = 'register'"
            :class="tab === 'register'
              ? 'border-sky-600 text-sky-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'"
            class="flex-1 py-4 text-center text-sm font-medium border-b-2 transition-colors"
          >
            Daftar
          </button>
        </div>

        <!-- Login Form -->
        <form v-if="tab === 'login'" @submit.prevent="handleLogin" class="p-6 space-y-4">
          <div>
            <label for="login-email" class="block text-sm font-medium text-slate-700 mb-1">
              Email
            </label>
            <input
              id="login-email"
              v-model="loginForm.email"
              type="email"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none transition-all"
              placeholder="email@studenti.uir.ac.id"
              required
            />
          </div>
          <div>
            <label for="login-password" class="block text-sm font-medium text-slate-700 mb-1">
              Password
            </label>
            <input
              id="login-password"
              v-model="loginForm.password"
              type="password"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none transition-all"
              placeholder="Minimal 6 karakter"
              required
            />
          </div>
          <div v-if="error" class="p-3 rounded-lg bg-red-50 text-red-700 text-sm">
            {{ error }}
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-2.5 px-4 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 focus:ring-4 focus:ring-sky-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Memproses...' : 'Masuk' }}
          </button>
        </form>

        <!-- Register Form -->
        <form v-else @submit.prevent="handleRegister" class="p-6 space-y-4">
          <div>
            <label for="reg-name" class="block text-sm font-medium text-slate-700 mb-1">
              Nama Lengkap
            </label>
            <input
              id="reg-name"
              v-model="registerForm.name"
              type="text"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none transition-all"
              placeholder="Nama lengkap sesuai KTP"
              required
            />
          </div>
          <div>
            <label for="reg-npm" class="block text-sm font-medium text-slate-700 mb-1">
              NPM (Nomor Pokok Mahasiswa)
            </label>
            <input
              id="reg-npm"
              v-model="registerForm.npm"
              type="text"
              inputmode="numeric"
              pattern="[0-9]*"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none transition-all"
              placeholder="10 digit NPM"
              maxlength="10"
              @keypress="onlyNumbers"
              required
            />
            <p class="mt-1 text-xs text-slate-500">Hanya menerima angka (0-9)</p>
          </div>
          <div>
            <label for="reg-email" class="block text-sm font-medium text-slate-700 mb-1">
              Email
            </label>
            <input
              id="reg-email"
              v-model="registerForm.email"
              type="email"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none transition-all"
              placeholder="email@studenti.uir.ac.id"
              required
            />
          </div>
          <div>
            <label for="reg-password" class="block text-sm font-medium text-slate-700 mb-1">
              Password
            </label>
            <input
              id="reg-password"
              v-model="registerForm.password"
              type="password"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none transition-all"
              placeholder="Minimal 6 karakter"
              minlength="6"
              required
            />
          </div>
          <div>
            <label for="reg-confirm" class="block text-sm font-medium text-slate-700 mb-1">
              Konfirmasi Password
            </label>
            <input
              id="reg-confirm"
              v-model="registerForm.confirm_password"
              type="password"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none transition-all"
              placeholder="Ulangi password"
              required
            />
          </div>
          <div v-if="error" class="p-3 rounded-lg bg-red-50 text-red-700 text-sm">
            {{ error }}
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-2.5 px-4 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 focus:ring-4 focus:ring-sky-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Memproses...' : 'Daftar' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const tab = ref('login')
const loading = ref(false)
const error = ref('')

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  name: '',
  npm: '',
  email: '',
  password: '',
  confirm_password: ''
})

const onlyNumbers = (event) => {
  const char = String.fromCharCode(event.keyCode)
  if (!/^[0-9]$/.test(char)) {
    event.preventDefault()
  }
}

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(loginForm.value)
    if (authStore.isAdmin) {
      router.push('/admin')
    } else {
      router.push('/dashboard')
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login gagal'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  error.value = ''
  if (registerForm.value.password !== registerForm.value.confirm_password) {
    error.value = 'Password tidak cocok'
    return
  }
  if (registerForm.value.npm && registerForm.value.npm.length < 8) {
    error.value = 'NPM harus minimal 8 digit'
    return
  }
  loading.value = true
  try {
    await authStore.register(registerForm.value)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registrasi gagal'
  } finally {
    loading.value = false
  }
}
</script>
