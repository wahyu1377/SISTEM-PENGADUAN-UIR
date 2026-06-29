<template>
  <div class="bg-white rounded-xl border border-slate-200 p-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-slate-500">{{ label }}</p>
        <p class="mt-2 text-3xl font-bold" :class="valueColor">{{ value }}</p>
      </div>
      <div :class="[iconBgColor, 'p-3 rounded-lg']">
        <component :is="icon" :size="24" :class="iconColor" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  icon: { type: Object, required: true },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'primary', 'warning', 'success', 'danger'].includes(v)
  }
})

const valueColor = {
  default: 'text-slate-900',
  primary: 'text-sky-600',
  warning: 'text-amber-600',
  success: 'text-emerald-600',
  danger: 'text-red-600'
}

const iconBgColor = {
  default: 'bg-slate-100',
  primary: 'bg-sky-100',
  warning: 'bg-amber-100',
  success: 'bg-emerald-100',
  danger: 'bg-red-100'
}

const iconColor = {
  default: 'text-slate-600',
  primary: 'text-sky-600',
  warning: 'text-amber-600',
  success: 'text-emerald-600',
  danger: 'text-red-600'
}
</script>
