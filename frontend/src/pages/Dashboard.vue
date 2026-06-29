<template>
  <UserLayout>
    <div class="p-6">
      <!-- Quick Action -->
      <div class="mb-6">
        <router-link
          to="/complaints/new"
          class="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700">
          <PlusCircle class="w-5 h-5" />
          Buat Pengaduan Baru
        </router-link>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4 mb-8">
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
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-400">Diproses</p>
              <p class="text-3xl font-bold text-blue-400 mt-1">{{ stats.processing }}</p>
            </div>
            <div class="p-3 bg-blue-600/20 rounded-lg">
              <RefreshCw class="w-6 h-6 text-blue-400" />
            </div>
          </div>
        </div>
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

      <!-- Recent -->
      <div class="bg-slate-800 rounded-xl border border-slate-700">
        <div class="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-white">Pengaduan Saya</h2>
          <router-link to="/history" class="text-sm text-sky-400 hover:text-sky-300">Lihat Semua</router-link>
        </div>
        <div class="p-6">
          <div v-if="loading" class="text-center py-8 text-slate-400">Memuat...</div>
          <div v-else-if="recent.length === 0" class="text-center py-12">
            <Inbox class="w-16 h-16 text-slate-500 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-white mb-2">Belum Ada Pengaduan</h3>
            <p class="text-slate-400">Buat pengaduan pertama</p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="c in recent"
              :key="c.id"
              class="p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="font-medium text-white truncate">{{ c.title }}</h3>
                  <p class="text-sm text-slate-400 line-clamp-2 mt-1">{{ c.description }}</p>
                </div>
                <StatusBadge :status="c.status" type="status" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </UserLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { complaintService } from '@/services/api'
import UserLayout from '@/components/UserLayout.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { FileText, Clock, RefreshCw, CheckCircle, PlusCircle, Inbox } from 'lucide-vue-next'

const loading = ref(true)
const stats = ref({ total: 0, pending: 0, processing: 0, resolved: 0 })
const recent = ref([])

const loadDashboard = async () => {
  loading.value = true
  try {
    const res = await complaintService.getMyComplaints({ per_page: 50 })
    const data = res.data.complaints || []
    const total = res.data.total || data.length
    recent.value = data.slice(0, 5)
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

onMounted(loadDashboard)
</script>
