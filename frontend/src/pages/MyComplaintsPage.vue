<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center space-x-8">
            <router-link to="/complaints" class="text-xl font-bold text-primary-600">
              Sistem Pengaduan
            </router-link>
            <router-link to="/complaints" class="text-gray-600 hover:text-primary-600">
              Pengaduan Saya
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-gray-600">{{ userName }}</span>
            <button @click="handleLogout" class="btn btn-secondary text-sm">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900">Pengaduan Saya</h1>
        <router-link to="/complaints/new" class="btn btn-primary">
          + Pengaduan Baru
        </router-link>
      </div>

      <!-- Filters -->
      <div class="card p-4 mb-6">
        <div class="flex flex-wrap gap-4">
          <select v-model="filters.status" class="input w-auto">
            <option value="">Semua Status</option>
            <option value="pending">Pending</option>
            <option value="analyzing">Menganalisis</option>
            <option value="reviewed">Ditinjau</option>
            <option value="forwarded">Diteruskan</option>
            <option value="resolved">Selesai</option>
            <option value="rejected">Ditolak</option>
          </select>
          <input
            v-model="filters.search"
            type="text"
            class="input flex-1"
            placeholder="Cari pengaduan..."
            @keyup.enter="fetchComplaints"
          />
          <button @click="fetchComplaints" class="btn btn-primary">
            Cari
          </button>
        </div>
      </div>

      <!-- Complaints List -->
      <div class="space-y-4">
        <div v-if="loading" class="text-center py-8 text-gray-600">
          Memuat...
        </div>

        <div v-else-if="complaints.length === 0" class="card p-8 text-center">
          <p class="text-gray-600">Belum ada pengaduan</p>
          <router-link to="/complaints/new" class="btn btn-primary mt-4">
            Buat Pengaduan Baru
          </router-link>
        </div>

        <div
          v-else
          v-for="complaint in complaints"
          :key="complaint.id"
          class="card p-6 hover:shadow-md transition-shadow cursor-pointer"
          @click="goToDetail(complaint.id)"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <h3 class="font-semibold text-gray-900">{{ complaint.title }}</h3>
                <span :class="getStatusBadgeClass(complaint.status)" class="badge">
                  {{ formatStatus(complaint.status) }}
                </span>
                <span v-if="complaint.priority" :class="getPriorityBadgeClass(complaint.priority)" class="badge">
                  {{ complaint.priority.toUpperCase() }}
                </span>
              </div>
              <p class="text-gray-600 text-sm line-clamp-2">{{ complaint.description }}</p>
              <div class="flex items-center gap-4 mt-3 text-sm text-gray-500">
                <span v-if="complaint.category">{{ complaint.category }}</span>
                <span>{{ formatDate(complaint.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- AI Analysis Results -->
          <div v-if="complaint.rag_analysis" class="mt-4 pt-4 border-t">
            <p class="text-sm text-gray-600">
              <strong>Rekomendasi Unit:</strong> {{ complaint.rag_analysis.recommended_unit }}
            </p>
            <p class="text-sm text-gray-500 mt-1">
              Confidence: {{ (complaint.rag_analysis.confidence_score * 100).toFixed(0) }}%
            </p>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-8">
        <button
          v-for="page in totalPages"
          :key="page"
          @click="goToPage(page)"
          :class="['btn', currentPage === page ? 'btn-primary' : 'btn-secondary']"
        >
          {{ page }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { complaintAPI } from '../services/api'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'

const router = useRouter()
const authStore = useAuthStore()

const complaints = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 10

const filters = ref({
  status: '',
  search: ''
})

const userName = computed(() => authStore.userName)

onMounted(() => {
  fetchComplaints()
})

async function fetchComplaints() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: perPage
    }
    if (filters.value.status) params.status_filter = filters.value.status
    if (filters.value.search) params.search = filters.value.search

    const response = await complaintAPI.getMyComplaints(params)
    complaints.value = response.data.complaints
    totalPages.value = Math.ceil(response.data.total / perPage)
  } catch (error) {
    console.error('Failed to fetch complaints:', error)
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  currentPage.value = page
  fetchComplaints()
}

function goToDetail(id) {
  router.push(`/complaints/${id}`)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function formatStatus(status) {
  const statusMap = {
    pending: 'Pending',
    analyzing: 'Menganalisis',
    reviewed: 'Ditinjau',
    forwarded: 'Diteruskan',
    resolved: 'Selesai',
    rejected: 'Ditolak'
  }
  return statusMap[status] || status
}

function formatDate(dateStr) {
  return format(new Date(dateStr), 'dd MMM yyyy, HH:mm', { locale: id })
}

function getStatusBadgeClass(status) {
  const classMap = {
    pending: 'badge-pending',
    analyzing: 'badge-analyzing',
    reviewed: 'badge-analyzing',
    forwarded: 'badge-analyzing',
    resolved: 'badge-resolved',
    rejected: 'badge-rejected'
  }
  return classMap[status] || 'badge-pending'
}

function getPriorityBadgeClass(priority) {
  return `badge-${priority}`
}
</script>
