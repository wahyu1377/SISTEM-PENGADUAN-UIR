<template>
  <div class="max-w-3xl mx-auto">
    <!-- Back Button -->
    <div class="mb-6">
      <button
        @click="goBack"
        class="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
      >
        <ArrowLeft class="w-4 h-4" />
        Kembali
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-xl border border-slate-200 p-12 text-center">
      <div class="animate-spin w-8 h-8 border-4 border-sky-600 border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-slate-500">Memuat detail pengaduan...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-white rounded-xl border border-slate-200 p-12 text-center">
      <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <AlertCircle class="w-6 h-6 text-red-600" />
      </div>
      <h3 class="text-lg font-semibold text-slate-900 mb-2">Pengaduan Tidak Ditemukan</h3>
      <p class="text-slate-500 mb-6">{{ error }}</p>
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
      <div class="bg-white rounded-xl border border-slate-200 p-6">
        <div class="flex justify-between items-start mb-4">
          <h1 class="text-2xl font-bold text-slate-900">{{ complaint.title }}</h1>
          <div class="flex gap-2">
            <StatusBadge v-if="complaint.priority" :status="complaint.priority" type="priority" />
            <StatusBadge :status="complaint.status" type="status" />
          </div>
        </div>
        <p class="text-slate-700 whitespace-pre-wrap">{{ complaint.description }}</p>
        <div class="mt-4 pt-4 border-t border-slate-100 text-sm text-slate-500">
          Dikirim: {{ formattedDate }}
        </div>
      </div>

      <!-- AI Analysis Result -->
      <div v-if="complaint.rag_analysis" class="bg-white rounded-xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">Hasil Analisis AI</h2>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-slate-500">Kategori</p>
              <p class="font-medium text-slate-900">{{ complaint.rag_analysis.category || '-' }}</p>
            </div>
            <div>
              <p class="text-sm text-slate-500">Prioritas</p>
              <p class="font-medium text-slate-900 capitalize">{{ complaint.rag_analysis.priority || '-' }}</p>
            </div>
          </div>
          <div>
            <p class="text-sm text-slate-500">Ringkasan</p>
            <p class="font-medium text-slate-900">{{ complaint.rag_analysis.summary || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-slate-500">Unit Tujuan</p>
            <p class="font-medium text-slate-900">{{ complaint.rag_analysis.recommended_unit || '-' }}</p>
          </div>
          <div v-if="complaint.rag_analysis.reason">
            <p class="text-sm text-slate-500">Alasan</p>
            <p class="text-slate-700">{{ complaint.rag_analysis.reason }}</p>
          </div>
          <div v-if="complaint.rag_analysis.confidence_score">
            <p class="text-sm text-slate-500 mb-2">Tingkat Kepercayaan AI</p>
            <div class="flex items-center gap-3">
              <div class="flex-1 bg-slate-200 rounded-full h-2">
                <div
                  class="bg-sky-600 h-2 rounded-full transition-all"
                  :style="{ width: `${Math.round(complaint.rag_analysis.confidence_score * 100)}%` }"
                ></div>
              </div>
              <span class="text-sm font-medium text-slate-700">
                {{ Math.round(complaint.rag_analysis.confidence_score * 100) }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Timeline -->
      <div class="bg-white rounded-xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">Status Pengaduan</h2>
        <div class="space-y-4">
          <div
            v-for="(item, index) in statusHistory"
            :key="index"
            class="flex items-center gap-4"
          >
            <div
              :class="item.active ? 'bg-sky-600' : 'bg-slate-200'"
              class="w-3 h-3 rounded-full flex-shrink-0"
            ></div>
            <div class="flex-1">
              <p :class="item.active ? 'font-medium text-slate-900' : 'text-slate-500'">
                {{ item.label }}
              </p>
              <p v-if="item.date" class="text-sm text-slate-400">{{ item.date }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'
import { complaintService } from '@/services/api'
import StatusBadge from '@/components/StatusBadge.vue'
import { ArrowLeft, AlertCircle } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const complaint = ref(null)
const loading = ref(true)
const error = ref('')

const formattedDate = computed(() => {
  if (!complaint.value) return ''
  return format(new Date(complaint.value.created_at), 'dd MMMM yyyy, HH:mm', { locale: id })
})

const statusHistory = computed(() => {
  if (!complaint.value) return []
  const status = complaint.value.status
  const statuses = ['pending', 'analyzing', 'reviewed', 'forwarded', 'resolved']
  const labels = ['Dikirim', 'Menganalisis', 'Ditinjau', 'Diteruskan', 'Selesai']
  const currentIndex = statuses.indexOf(status)

  return statuses.map((s, i) => ({
    label: labels[i],
    active: i <= currentIndex,
    date: i === currentIndex ? formattedDate.value : null
  }))
})

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