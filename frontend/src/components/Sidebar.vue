<template>
  <aside class="w-64 bg-white border-r border-slate-200 min-h-screen">
    <div class="p-6 border-b border-slate-200">
      <h2 class="text-lg font-bold text-slate-900">{{ title }}</h2>
      <p class="text-sm text-slate-500">{{ subtitle }}</p>
    </div>
    <nav class="p-4">
      <ul class="space-y-1">
        <li v-for="item in items" :key="item.path">
          <router-link
            :to="item.path"
            class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors"
            :class="isActive(item.path)
              ? 'bg-sky-50 text-sky-700 border-l-4 border-sky-600 -ml-1 pl-5'
              : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'"
          >
            <component :is="item.icon" :size="18" />
            {{ item.label }}
          </router-link>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'

defineProps({
  title: { type: String, default: 'Navigation' },
  subtitle: { type: String, default: '' },
  items: { type: Array, default: () => [] }
})

const route = useRoute()

const isActive = (path) => {
  if (path === '/admin') return route.path === '/admin'
  return route.path.startsWith(path)
}
</script>
