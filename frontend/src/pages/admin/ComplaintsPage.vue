<template>
  <AdminLayout>
    <div class="p-6">
      <!-- Action Bar -->
      <div class="mb-6 flex justify-between items-center">
        <span class="text-sm text-slate-400 self-center">Total: {{ totalItems }} pengaduan</span>
        <div class="flex gap-2">
          <button
            @click="exportCSV"
            :disabled="exporting"
            class="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
          >
            <Download v-if="!exporting" class="w-4 h-4" />
            <Loader v-else class="w-4 h-4 animate-spin" />
            {{ exporting ? 'Mengunduh...' : 'Export CSV' }}
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-4 mb-6">
        <div class="flex flex-wrap gap-4">
          <select
            v-model="filters.status"
            class="px-4 py-2 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm focus:border-sky-500 outline-none"
            @change="loadComplaints"
          >
            <option value="">Semua Status</option>
            <option value="pending">Menunggu</option>
            <option value="analyzing">Menganalisis</option>
            <option value="reviewed">Ditinjau</option>
            <option value="forwarded">Diteruskan</option>
            <option value="resolved">Selesai</option>
            <option value="rejected">Ditolak</option>
          </select>
          <select
            v-model="filters.priority"
            class="px-4 py-2 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm focus:border-sky-500 outline-none"
            @change="loadComplaints"
          >
            <option value="">Semua Prioritas</option>
            <option value="high">Tinggi</option>
            <option value="medium">Sedang</option>
            <option value="low">Rendah</option>
          </select>
          <select
            v-model="filters.category"
            class="px-4 py-2 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm focus:border-sky-500 outline-none"
            @change="loadComplaints"
          >
            <option value="">Semua Kategori</option>
            <option value="Akademik">Akademik</option>
            <option value="Fasilitas Kampus">Fasilitas Kampus</option>
            <option value="Perpustakaan">Perpustakaan</option>
            <option value="Teknologi Informasi">Teknologi Informasi</option>
            <option value="Administrasi">Administrasi</option>
            <option value="Lainnya">Lainnya</option>
          </select>
          <div class="flex-1 min-w-[200px]">
            <div class="relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                v-model="filters.search"
                type="text"
                placeholder="Cari pengaduan..."
                class="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm focus:border-sky-500 outline-none"
                @input="debouncedSearch"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div v-if="loading" class="p-8 text-center text-slate-400">
          Memuat...
        </div>
        <table v-else-if="complaints.length > 0" class="w-full">
          <thead class="bg-slate-700/50">
            <tr class="text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              <th class="px-6 py-3">Judul</th>
              <th class="px-6 py-3">Mahasiswa</th>
              <th class="px-6 py-3">Kategori</th>
              <th class="px-6 py-3">Prioritas</th>
              <th class="px-6 py-3">Status</th>
              <th class="px-6 py-3">Tanggal</th>
              <th class="px-6 py-3">Aksi</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-700">
            <tr
              v-for="complaint in complaints"
              :key="complaint.id"
              class="hover:bg-slate-700/30"
            >
              <td class="px-6 py-4">
                <p class="font-medium text-white">{{ complaint.title }}</p>
              </td>
              <td class="px-6 py-4">
                <p class="text-slate-300">{{ complaint.user_name || 'N/A' }}</p>
                <p class="text-xs text-slate-500">{{ complaint.user_npm || '' }}</p>
              </td>
              <td class="px-6 py-4 text-slate-400">
                {{ complaint.category || '-' }}
              </td>
              <td class="px-6 py-4">
                <StatusBadge
                  v-if="complaint.priority"
                  :status="complaint.priority"
                  type="priority"
                />
                <span v-else class="text-slate-500">-</span>
              </td>
              <td class="px-6 py-4">
                <StatusBadge :status="complaint.status" type="status" />
              </td>
              <td class="px-6 py-4 text-slate-400">
                {{ formatDate(complaint.created_at) }}
              </td>
              <td class="px-6 py-4">
                <router-link
                  :to="`/admin/complaints/${complaint.id}`"
                  class="text-sky-400 hover:text-sky-300 font-medium"
                >
                  Detail
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="p-8">
          <EmptyState
            icon-bg-color="bg-slate-700"
            icon-color="text-slate-400"
            title="Tidak Ada Pengaduan"
            description="Pengaduan yang sesuai filter tidak ditemukan."
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
              class="px-3 py-1.5 text-sm font-medium rounded-lg border border-slate-600 bg-slate-700 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600 transition-colors"
            >
              Sebelumnya
            </button>
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="goToPage(page)"
              :class="page === currentPage
                ? 'bg-sky-600 text-white border-sky-600'
                : 'bg-slate-700 text-white border-slate-600 hover:bg-slate-600'"
              class="px-3 py-1.5 text-sm font-medium rounded-lg border transition-colors"
            >
              {{ page }}
            </button>
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 text-sm font-medium rounded-lg border border-slate-600 bg-slate-700 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600 transition-colors"
            >
              Selanjutnya
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { complaintService } from '@/services/api'
import AdminLayout from '@/components/AdminLayout.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import EmptyState from '@/components/EmptyState.vue'
import { Search, Download, Loader } from 'lucide-vue-next'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'

const route = useRoute()

const loading = ref(true)
const exporting = ref(false)
const complaints = ref([])
const totalPages = ref(1)
const totalItems = ref(0)
const currentPage = ref(1)
const perPage = 20

const filters = ref({
  status: '',
  priority: '',
  category: '',
  search: ''
})

let searchTimeout = null

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

const loadComplaints = async (page = 1) => {
  loading.value = true
  try {
    const params = { page, per_page: perPage }
    if (filters.value.status) params.status_filter = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.search) params.search = filters.value.search

    const response = await complaintService.getAllComplaints(params)
    complaints.value = response.data.complaints
    totalItems.value = response.data.total
    totalPages.value = Math.ceil(response.data.total / response.data.per_page) || 1
    currentPage.value = page
  } catch (e) {
    console.error('Failed to load complaints:', e)
  } finally {
    loading.value = false
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => loadComplaints(1), 500)
}

const goToPage = (page) => loadComplaints(page)

const exportCSV = async () => {
  exporting.value = true
  try {
    const params = {}
    if (filters.value.status) params.status_filter = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.category) params.category = filters.value.category

    const response = await complaintService.exportComplaints(params)

    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `laporan_pengaduan_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Export error:', e)
    alert('Gagal export data')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  // Apply filters from URL if present
  if (route.query.status) filters.value.status = route.query.status
  if (route.query.priority) filters.value.priority = route.query.priority
  if (route.query.category) filters.value.category = route.query.category

  loadComplaints()
})
</script>