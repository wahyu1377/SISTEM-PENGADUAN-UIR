<template>
  <UserLayout>
    <div class="p-6">
      <!-- Back Link -->
      <div class="mb-6">
        <router-link
          to="/history"
          class="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg transition-colors"
        >
          <ArrowLeft class="w-4 h-4" />
          Kembali
        </router-link>
      </div>

      <!-- Form Card -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
        <h2 class="text-xl font-semibold text-white mb-6">Form Pengaduan Baru</h2>
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label for="title" class="block text-sm font-medium text-slate-300 mb-1">
              Judul Pengaduan *
            </label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-600 bg-slate-700 text-white placeholder-slate-400 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all"
              placeholder="Contoh: AC Ruang Kelas B203 Tidak Berfungsi"
              maxlength="200"
              required
            />
            <p class="text-sm text-slate-500 mt-1">{{ form.title.length }}/200 karakter</p>
          </div>

          <div>
            <label for="description" class="block text-sm font-medium text-slate-300 mb-1">
              Deskripsi Lengkap *
            </label>
            <textarea
              id="description"
              v-model="form.description"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-600 bg-slate-700 text-white placeholder-slate-400 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all resize-none"
              rows="6"
              placeholder="Jelaskan pengaduan Anda secara detail. Sertakan informasi seperti lokasi, waktu kejadian, dan dampak yang dialami."
              maxlength="5000"
              required
            ></textarea>
            <p class="text-sm text-slate-500 mt-1">{{ form.description.length }}/5000 karakter</p>
          </div>

          <div v-if="error" class="p-3 rounded-lg bg-red-500/20 text-red-400 text-sm">
            {{ error }}
          </div>

          <div v-if="success" class="p-3 rounded-lg bg-emerald-500/20 text-emerald-400 text-sm">
            Pengaduan berhasil dikirim! Mengalihkan ke dashboard...
          </div>

          <!-- Info Box -->
          <div class="bg-sky-600/20 p-4 rounded-lg border border-sky-600/30">
            <p class="text-sm text-sky-300">
              <strong>Catatan:</strong> Setelah dikirim, pengaduan Anda akan dianalisis secara otomatis
              oleh AI untuk menentukan kategori, prioritas, dan unit yang tepat.
            </p>
          </div>

          <div class="flex gap-4">
            <router-link
              to="/history"
              class="flex-1 py-2.5 px-4 text-center border border-slate-600 text-slate-300 font-medium rounded-lg hover:bg-slate-700 transition-colors"
            >
              Batal
            </router-link>
            <button
              type="submit"
              class="flex-1 py-2.5 px-4 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="loading || !isFormValid"
            >
              {{ loading ? 'Mengirim...' : 'Kirim Pengaduan' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </UserLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { complaintService } from '@/services/api'
import UserLayout from '@/components/UserLayout.vue'
import { ArrowLeft } from 'lucide-vue-next'

const router = useRouter()

const form = ref({
  title: '',
  description: ''
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

const isFormValid = computed(() => {
  return form.value.title.length >= 5 && form.value.description.length >= 20
})

const handleSubmit = async () => {
  if (!isFormValid.value) return

  loading.value = true
  error.value = ''
  success.value = false

  try {
    const response = await complaintService.createComplaint({
      title: form.value.title,
      description: form.value.description
    })

    success.value = true

    setTimeout(() => {
      router.push(`/complaints/${response.data.id}`)
    }, 1500)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Gagal mengirim pengaduan'
  } finally {
    loading.value = false
  }
}
</script>
