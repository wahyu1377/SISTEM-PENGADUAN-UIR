<template>
  <div class="flex flex-col items-center justify-center py-12 text-center">
    <div :class="[iconBgColor, 'p-4 rounded-full mb-4']">
      <component :is="icon" :size="32" :class="iconColor" />
    </div>
    <h3 class="text-lg font-medium text-slate-900">{{ title }}</h3>
    <p class="mt-1 text-sm text-slate-500 max-w-sm">{{ description }}</p>
    <div v-if="$slots.action" class="mt-6">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
import { FileText } from 'lucide-vue-next'

defineProps({
  icon: { type: Object, default: () => FileText },
  iconBgColor: { type: String, default: 'bg-slate-100' },
  iconColor: { type: String, default: 'text-slate-400' },
  title: { type: String, default: 'Tidak ada data' },
  description: { type: String, default: 'Belum ada item untuk ditampilkan.' }
})
</script>
