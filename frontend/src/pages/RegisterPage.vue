<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 py-12 px-4">
    <div class="max-w-md w-full">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-slate-900">Daftar Akun Baru</h1>
        <p class="mt-2 text-sm text-slate-500">Sistem Pengaduan Mahasiswa UIR</p>
      </div>

      <!-- Card -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label for="reg-name" class="block text-sm font-medium text-slate-700 mb-1">
              Nama Lengkap
            </label>
            <input
              id="reg-name"
              v-model="form.name"
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
              v-model="form.npm"
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
              v-model="form.email"
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
              v-model="form.password"
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
              v-model="form.confirm_password"
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
            class="w-full py-2.5 px-4 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 focus:ring-4 focus:ring-sky-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="loading"
          >
            {{ loading ? 'Memproses...' : 'Daftar' }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-slate-600">
            Sudah punya akun?
            <router-link to="/login" class="text-sky-600 hover:underline font-medium">
              Masuk di sini
            </router-link>
          </p>
        </div>
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

const form = ref({
  name: '',
  npm: '',
  email: '',
  password: '',
  confirm_password: ''
})

const loading = ref(false)
const error = ref('')

const onlyNumbers = (event) => {
  const char = String.fromCharCode(event.keyCode)
  if (!/^[0-9]$/.test(char)) {
    event.preventDefault()
  }
}

const handleRegister = async () => {
  if (form.value.password !== form.value.confirm_password) {
    error.value = 'Password tidak cocok'
    return
  }

  if (form.value.npm && form.value.npm.length < 8) {
    error.value = 'NPM harus minimal 8 digit'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await authStore.register(form.value)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registrasi gagal'
  } finally {
    loading.value = false
  }
}
</script>
