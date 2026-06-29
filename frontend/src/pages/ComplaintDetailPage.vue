<template>
  <UserLayout>
    <div class="p-6 max-w-4xl">
      <!-- Back Button -->
      <div class="mb-6">
        <button
          @click="goBack"
          class="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg transition-colors"
        >
          <ArrowLeft class="w-4 h-4" />
          Kembali
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
          Kembali ke Riwayat
        </button>
      </div>

      <!-- Complaint Content -->
      <div v-else-if="complaint" class="space-y-6">
        <!-- Main Info -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="text-2xl font-bold text-white">{{ complaint.title }}</h1>
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

        <!-- Attachments Section -->
        <div v-if="complaint.id" class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-white">Lampiran ({{ attachments.length }})</h2>
            <button
              v-if="attachments.length > 0"
              @click="loadAttachments"
              class="text-slate-400 hover:text-white text-sm"
              title="Refresh"
            >
              <RefreshCw class="w-4 h-4" />
            </button>
          </div>

          <!-- Loading -->
          <div v-if="attachmentsLoading" class="text-center py-4 text-slate-400">
            Memuat lampiran...
          </div>

          <!-- Empty -->
          <div v-else-if="attachments.length === 0" class="text-center py-6">
            <File class="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p class="text-slate-500">Tidak ada lampiran</p>
          </div>

          <!-- Attachment List -->
          <div v-else class="space-y-2">
            <div
              v-for="att in attachments"
              :key="att.id"
              class="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg hover:bg-slate-700"
            >
              <div class="flex items-center gap-3">
                <component :is="getFileIcon(att.file_type)" class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-white text-sm font-medium">{{ att.original_filename }}</p>
                  <p class="text-slate-500 text-xs">{{ formatFileSize(att.file_size) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click="downloadAttachment(att.url, att.original_filename)"
                  class="p-2 text-slate-400 hover:text-white"
                  title="Download"
                >
                  <Download class="w-4 h-4" />
                </button>
                <button
                  @click="deleteAttachment(att.id)"
                  class="p-2 text-slate-400 hover:text-red-400"
                  title="Hapus"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Analysis Result -->
        <div v-if="complaint.rag_analysis" class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <h2 class="text-lg font-semibold text-white mb-4">Hasil Analisis AI</h2>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-slate-400">Kategori</p>
                <p class="font-medium text-white">{{ complaint.rag_analysis.category || '-' }}</p>
              </div>
              <div>
                <p class="text-sm text-slate-400">Unit Tujuan</p>
                <p class="font-medium text-white">{{ complaint.rag_analysis.recommended_unit || '-' }}</p>
              </div>
              <div>
                <p class="text-sm text-slate-400">Confidence Score</p>
                <div class="flex items-center gap-2">
                  <div class="flex-1 bg-slate-700 rounded-full h-2">
                    <div
                      class="bg-sky-500 h-2 rounded-full"
                      :style="{ width: `${Math.round((complaint.rag_analysis.confidence_score || 0) * 100)}%` }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium text-white">{{ Math.round((complaint.rag_analysis.confidence_score || 0) * 100) }}%</span>
                </div>
              </div>
              <div>
                <p class="text-sm text-slate-400">Tingkat Kepercayaan</p>
                <p class="font-medium">
                  <span v-if="complaint.rag_analysis.confidence_score >= 0.7" class="text-emerald-400">Tinggi</span>
                  <span v-else-if="complaint.rag_analysis.confidence_score >= 0.4" class="text-amber-400">Sedang</span>
                  <span v-else class="text-red-400">Rendah</span>
                </p>
              </div>
            </div>
            <div v-if="complaint.rag_analysis.summary">
              <p class="text-sm text-slate-400 mb-1">Ringkasan</p>
              <p class="text-slate-300">{{ complaint.rag_analysis.summary }}</p>
            </div>
            <div v-if="complaint.rag_analysis.reason">
              <p class="text-sm text-slate-400 mb-1">Alasan Rekomendasi</p>
              <p class="text-slate-300">{{ complaint.rag_analysis.reason }}</p>
            </div>
          </div>
        </div>

        <!-- Admin Notes -->
        <div v-if="complaint.admin_notes" class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <h2 class="text-lg font-semibold text-white mb-4">Catatan Admin</h2>
          <p class="text-slate-300">{{ complaint.admin_notes }}</p>
        </div>

        <!-- Status Timeline -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <h2 class="text-lg font-semibold text-white mb-4">Timeline</h2>
          <div class="space-y-4">
            <div class="flex items-center gap-4">
              <div class="w-3 h-3 bg-emerald-500 rounded-full flex-shrink-0"></div>
              <div class="flex-1">
                <p class="font-medium text-white">Pengaduan Dibuat</p>
                <p class="text-sm text-slate-500">{{ formattedDate }}</p>
              </div>
            </div>
            <div v-if="complaint.updated_at !== complaint.created_at" class="flex items-center gap-4">
              <div class="w-3 h-3 bg-sky-500 rounded-full flex-shrink-0"></div>
              <div class="flex-1">
                <p class="font-medium text-white">Terakhir Diperbarui</p>
                <p class="text-sm text-slate-500">{{ formatUpdatedDate }}</p>
              </div>
            </div>
            <div v-if="complaint.resolved_at" class="flex items-center gap-4">
              <div class="w-3 h-3 bg-emerald-500 rounded-full flex-shrink-0"></div>
              <div class="flex-1">
                <p class="font-medium text-emerald-400">Selesai</p>
                <p class="text-sm text-slate-500">{{ formatResolvedDate }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </UserLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'
import { complaintService, attachmentService } from '@/services/api'
import UserLayout from '@/components/UserLayout.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { ArrowLeft, AlertCircle, File, Trash2, Download, Image, FileText, RefreshCw } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const complaint = ref(null)
const loading = ref(true)
const error = ref('')
const attachments = ref([])
const attachmentsLoading = ref(false)

const formattedDate = computed(() => {
  if (!complaint.value) return ''
  return format(new Date(complaint.value.created_at), 'dd MMMM yyyy, HH:mm', { locale: id })
})

const formatUpdatedDate = computed(() => {
  if (!complaint.value) return ''
  return format(new Date(complaint.value.updated_at), 'dd MMMM yyyy, HH:mm', { locale: id })
})

const formatResolvedDate = computed(() => {
  if (!complaint.value?.resolved_at) return ''
  return format(new Date(complaint.value.resolved_at), 'dd MMMM yyyy, HH:mm', { locale: id })
})

const getFileIcon = (fileType) => {
  if (!fileType) return FileText
  if (fileType.startsWith('image/')) return Image
  return FileText
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

const loadAttachments = async () => {
  if (!complaint.value?.id) return
  attachmentsLoading.value = true
  try {
    const response = await attachmentService.getAttachments(complaint.value.id)
    attachments.value = response.data.attachments || []
  } catch (e) {
    console.error('Failed to load attachments:', e)
    attachments.value = []
  } finally {
    attachmentsLoading.value = false
  }
}

const deleteAttachment = async (attachmentId) => {
  if (!confirm('Apakah Anda yakin ingin menghapus lampiran ini?')) return
  try {
    await attachmentService.deleteAttachment(attachmentId)
    await loadAttachments()
  } catch (e) {
    console.error('Failed to delete attachment:', e)
    alert('Gagal menghapus lampiran')
  }
}

const downloadAttachment = (url, filename) => {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const goBack = () => {
  if (window.history.length > 2) {
    router.back()
  } else {
    router.push('/history')
  }
}

onMounted(async () => {
  try {
    const response = await complaintService.getComplaint(route.params.id)
    complaint.value = response.data
    await loadAttachments()
  } catch (e) {
    if (e.response?.status === 404) {
      error.value = 'Pengaduan tidak ditemukan atau Anda tidak memiliki akses.'
    } else if (e.response?.status === 401) {
      error.value = 'Sesi telah habis. Silakan login kembali.'
    } else {
      error.value = 'Gagal memuat detail pengaduan.'
    }
    console.error('Failed to load complaint:', e)
  } finally {
    loading.value = false
  }
})
</script>
