<template>
  <AdminLayout>
    <div class="p-6">
      <!-- Quick Actions -->
      <div class="mb-6 flex gap-4">
        <router-link to="/admin/complaints" class="inline-flex items-center gap-2 px-4 py-2.5 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 transition-colors">
          <FileText class="w-5 h-5" />
          Kelola Pengaduan
        </router-link>
        <router-link to="/admin/complaints?status=pending" class="inline-flex items-center gap-2 px-4 py-2.5 bg-amber-600 text-white font-medium rounded-lg hover:bg-amber-700 transition-colors">
          <Clock class="w-5 h-5" />
          Pengaduan Menunggu
        </router-link>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <!-- Total -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-400">Total</p>
              <p class="text-3xl font-bold text-white mt-1">{{ stats.total }}</p>
            </div>
            <div class="p-3 bg-sky-600/20 rounded-lg">
              <FileText class="w-6 h-6 text-sky-400" />
            </div>
          </div>
        </div>
        <!-- Pending -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-400">Menunggu</p>
              <p class="text-3xl font-bold text-amber-400 mt-1">{{ stats.pending }}</p>
            </div>
            <div class="p-3 bg-amber-600/20 rounded-lg">
              <Clock class="w-6 h-6 text-amber-400" />
            </div>
          </div>
        </div>
        <!-- Processing -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-400">Diproses</p>
              <p class="text-3xl font-bold text-sky-400 mt-1">{{ stats.processing }}</p>
            </div>
            <div class="p-3 bg-sky-600/20 rounded-lg">
              <RefreshCw class="w-6 h-6 text-sky-400" />
            </div>
          </div>
        </div>
        <!-- Resolved -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-400">Selesai</p>
              <p class="text-3xl font-bold text-emerald-400 mt-1">{{ stats.resolved }}</p>
            </div>
            <div class="p-3 bg-emerald-600/20 rounded-lg">
              <CheckCircle class="w-6 h-6 text-emerald-400" />
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-white">Pengaduan Terbaru</h2>
          <router-link to="/admin/complaints" class="text-sm text-sky-400 hover:text-sky-300">Lihat Semua</router-link>
        </div>
        <div v-if="recentComplaints.length === 0" class="text-center py-8 text-slate-400">
          Belum ada pengaduan
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="complaint in recentComplaints"
            :key="complaint.id"
            class="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
            <div class="flex-1 min-w-0">
              <p class="text-white font-medium truncate">{{ complaint.title }}</p>
              <p class="text-sm text-slate-400">{{ formatDate(complaint.created_at) }}</p>
            </div>
            <StatusBadge :status="complaint.status" type="status" />
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { complaintService } from '@/services/api'
import AdminLayout from '@/components/AdminLayout.vue'
import { FileText, Clock, RefreshCw, CheckCircle } from 'lucide-vue-next'
import StatusBadge from '@/components/StatusBadge.vue'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'

const route = useRoute()
const loading = ref(true)
const stats = ref({ total: 0, pending: 0, processing: 0, resolved: 0 })
const recentComplaints = ref([])

const formatDate = (date) => format(new Date(date), 'dd MMM yyyy', { locale: id })

const loadData = async () => {
  loading.value = true
  try {
    const res = await complaintService.getAllComplaints({ per_page: 50 })
    const data = res.data.complaints || []
    const total = res.data.total || data.length
    recentComplaints.value = data.slice(0, 5)
    stats.value = {
      total,
      pending: data.filter(c => c.status === 'pending').length,
      processing: data.filter(c => ['analyzing', 'reviewed', 'forwarded'].includes(c.status)).length,
      resolved: data.filter(c => c.status === 'resolved').length
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
watch(() => route.path, loadData)
</script>
