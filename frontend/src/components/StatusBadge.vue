<template>
  <span :class="[baseClass, colorClass]">
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
  type: { type: String, default: 'status' }
})

const labels = {
  status: {
    pending: 'Menunggu',
    analyzing: 'Menganalisis',
    reviewed: 'Ditinjau',
    forwarded: 'Diteruskan',
    resolved: 'Selesai',
    rejected: 'Ditolak'
  },
  priority: {
    high: 'Tinggi',
    medium: 'Sedang',
    low: 'Rendah'
  }
}

const label = computed(() => {
  return labels[props.type]?.[props.status] || props.status
})

// High contrast colors for dark theme
const baseClass = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'

const colorClass = computed(() => {
  if (props.type === 'priority') {
    const colors = {
      high: 'bg-red-600/80 text-white border border-red-500',
      medium: 'bg-amber-600/80 text-white border border-amber-500',
      low: 'bg-blue-600/80 text-white border border-blue-500'
    }
    return colors[props.status] || 'bg-slate-600/80 text-white border border-slate-500'
  }

  const colors = {
    pending: 'bg-amber-600/80 text-white border border-amber-500',
    analyzing: 'bg-blue-600/80 text-white border border-blue-500',
    reviewed: 'bg-purple-600/80 text-white border border-purple-500',
    forwarded: 'bg-orange-600/80 text-white border border-orange-500',
    resolved: 'bg-emerald-600/80 text-white border border-emerald-500',
    rejected: 'bg-red-600/80 text-white border border-red-500'
  }
  return colors[props.status] || 'bg-slate-600/80 text-white border border-slate-500'
})
</script>
