<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Dashboard Admin</h1>
      <p class="text-slate-500">Kelola dan proses pengaduan mahasiswa</p>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard
        label="Total Pengaduan"
        :value="stats.total"
        :icon="FileText"
        variant="primary"
      />
      <StatCard
        label="Menunggu"
        :value="stats.pending"
        :icon="Clock"
        variant="warning"
      />
      <StatCard
        label="Diproses"
        :value="stats.processing"
        :icon="RefreshCw"
        variant="primary"
      />
      <StatCard
        label="Selesai"
        :value="stats.resolved"
        :icon="CheckCircle"
        variant="success"
      />
    </div>

    <!-- Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Recent Complaints -->
      <div class="lg:col-span-2 bg-white rounded-xl border border-slate-200">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
          <h2 class="text-lg font-semibold text-slate-900">Pengaduan Terbaru</h2>
          <router-link
            to="/admin/complaints"
            class="text-sm text-sky-600 hover:text-sky-700 font-medium"
          >
            Lihat Semua
          </router-link>
        </div>
        <div class="p-6">
          <div v-if="loading" class="text-center py-8 text-slate-500">
            Memuat...
          </div>
          <div v-else-if="recentComplaints.length === 0">
            <EmptyState
              icon-bg-color="bg-slate-100"
              icon-color="text-slate-400"
              title="Belum Ada Pengaduan"
              description="Pengaduan dari mahasiswa akan muncul di sini."
            />
          </div>
          <table v-else class="w-full">
            <thead>
              <tr class="text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                <th class="pb-3">Judul</th>
                <th class="pb-3">Mahasiswa</th>
                <th class="pb-3">Status</th>
                <th class="pb-3">Aksi</th>
              </tr>
            </thead>
            <tbody class="text-sm">
              <tr
                v-for="complaint in recentComplaints"
                :key="complaint.id"
                class="border-t border-slate-100"
              >
                <td class="py-3 pr-4">
                  <p class="font-medium text-slate-900 truncate max-w-xs">{{ complaint.title }}</p>
                  <p class="text-xs text-slate-500">{{ complaint.category || '-' }}</p>
                </td>
                <td class="py-3 pr-4">
                  <p class="text-slate-900">{{ complaint.user_name }}</p>
                  <p class="text-xs text-slate-500">{{ complaint.user_npm }}</p>
                </td>
                <td class="py-3">
                  <StatusBadge :status="complaint.status" type="status" />
                </td>
                <td class="py-3">
                  <router-link
                    :to="`/admin/complaints/${complaint.id}`"
                    class="text-sky-600 hover:text-sky-700 font-medium"
                  >
                    Proses
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="space-y-4">
        <div class="bg-white rounded-xl border border-slate-200 p-6">
          <h2 class="text-lg font-semibold text-slate-900 mb-4">Aksi Cepat</h2>
          <div class="space-y-3">
            <router-link
              to="/admin/complaints"
              class="flex items-center gap-3 p-4 rounded-lg bg-sky-50 hover:bg-sky-100 transition-colors"
            >
              <div class="p-2 bg-sky-100 rounded-lg">
                <FileText class="w-5 h-5 text-sky-600" />
              </div>
              <div>
                <p class="font-medium text-slate-900">Kelola Pengaduan</p>
                <p class="text-sm text-slate-500">Lihat semua pengaduan</p>
              </div>
            </router-link>
            <router-link
              to="/admin/complaints?status=pending"
              class="flex items-center gap-3 p-4 rounded-lg bg-amber-50 hover:bg-amber-100 transition-colors"
            >
              <div class="p-2 bg-amber-100 rounded-lg">
                <Clock class="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p class="font-medium text-slate-900">Menunggu</p>
                <p class="text-sm text-slate-500">{{ stats.pending }} pengaduan perlu diproses</p>
              </div>
            </router-link>
            <router-link
              to="/admin/complaints?status=resolved"
              class="flex items-center gap-3 p-4 rounded-lg bg-emerald-50 hover:bg-emerald-100 transition-colors"
            >
              <div class="p-2 bg-emerald-100 rounded-lg">
                <CheckCircle class="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <p class="font-medium text-slate-900">Selesai</p>
                <p class="text-sm text-slate-500">{{ stats.resolved }} pengaduan sudah selesai</p>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { complaintService } from '@/services/api'
import StatCard from '@/components/StatCard.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import EmptyState from '@/components/EmptyState.vue'
import {
  FileText,
  Clock,
  RefreshCw,
  CheckCircle
} from 'lucide-vue-next'

const loading = ref(true)
const stats = ref({
  total: 0,
  pending: 0,
  processing: 0,
  resolved: 0
})
const recentComplaints = ref([])

onMounted(async () => {
  try {
    const response = await complaintService.getAllComplaints({ per_page: 10 })
    const complaints = response.data.complaints

    stats.value.total = response.data.total
    stats.value.pending = complaints.filter(c => c.status === 'pending').length
    stats.value.processing = complaints.filter(c => ['analyzing', 'reviewed', 'forwarded'].includes(c.status)).length
    stats.value.resolved = complaints.filter(c => c.status === 'resolved').length

    recentComplaints.value = complaints.slice(0, 5)
  } catch (e) {
    console.error('Failed to load admin dashboard:', e)
  } finally {
    loading.value = false
  }
})
</script>
