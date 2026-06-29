<template>
  <UserLayout>
    <div class="p-6">
      <!-- Header -->
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-white">Riwayat Pengaduan</h1>
        <router-link
          to="/complaints/new"
          class="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700">
          <PlusCircle class="w-5 h-5" />
          Buat Baru
        </router-link>
      </div>

      <!-- Filters -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-4 mb-6">
        <div class="flex gap-4 flex-wrap items-center">
          <!-- Status Filter -->
          <select
            v-model="filters.status"
            class="px-4 py-2 rounded-lg border border-slate-600 bg-slate-700 text-white text-sm"
            @change="loadComplaints">
            <option value="">Semua Status</option>
            <option value="pending">Menunggu</option>
            <option value="analyzing">Menganalisis</option>
            <option value="reviewed">Ditinjau</option>
            <option value="forwarded">Diteruskan</option>
            <option value="resolved">Selesai</option>
            <option value="rejected">Ditolak</option>
          </select>
          <!-- Search Input -->
          <div class="flex-1 min-w-[200px] relative">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              v-model="filters.search"
              type="text"
              placeholder="Cari judul atau deskripsi..."
              class="w-full pl-10 pr-10 py-2 rounded-lg border border-slate-600 bg-slate-700 text-white placeholder-slate-400 text-sm"
              @input="debouncedSearch" />
            <button
              v-if="filters.search"
              @click="clearSearch"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- List -->
      <div class="space-y-4">
        <div v-if="loading" class="text-center py-12 text-slate-400">Memuat...</div>
        <div v-else-if="complaints.length === 0" class="text-center py-12">
          <Inbox class="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-white mb-2">Belum Ada Pengaduan</h3>
          <p class="text-slate-400">Pengaduan kosong.</p>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="complaint in complaints"
            :key="complaint.id"
            class="bg-slate-800 rounded-xl border border-slate-700 p-4">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1">
                <h3 class="font-medium text-white">{{ complaint.title }}</h3>
                <p class="text-sm text-slate-400 line-clamp-2 mt-1">{{ complaint.description }}</p>
                <div class="flex items-center gap-3 mt-2">
                  <span class="text-xs text-slate-500">{{ formatDate(complaint.created_at) }}</span>
                  <StatusBadge v-if="complaint.category" :status="complaint.category" type="category" />
                </div>
              </div>
              <div class="flex flex-col items-end gap-2">
                <StatusBadge :status="complaint.status" type="status" />
                <router-link
                  :to="'/complaints/' + complaint.id"
                  class="text-sm text-sky-400 hover:text-sky-300">Detail</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-6 flex items-center justify-center gap-2">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-4 py-2 rounded-lg border border-slate-600 bg-slate-800 disabled:opacity-50">
          Sebelumnya
        </button>
        <button
          v-for="p in visiblePages"
          :key="p"
          @click="goToPage(p)"
          :class="p === currentPage ? 'bg-sky-600 border-sky-600' : 'bg-slate-800 border-slate-600 hover:bg-slate-700'"
          class="px-4 py-2 rounded-lg border text-white">
          {{ p }}
        </button>
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-4 py-2 rounded-lg border border-slate-600 bg-slate-800 disabled:opacity-50 hover:bg-slate-700">
          Selanjutnya
        </button>
      </div>
    </div>
  </UserLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { complaintService } from '@/services/api'
import UserLayout from '@/components/UserLayout.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { PlusCircle, Inbox, Search, X } from 'lucide-vue-next'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'

const complaints = ref([])
const totalPages = ref(1)
const currentPage = ref(1)
const filters = ref({ status: '', search: '' })
const loading = ref(true)
let timeout = null

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const formatDate = (date) => format(new Date(date), 'dd MMM yyyy', { locale: id })

const loadComplaints = async (page = 1) => {
  loading.value = true
  try {
    const params = { page, per_page: 10 }
    if (filters.value.status) params.status_filter = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    const res = await complaintService.getMyComplaints(params)
    complaints.value = res.data.complaints || []
    totalPages.value = Math.ceil((res.data.total || 0) / (res.data.per_page || 10)) || 1
    currentPage.value = page
  } catch (e) {
    console.error(e)
    complaints.value = []
  } finally {
    loading.value = false
  }
}

const debouncedSearch = () => {
  clearTimeout(timeout)
  timeout = setTimeout(() => loadComplaints(1), 500)
}

const clearSearch = () => {
  filters.value.search = ''
  loadComplaints(1)
}

const goToPage = (page) => loadComplaints(page)

onMounted(() => loadComplaints())
</script>
