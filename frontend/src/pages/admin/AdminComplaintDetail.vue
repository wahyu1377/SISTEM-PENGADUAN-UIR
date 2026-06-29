<template>
  <AdminLayout>
    <div class="p-6">
      <!-- Back Button -->
      <div class="mb-6">
        <button
          @click="goBack"
          class="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg transition-colors"
        >
          <ArrowLeft class="w-4 h-4" />
          Kembali ke Daftar
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-slate-800 rounded-xl border border-slate-700 p-12 text-center">
        <div class="animate-spin w-8 h-8 border-4 border-sky-600 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p class="text-slate-400">Memuat detail pengaduan...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-slate-800 rounded-xl border border-slate-700 p-12 text-center">
        <div class="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertCircle class="w-6 h-6 text-red-400" />
        </div>
        <h3 class="text-lg font-semibold text-white mb-2">Pengaduan Tidak Ditemukan</h3>
        <p class="text-slate-400 mb-6">{{ error }}</p>
        <button
          @click="goBack"
          class="px-4 py-2 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 transition-colors"
        >
          Kembali
        </button>
      </div>

      <!-- Complaint Content -->
      <div v-else-if="complaint" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Main Info -->
          <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h1 class="text-xl font-bold text-white">{{ complaint.title }}</h1>
                <p class="text-sm text-slate-500 mt-1">ID: {{ complaint.id }}</p>
              </div>
              <div class="flex gap-2">
                <StatusBadge v-if="complaint.priority" :status="complaint.priority" type="priority" />
                <StatusBadge :status="complaint.status" type="status" />
              </div>
            </div>
            <p class="text-slate-300 whitespace-pre-wrap mb-4">{{ complaint.description }}</p>
            <div class="pt-4 border-t border-slate-700 text-sm text-slate-500">
              Dikirim: {{ formattedDate }}
            </div>
          </div>

          <!-- AI Analysis -->
          <div v-if="complaint.rag_analysis" class="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold text-white">Hasil Analisis AI</h2>
              <button
                @click="reanalyze"
                :disabled="reanalyzing"
                class="px-3 py-1.5 text-sm bg-slate-700 text-slate-300 font-medium rounded-lg hover:bg-slate-600 transition-colors disabled:opacity-50"
              >
                {{ reanalyzing ? 'Menganalisis...' : 'Analisis Ulang' }}
              </button>
            </div>
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-sm text-slate-400">Kategori</p>
                  <p class="font-medium text-white">{{ complaint.rag_analysis.category || '-' }}</p>
                </div>
                <div>
                  <p class="text-sm text-slate-400">Tingkat Kepercayaan</p>
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-slate-700 rounded-full h-2">
                      <div
                        class="bg-sky-600 h-2 rounded-full"
                        :style="{ width: `${Math.round((complaint.rag_analysis.confidence_score || 0) * 100)}%` }"
                      ></div>
                    </div>
                    <span class="text-sm font-medium text-white">{{ Math.round((complaint.rag_analysis.confidence_score || 0) * 100) }}%</span>
                  </div>
                </div>
              </div>
              <div v-if="complaint.rag_analysis.summary">
                <p class="text-sm text-slate-400">Ringkasan</p>
                <p class="text-slate-300">{{ complaint.rag_analysis.summary }}</p>
              </div>
              <div v-if="complaint.rag_analysis.recommended_unit">
                <p class="text-sm text-slate-400">Unit Rekomendasi</p>
                <p class="font-medium text-white">{{ complaint.rag_analysis.recommended_unit }}</p>
              </div>
              <div v-if="complaint.rag_analysis.reason">
                <p class="text-sm text-slate-400">Alasan</p>
                <p class="text-slate-300">{{ complaint.rag_analysis.reason }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Student Info -->
          <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h2 class="text-lg font-semibold text-white mb-4">Informasi Mahasiswa</h2>
            <div class="space-y-3">
              <div>
                <p class="text-sm text-slate-400">Nama</p>
                <p class="font-medium text-white">{{ complaint.user_name || '-' }}</p>
              </div>
              <div>
                <p class="text-sm text-slate-400">NPM</p>
                <p class="font-medium text-white">{{ complaint.user_npm || '-' }}</p>
              </div>
            </div>
          </div>

          <!-- Update Form -->
          <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h2 class="text-lg font-semibold text-white mb-4">Proses Pengaduan</h2>

            <!-- Success Message -->
            <div v-if="showSuccess" class="mb-4 p-3 rounded-lg bg-emerald-600/20 text-emerald-400 text-sm">
              Perubahan berhasil disimpan!
            </div>

            <!-- Error Message -->
            <div v-if="updateError" class="mb-4 p-3 rounded-lg bg-red-600/20 text-red-400 text-sm">
              {{ updateError }}
            </div>

            <form @submit.prevent="updateComplaint" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">Status</label>
                <select
                  v-model="updateForm.status"
                  class="w-full px-4 py-2.5 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm focus:border-sky-500 outline-none"
                >
                  <option value="pending">Menunggu</option>
                  <option value="reviewed">Ditinjau</option>
                  <option value="forwarded">Diteruskan</option>
                  <option value="resolved">Selesai</option>
                  <option value="rejected">Ditolak</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">Unit Tujuan</label>
                <input
                  v-model="updateForm.assigned_unit"
                  type="text"
                  class="w-full px-4 py-2.5 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm focus:border-sky-500 outline-none"
                  placeholder="Nama unit terkait"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">Catatan Admin</label>
                <textarea
                  v-model="updateForm.admin_notes"
                  class="w-full px-4 py-2.5 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm focus:border-sky-500 outline-none resize-none"
                  rows="3"
                  placeholder="Tambahkan catatan..."
                ></textarea>
              </div>
              <button
                type="submit"
                :disabled="updating"
                class="w-full py-2.5 px-4 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 transition-colors disabled:opacity-50"
              >
                {{ updating ? 'Menyimpan...' : 'Simpan Perubahan' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'
import { complaintService } from '@/services/api'
import AdminLayout from '@/components/AdminLayout.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { ArrowLeft, AlertCircle } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const complaint = ref(null)
const loading = ref(true)
const error = ref('')
const updating = ref(false)
const reanalyzing = ref(false)
const showSuccess = ref(false)
const updateError = ref('')

const updateForm = ref({
  status: 'pending',
  assigned_unit: '',
  admin_notes: ''
})

const formattedDate = computed(() => {
  if (!complaint.value) return ''
  return format(new Date(complaint.value.created_at), 'dd MMMM yyyy, HH:mm', { locale: id })
})

const goBack = () => {
  if (window.history.length > 2) {
    router.back()
  } else {
    router.push('/admin/complaints')
  }
}

const loadComplaint = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await complaintService.getAdminComplaint(route.params.id)
    complaint.value = response.data
    updateForm.value.status = response.data.status || 'pending'
    updateForm.value.assigned_unit = response.data.assigned_unit || ''
    updateForm.value.admin_notes = response.data.admin_notes || ''
  } catch (e) {
    if (e.response?.status === 404) {
      error.value = 'Pengaduan tidak ditemukan.'
    } else if (e.response?.status === 403) {
      error.value = 'Anda tidak memiliki akses ke pengaduan ini.'
    } else {
      error.value = 'Gagal memuat detail pengaduan.'
    }
    console.error('Failed to load complaint:', e)
  } finally {
    loading.value = false
  }
}

const updateComplaint = async () => {
  updating.value = true
  try {
    await complaintService.updateStatus(route.params.id, updateForm.value.status)

    if (updateForm.value.assigned_unit !== complaint.value.assigned_unit ||
        updateForm.value.admin_notes !== complaint.value.admin_notes) {
      await complaintService.updateComplaint(route.params.id, {
        assigned_unit: updateForm.value.assigned_unit,
        admin_notes: updateForm.value.admin_notes
      })
    }

    await loadComplaint()
    showSuccess.value = true
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
  } catch (e) {
    console.error('Failed to update complaint:', e)
    updateError.value = e.response?.data?.detail || 'Gagal menyimpan perubahan'
    setTimeout(() => {
      updateError.value = ''
    }, 5000)
  } finally {
    updating.value = false
  }
}

const reanalyze = async () => {
  reanalyzing.value = true
  try {
    await complaintService.reanalyzeComplaint(route.params.id)
    await loadComplaint()
    showSuccess.value = true
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
  } catch (e) {
    console.error('Failed to reanalyze:', e)
    updateError.value = 'Gagal menganalisis ulang'
    setTimeout(() => {
      updateError.value = ''
    }, 5000)
  } finally {
    reanalyzing.value = false
  }
}

onMounted(loadComplaint)
</script>