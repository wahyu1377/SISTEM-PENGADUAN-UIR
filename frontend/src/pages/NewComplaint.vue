<template>
  <Layout>
    <div class="mb-6 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">Buat Pengaduan Baru</h1>
      <router-link to="/dashboard" class="text-gray-600 hover:text-gray-900">
        Kembali
      </router-link>
    </div>

    <div class="card p-6">
      <form @submit.prevent="submitComplaint" class="space-y-6">
        <div>
          <label class="label">Judul Pengaduan</label>
          <input
            v-model="form.title"
            type="text"
            class="input"
            placeholder="Contoh: AC Ruang Kelas B203 Tidak Berfungsi"
            maxlength="200"
            required
          />
          <div class="text-xs text-gray-500 mt-1">{{ form.title.length }}/200 karakter</div>
        </div>

        <div>
          <label class="label">Deskripsi Pengaduan</label>
          <textarea
            v-model="form.description"
            class="input min-h-[200px]"
            placeholder="Jelaskan pengaduan Anda secara detail. Sertakan informasi seperti lokasi, waktu kejadian, dan pihak terkait."
            maxlength="5000"
            required
          ></textarea>
          <div class="text-xs text-gray-500 mt-1">{{ form.description.length }}/5000 karakter</div>
        </div>

        <div class="flex items-center space-x-4">
          <button type="submit" :disabled="loading" class="btn btn-primary">
            {{ loading ? 'Mengirim...' : 'Kirim Pengaduan' }}
          </button>
          <router-link to="/dashboard" class="btn btn-secondary">
            Batal
          </router-link>
        </div>

        <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>
        <div v-if="success" class="text-green-600 text-sm">Pengaduan berhasil dikirim</div>
      </form>
    </div>

    <!-- Info Box -->
    <div class="mt-6 card p-6 bg-blue-50 border-blue-200">
      <h3 class="font-semibold text-blue-900 mb-2">Informasi</h3>
      <ul class="text-sm text-blue-800 space-y-1">
        <li>- Pengaduan akan dianalisis secara otomatis oleh sistem AI</li>
        <li>- Anda dapat memantau status pengaduan di halaman riwayat</li>
        <li>- Hasil analisis AI akan ditampilkan setelah pengaduan diproses</li>
      </ul>
    </div>
  </Layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { complaintService } from '@/services/api'
import Layout from '@/components/Layout.vue'

const router = useRouter()

const form = ref({
  title: '',
  description: ''
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

const submitComplaint = async () => {
  error.value = ''
  success.value = false
  loading.value = true

  try {
    await complaintService.createComplaint(form.value)
    success.value = true
    setTimeout(() => {
      router.push('/dashboard')
    }, 1500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Gagal mengirim pengaduan'
  } finally {
    loading.value = false
  }
}
</script>
