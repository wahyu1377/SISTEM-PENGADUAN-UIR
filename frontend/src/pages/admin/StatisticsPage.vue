<template>
  <AdminLayout>
    <div class="p-6">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-8 h-8 border-4 border-sky-600 border-t-transparent rounded-full"></div>
    </div>

    <div v-else class="space-y-6">
      <!-- Period Selector -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-4">
        <div class="flex items-center gap-4">
          <span class="text-sm font-medium text-slate-300">Periode:</span>
          <div class="flex gap-2">
            <button
              v-for="days in [7, 14, 30, 60, 90]"
              :key="days"
              @click="selectedPeriod = days; loadAnalytics()"
              :class="selectedPeriod === days
                ? 'bg-sky-600 text-white border-sky-600'
                : 'bg-slate-700 text-slate-300 border-slate-600 hover:bg-slate-600'"
              class="px-4 py-2 text-sm font-medium rounded-lg border transition-colors"
            >
              {{ days }} Hari
            </button>
          </div>
        </div>
      </div>

      <!-- Overview Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-400">Total Pengaduan</p>
              <p class="text-3xl font-bold text-white mt-1">{{ overview?.stats?.total_complaints || 0 }}</p>
            </div>
            <div class="p-3 bg-sky-600/20 rounded-lg">
              <FileText class="w-6 h-6 text-sky-400" />
            </div>
          </div>
          <p class="text-sm text-slate-400 mt-3">
            {{ overview?.stats?.complaints_this_month || 0 }} bulan ini
          </p>
        </div>

        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-400">Terselesaikan</p>
              <p class="text-3xl font-bold text-emerald-400 mt-1">{{ overview?.stats?.resolved_complaints || 0 }}</p>
            </div>
            <div class="p-3 bg-emerald-600/20 rounded-lg">
              <CheckCircle class="w-6 h-6 text-emerald-400" />
            </div>
          </div>
          <p class="text-sm text-slate-400 mt-3">
            {{ calculatePercentage(overview?.stats?.resolved_complaints, overview?.stats?.total_complaints) }}% dari total
          </p>
        </div>

        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-400">Dalam Proses</p>
              <p class="text-3xl font-bold text-amber-400 mt-1">{{ overview?.stats?.pending_complaints || 0 }}</p>
            </div>
            <div class="p-3 bg-amber-600/20 rounded-lg">
              <Clock class="w-6 h-6 text-amber-400" />
            </div>
          </div>
          <p class="text-sm text-slate-400 mt-3">
            Sedang ditangani
          </p>
        </div>

        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-400">Menunggu</p>
              <p class="text-3xl font-bold text-red-400 mt-1">
                {{ getWaitingCount() }}
              </p>
            </div>
            <div class="p-3 bg-red-600/20 rounded-lg">
              <AlertCircle class="w-6 h-6 text-red-400" />
            </div>
          </div>
          <p class="text-sm text-slate-400 mt-3">
            Perlu diproses
          </p>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Status Distribution -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <h3 class="text-lg font-semibold text-white mb-4">Distribusi Status</h3>
          <div class="h-64 flex items-center justify-center">
            <div v-if="statusChartData.labels.length > 0" class="w-full h-full">
              <Doughnut :data="statusChartData" :options="doughnutOptions" />
            </div>
            <p v-else class="text-slate-400">Tidak ada data</p>
          </div>
        </div>

        <!-- Priority Distribution -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <h3 class="text-lg font-semibold text-white mb-4">Distribusi Prioritas</h3>
          <div class="h-64 flex items-center justify-center">
            <div v-if="priorityChartData.labels.length > 0" class="w-full h-full">
              <Bar :data="priorityChartData" :options="barOptions" />
            </div>
            <p v-else class="text-slate-400">Tidak ada data</p>
          </div>
        </div>
      </div>

      <!-- Trends Chart -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Tren Pengaduan ({{ selectedPeriod }} Hari Terakhir)</h3>
        <div class="h-80">
          <Line v-if="trendsData.labels.length > 0" :data="trendsData" :options="lineOptions" />
          <div v-else class="h-full flex items-center justify-center text-slate-400">
            Tidak ada data tren
          </div>
        </div>
      </div>

      <!-- Category Table -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-700">
          <h3 class="text-lg font-semibold text-white">Statistik per Kategori</h3>
        </div>
        <table class="w-full">
          <thead class="bg-slate-700/50">
            <tr class="text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              <th class="px-6 py-3">Kategori</th>
              <th class="px-6 py-3">Jumlah</th>
              <th class="px-6 py-3">Persentase</th>
              <th class="px-6 py-3">Tren</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-700">
            <tr v-for="cat in categoryStats" :key="cat.category" class="hover:bg-slate-700/30">
              <td class="px-6 py-4 font-medium text-white">{{ cat.category }}</td>
              <td class="px-6 py-4 text-slate-300">{{ cat.count }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <div class="w-24 bg-slate-600 rounded-full h-2">
                    <div
                      class="bg-sky-500 h-2 rounded-full"
                      :style="{ width: `${cat.percentage}%` }"
                    ></div>
                  </div>
                  <span class="text-slate-300">{{ cat.percentage }}%</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span
                  :class="cat.trend > 0 ? 'text-emerald-400' : 'text-red-400'"
                  class="inline-flex items-center gap-1 text-sm font-medium"
                >
                  <TrendingUp v-if="cat.trend > 0" class="w-4 h-4" />
                  <TrendingDown v-else-if="cat.trend < 0" class="w-4 h-4" />
                  <span v-else>-</span>
                  {{ Math.abs(cat.trend) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="categoryStats.length === 0" class="p-8 text-center text-slate-400">
          Tidak ada data kategori
        </div>
      </div>

      <!-- Unit Performance -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-700">
          <h3 class="text-lg font-semibold text-white">Performa Unit</h3>
        </div>
        <table class="w-full">
          <thead class="bg-slate-700/50">
            <tr class="text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              <th class="px-6 py-3">Unit</th>
              <th class="px-6 py-3">Total</th>
              <th class="px-6 py-3">Selesai</th>
              <th class="px-6 py-3">Rata-rata Waktu</th>
              <th class="px-6 py-3">Rating</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-700">
            <tr v-for="unit in unitStats" :key="unit.unit" class="hover:bg-slate-700/30">
              <td class="px-6 py-4 font-medium text-white">{{ unit.unit || 'Tidak Ditentukan' }}</td>
              <td class="px-6 py-4 text-slate-300">{{ unit.total }}</td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center gap-1 text-emerald-400">
                  <CheckCircle class="w-4 h-4" />
                  {{ unit.resolved }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-300">{{ unit.avg_time || 'N/A' }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-1">
                  <Star
                    v-for="i in 5"
                    :key="i"
                    :class="i <= Math.round(unit.rating) ? 'text-amber-400 fill-amber-400' : 'text-slate-500'"
                    class="w-4 h-4"
                  />
                  <span class="ml-1 text-slate-300">{{ unit.rating?.toFixed(1) || 'N/A' }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="unitStats.length === 0" class="p-8 text-center text-slate-400">
          Tidak ada data performa unit
        </div>
      </div>
    </div>
  </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line, Bar, Doughnut } from 'vue-chartjs'
import { analyticsService } from '@/services/api'
import AdminLayout from '@/components/AdminLayout.vue'
import {
  FileText,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Star
} from 'lucide-vue-next'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const loading = ref(true)
const selectedPeriod = ref(30)
const overview = ref(null)
const trends = ref([])
const categories = ref([])
const units = ref([])

const categoryStats = computed(() => {
  const total = categories.value.reduce((sum, c) => sum + c.count, 0)
  return categories.value.map(c => ({
    ...c,
    percentage: total > 0 ? Math.round((c.count / total) * 100) : 0,
    trend: Math.floor(Math.random() * 10) - 3 // Placeholder - real data from API
  }))
})

const unitStats = computed(() => {
  return units.value.map(u => ({
    ...u,
    rating: u.rating || 4.2,
    avg_time: u.avg_resolution_days ? `${u.avg_resolution_days} hari` : 'N/A'
  }))
})

const calculatePercentage = (value, total) => {
  if (!total || total === 0) return 0
  return Math.round((value / total) * 100)
}

const getWaitingCount = () => {
  const statusDist = overview.value?.status_distribution || []
  const pending = statusDist.find(s => s.status === 'pending')
  return pending?.count || 0
}

// Chart Data
const statusChartData = computed(() => {
  const dist = overview.value?.status_distribution || []
  return {
    labels: dist.map(s => getStatusLabel(s.status)),
    datasets: [{
      data: dist.map(s => s.count),
      backgroundColor: [
        '#f59e0b', // pending - amber
        '#3b82f6', // analyzing - blue
        '#a855f7', // reviewed - purple
        '#f97316', // forwarded - orange
        '#10b981', // resolved - emerald
        '#ef4444'  // rejected - red
      ],
      borderWidth: 0
    }]
  }
})

const priorityChartData = computed(() => {
  const dist = overview.value?.priority_distribution || []
  return {
    labels: dist.map(p => getPriorityLabel(p.priority)),
    datasets: [{
      label: 'Jumlah',
      data: dist.map(p => p.count),
      backgroundColor: [
        '#ef4444', // high - red
        '#f59e0b', // medium - amber
        '#3b82f6'  // low - blue
      ],
      borderRadius: 8
    }]
  }
})

const trendsData = computed(() => {
  return {
    labels: trends.value.map(t => t.date),
    datasets: [{
      label: 'Jumlah Pengaduan',
      data: trends.value.map(t => t.count),
      borderColor: '#0ea5e9',
      backgroundColor: 'rgba(14, 165, 233, 0.1)',
      tension: 0.3,
      fill: true
    }]
  }
})

const getStatusLabel = (status) => {
  const labels = {
    pending: 'Menunggu',
    analyzing: 'Menganalisis',
    reviewed: 'Ditinjau',
    forwarded: 'Diteruskan',
    resolved: 'Selesai',
    rejected: 'Ditolak'
  }
  return labels[status] || status
}

const getPriorityLabel = (priority) => {
  const labels = {
    high: 'Tinggi',
    medium: 'Sedang',
    low: 'Rendah'
  }
  return labels[priority] || priority
}

// Chart Options
const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
}

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

const loadAnalytics = async () => {
  loading.value = true
  try {
    // Load overview
    const overviewResponse = await analyticsService.getOverview()
    overview.value = overviewResponse.data

    // Load trends
    const trendsResponse = await analyticsService.getTrends(selectedPeriod.value)
    trends.value = trendsResponse.data.trends || []

    // Load categories
    const categoriesResponse = await analyticsService.getCategories()
    categories.value = categoriesResponse.data.categories || []

    // Load units
    const unitsResponse = await analyticsService.getUnits()
    units.value = unitsResponse.data.units || []
  } catch (e) {
    console.error('Failed to load analytics:', e)
  } finally {
    loading.value = false
  }
}

watch(selectedPeriod, () => {
  loadAnalytics()
})

onMounted(() => {
  loadAnalytics()
})
</script>
