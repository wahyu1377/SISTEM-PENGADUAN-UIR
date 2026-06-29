<template>
  <AdminLayout>
    <div class="p-6">
      <!-- Action Info -->
      <div class="mb-6 flex justify-end">
        <span class="text-sm text-slate-400 self-center">Total: {{ stats.total_documents || 0 }} dokumen</span>
      </div>

      <!-- Stats Overview -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <!-- Total Documents -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-4">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-sky-600/20 rounded-lg">
              <FileText class="w-5 h-5 text-sky-400" />
            </div>
            <div>
              <p class="text-sm text-slate-400">Total Dokumen</p>
              <p class="text-2xl font-bold text-white">{{ stats.total_documents || 0 }}</p>
            </div>
          </div>
        </div>
        <!-- Total Chunks -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-4">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-emerald-600/20 rounded-lg">
              <Layers class="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p class="text-sm text-slate-400">Total Chunks</p>
              <p class="text-2xl font-bold text-white">{{ stats.total_chunks || 0 }}</p>
            </div>
          </div>
        </div>
        <!-- Total Categories -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-4">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-purple-600/20 rounded-lg">
              <Database class="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p class="text-sm text-slate-400">Kategori</p>
              <p class="text-2xl font-bold text-white">{{ stats.total_categories || 0 }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Upload Section -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6 mb-6">
        <h2 class="text-lg font-semibold text-white mb-4">Upload Dokumen Baru</h2>
        <form @submit.prevent="handleUpload" class="flex flex-wrap gap-4 items-end">
          <div class="flex-1 min-w-[300px]">
            <label class="block text-sm font-medium text-slate-300 mb-1">Pilih File</label>
            <input
              type="file"
              @change="handleFileSelect"
              accept=".pdf,.docx,.txt"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm"
              required
            />
            <p class="mt-1 text-xs text-slate-500">Format: PDF, DOCX, TXT (maksimal 10MB)</p>
          </div>
          <div class="w-48">
            <label class="block text-sm font-medium text-slate-300 mb-1">Kategori</label>
            <select
              v-model="uploadForm.category"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm"
              required
            >
              <option value="">Pilih Kategori</option>
              <option value="sop">SOP</option>
              <option value="struktur_organisasi">Struktur Organisasi</option>
              <option value="panduan_layanan">Panduan Layanan</option>
              <option value="lainnya">Lainnya</option>
            </select>
          </div>
          <button
            type="submit"
            :disabled="uploading"
            class="px-6 py-2.5 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 transition-colors disabled:opacity-50"
          >
            {{ uploading ? 'Mengupload...' : 'Upload' }}
          </button>
        </form>
        <div v-if="uploadSuccess" class="mt-4 p-3 rounded-lg bg-emerald-600/20 text-emerald-400 text-sm">
          {{ uploadSuccess }}
        </div>
        <div v-if="uploadError" class="mt-4 p-3 rounded-lg bg-red-600/20 text-red-400 text-sm">
          {{ uploadError }}
        </div>
      </div>

      <!-- Documents List -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-700 flex justify-between items-center">
          <h2 class="text-lg font-semibold text-white">Daftar Dokumen</h2>
          <div class="flex gap-2">
            <select
              v-model="filterCategory"
              @change="loadDocuments"
              class="px-4 py-2 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm"
            >
              <option value="">Semua Kategori</option>
              <option value="sop">SOP</option>
              <option value="struktur_organisasi">Struktur Organisasi</option>
              <option value="panduan_layanan">Panduan Layanan</option>
              <option value="lainnya">Lainnya</option>
            </select>
            <button
              @click="loadDocuments"
              class="p-2 text-slate-400 hover:text-white"
              title="Refresh"
            >
              <RefreshCw class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="p-8 text-center text-slate-400">
          Memuat dokumen...
        </div>

        <!-- Documents Table -->
        <table v-else-if="documents.length > 0" class="w-full">
          <thead class="bg-slate-700/50">
            <tr class="text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              <th class="px-6 py-3">Judul</th>
              <th class="px-6 py-3">Kategori</th>
              <th class="px-6 py-3">Chunks</th>
              <th class="px-6 py-3">Tanggal</th>
              <th class="px-6 py-3">Aksi</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-700">
            <tr
              v-for="doc in documents"
              :key="doc.id"
              class="hover:bg-slate-700/30"
            >
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <FileText class="w-4 h-4 text-slate-400" />
                  <span class="font-medium text-white truncate max-w-xs">{{ doc.title }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-700 text-slate-300">
                  {{ doc.category || 'Lainnya' }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-400">
                {{ doc.chunk_count || 0 }} chunks
              </td>
              <td class="px-6 py-4 text-slate-400">
                {{ formatDate(doc.created_at) }}
              </td>
              <td class="px-6 py-4">
                <div class="flex gap-2">
                  <button
                    @click="viewDocument(doc)"
                    class="text-sky-400 hover:text-sky-300 font-medium text-sm"
                  >
                    Lihat
                  </button>
                  <button
                    @click="deleteDocument(doc.id)"
                    class="text-red-400 hover:text-red-300 font-medium text-sm"
                  >
                    Hapus
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-else class="p-8 text-center">
          <EmptyState
            icon-bg-color="bg-slate-700"
            icon-color="text-slate-400"
            title="Belum Ada Dokumen"
            description="Upload dokumen pertama untuk membangun knowledge base AI."
          />
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="px-6 py-4 border-t border-slate-700 flex justify-between items-center">
          <p class="text-sm text-slate-400">
            Menampilkan {{ (currentPage - 1) * perPage + 1 }} - {{ Math.min(currentPage * perPage, totalItems) }} dari {{ totalItems }}
          </p>
          <div class="flex gap-2">
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-1.5 text-sm rounded-lg border border-slate-600 bg-slate-700 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600"
            >
              Sebelumnya
            </button>
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="goToPage(page)"
              :class="page === currentPage ? 'bg-sky-600 border-sky-600' : 'bg-slate-700 border-slate-600 hover:bg-slate-600'"
              class="px-3 py-1.5 text-sm rounded-lg border text-white"
            >
              {{ page }}
            </button>
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 text-sm rounded-lg border border-slate-600 bg-slate-700 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600"
            >
              Selanjutnya
            </button>
          </div>
        </div>
      </div>

      <!-- Document Detail Modal -->
      <div v-if="selectedDocument" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="selectedDocument = null">
        <div class="bg-slate-800 rounded-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden border border-slate-700">
          <div class="px-6 py-4 border-b border-slate-700 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-white">{{ selectedDocument.title }}</h3>
            <button @click="selectedDocument = null" class="text-slate-400 hover:text-white">
              <X class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 overflow-y-auto max-h-[60vh]">
            <div class="space-y-4">
              <div>
                <p class="text-sm text-slate-400">Kategori</p>
                <p class="font-medium text-white">{{ selectedDocument.category }}</p>
              </div>
              <div>
                <p class="text-sm text-slate-400 mb-2">Konten</p>
                <div class="bg-slate-900 rounded-lg p-4 text-sm text-slate-300 whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {{ selectedDocument.content || 'Konten tidak tersedia' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'
import { documentService } from '@/services/api'
import AdminLayout from '@/components/AdminLayout.vue'
import EmptyState from '@/components/EmptyState.vue'
import {
  FileText,
  Layers,
  Database,
  RefreshCw,
  X
} from 'lucide-vue-next'

const loading = ref(true)
const documents = ref([])
const stats = ref({})
const currentPage = ref(1)
const perPage = ref(10)
const totalItems = ref(0)
const filterCategory = ref('')

const uploadForm = ref({
  file: null,
  category: ''
})
const uploading = ref(false)
const uploadSuccess = ref('')
const uploadError = ref('')
const selectedDocument = ref(null)

const totalPages = computed(() => Math.ceil(totalItems.value / perPage.value) || 1)

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

const formatDate = (date) => {
  return format(new Date(date), 'dd MMM yyyy', { locale: id })
}

const loadStats = async () => {
  try {
    const response = await documentService.getDocuments({ per_page: 1 })
    // Get basic stats from document list response or use default
    stats.value = {
      total_documents: response.data.total || 0,
      total_chunks: 0,
      total_categories: 0
    }
  } catch (e) {
    console.error('Failed to load stats:', e)
    stats.value = { total_documents: 0, total_chunks: 0, total_categories: 0 }
  }
}

const loadDocuments = async (page = 1) => {
  loading.value = true
  try {
    const params = { page, per_page: perPage.value }
    if (filterCategory.value) params.category = filterCategory.value

    const response = await documentService.getDocuments(params)
    documents.value = response.data.documents
    totalItems.value = response.data.total
    currentPage.value = page
  } catch (e) {
    console.error('Failed to load documents:', e)
  } finally {
    loading.value = false
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    uploadForm.value.file = file
  }
}

const handleUpload = async () => {
  if (!uploadForm.value.file || !uploadForm.value.category) {
    uploadError.value = 'Pilih file dan kategori terlebih dahulu'
    return
  }

  uploading.value = true
  uploadSuccess.value = ''
  uploadError.value = ''

  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    formData.append('category', uploadForm.value.category)

    await documentService.uploadDocument(formData)
    uploadSuccess.value = 'Dokumen berhasil diupload dan diproses!'
    uploadForm.value = { file: null, category: '' }
    await loadDocuments()
    await loadStats()
  } catch (e) {
    uploadError.value = e.response?.data?.detail || 'Gagal mengupload dokumen'
  } finally {
    uploading.value = false
  }
}

const viewDocument = async (doc) => {
  try {
    const response = await documentService.getDocument(doc.id)
    selectedDocument.value = response.data
  } catch (e) {
    console.error('Failed to load document:', e)
  }
}

const deleteDocument = async (id) => {
  if (!confirm('Apakah Anda yakin ingin menghapus dokumen ini?')) return

  try {
    await documentService.deleteDocument(id)
    await loadDocuments()
    await loadStats()
  } catch (e) {
    console.error('Failed to delete document:', e)
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    loadDocuments(page)
  }
}

onMounted(() => {
  loadDocuments()
  loadStats()
})
</script>