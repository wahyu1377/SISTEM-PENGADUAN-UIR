<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Kelola Pengaduan</h1>
      <p class="text-slate-500">Lihat dan proses semua pengaduan mahasiswa</p>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl border border-slate-200 p-4 mb-6">
      <div class="flex flex-wrap gap-4">
        <select
          v-model="filters.status"
          class="px-4 py-2 rounded-lg border border-slate-300 text-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none"
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
          class="px-4 py-2 rounded-lg border border-slate-300 text-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none"
          @change="loadComplaints"
        >
          <option value="">Semua Prioritas</option>
          <option value="high">Tinggi</option>
          <option value="medium">Sedang</option>
          <option value="low">Rendah</option>
        </select>
        <select
          v-model="filters.category"
          class="px-4 py-2 rounded-lg border border-slate-300 text-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none"
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
              class="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-300 text-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-200 outline-none"
              @input="debouncedSearch"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-slate-500">
        Memuat...
      </div>
      <table v-else-if="complaints.length > 0" class="w-full">
        <thead class="bg-slate-50">
          <tr class="text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
            <th class="px-6 py-3">Judul</th>
            <th class="px-6 py-3">Mahasiswa</th>
            <th class="px-6 py-3">Kategori</th>
            <th class="px-6 py-3">Prioritas</th>
            <th class="px-6 py-3">Status</th>
            <th class="px-6 py-3">Tanggal</th>
            <th class="px-6 py-3">Aksi</th>
          </tr>
        </thead>
        <tbody class="text-sm divide-y divide-slate-100">
          <tr
            v-for="complaint in complaints"
            :key="complaint.id"
            class="hover:bg-slate-50"
          >
            <td class="px-6 py-4">
              <p class="font-medium text-slate-900">{{ complaint.title }}</p>
            </td>
            <td class="px-6 py-4">
              <p class="text-slate-900">{{ complaint.user_name }}</p>
              <p class="text-xs text-slate-500">{{ complaint.user_npm }}</p>
            </td>
            <td class="px-6 py-4 text-slate-600">
              {{ complaint.category || '-' }}
            </td>
            <td class="px-6 py-4">
              <StatusBadge
                v-if="complaint.priority"
                :status="complaint.priority"
                type="priority"
              />
              <span v-else class="text-slate-400">-</span>
            </td>
            <td class="px-6 py-4">
              <StatusBadge :status="complaint.status" type="status" />
            </td>
            <td class="px-6 py-4 text-slate-500">
              {{ formatDate(complaint.created_at) }}
            </td>
            <td class="px-6 py-4">
              <router-link
                :to="`/admin/complaints/${complaint.id}`"
                class="text-sky-600 hover:text-sky-700 font-medium"
              >
                Detail
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="p-8">
        <EmptyState
          icon-bg-color="bg-slate-100"
          icon-color="text-slate-400"
          title="Tidak Ada Pengaduan"
          description="Pengaduan yang sesuai filter tidak ditemukan."
        />
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-6 py-4 border-t border-slate-200 flex justify-center gap-2">
        <button
          v-for="page in totalPages"
          :key="page"
          @click="goToPage(page)"
          :class="page === currentPage
            ? 'bg-sky-600 text-white'
            : 'bg-white text-slate-600 hover:bg-slate-50'"
          class="px-4 py-2 text-sm font-medium rounded-lg border border-slate-300 transition-colors"
        >
          {{ page }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { complaintService } from '@/services/api'
import StatusBadge from '@/components/StatusBadge.vue'
import EmptyState from '@/components/EmptyState.vue'
import { Search } from 'lucide-vue-next'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'

const route = useRoute()

const loading = ref(true)
const complaints = ref([])
const totalPages = ref(1)
const currentPage = ref(1)

const filters = ref({
  status: '',
  priority: '',
  category: '',
  search: ''
})

let searchTimeout = null

const formatDate = (date) => {
  return format(new Date(date), 'dd MMM yyyy', { locale: id })
}

const loadComplaints = async (page = 1) => {
  loading.value = true
  try {
    const params = { page, per_page: 20 }
    if (filters.value.status) params.status_filter = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.search) params.search = filters.value.search

    const response = await complaintService.getAllComplaints(params)
    complaints.value = response.data.complaints
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

onMounted(() => {
  // Apply filters from URL if present
  if (route.query.status) filters.value.status = route.query.status
  if (route.query.priority) filters.value.priority = route.query.priority
  if (route.query.category) filters.value.category = route.query.category

  loadComplaints()
})
</script>
