<template>
  <div class="flex items-center justify-between bg-white rounded-lg shadow-sm border border-gray-100 p-4">
    <div class="flex items-center space-x-4">
      <div :class="statusClasses" class="w-2 h-2 rounded-full"></div>
      <div>
        <h3 class="text-sm font-medium text-gray-900">{{ title }}</h3>
        <p class="text-xs text-gray-500">{{ formattedDate }}</p>
      </div>
    </div>
    <div class="flex items-center space-x-3">
      <span :class="priorityClass" class="badge">
        {{ priority }}
      </span>
      <span :class="statusClass" class="badge">
        {{ statusLabel }}
      </span>
      <router-link :to="`/complaints/${id}`" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
        Detail
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'

const props = defineProps({
  id: { type: String, required: true },
  title: { type: String, required: true },
  status: { type: String, default: 'pending' },
  priority: { type: String, default: 'medium' },
  category: { type: String, default: '' },
  createdAt: { type: String, required: true }
})

const formattedDate = computed(() => {
  return format(new Date(props.createdAt), 'dd MMM yyyy, HH:mm', { locale: id })
})

const statusClasses = computed(() => {
  const classes = {
    pending: 'bg-yellow-400',
    analyzing: 'bg-blue-400',
    reviewed: 'bg-purple-400',
    forwarded: 'bg-orange-400',
    resolved: 'bg-green-400',
    rejected: 'bg-red-400'
  }
  return classes[props.status] || 'bg-gray-400'
})

const statusLabel = computed(() => {
  const labels = {
    pending: 'Menunggu',
    analyzing: 'Menganalisis',
    reviewed: 'Ditinjau',
    forwarded: 'Diteruskan',
    resolved: 'Selesai',
    rejected: 'Ditolak'
  }
  return labels[props.status] || props.status
})

const statusClass = computed(() => {
  const classes = {
    pending: 'badge-pending',
    analyzing: 'badge-analyzing',
    reviewed: 'badge-reviewed',
    forwarded: 'badge-forwarded',
    resolved: 'badge-resolved',
    rejected: 'badge-rejected'
  }
  return classes[props.status] || ''
})

const priorityClass = computed(() => {
  const classes = {
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low'
  }
  return classes[props.priority] || 'badge-medium'
})
</script>
