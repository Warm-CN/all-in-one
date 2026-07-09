<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
    <div class="mb-3 flex items-center justify-between">
      <span class="rounded-full px-2 py-1 text-xs font-semibold" :class="categoryClass">{{ categoryLabel }}</span>
      <span class="rounded-full px-2 py-1 text-xs" :class="statusClass">{{ statusLabel }}</span>
    </div>
    <h3 class="mb-1 text-lg font-bold text-slate-800">{{ suggestion.title }}</h3>
    <p class="mb-2 text-xs text-slate-400">
      <span v-if="suggestion.is_anonymous" class="text-slate-400">匿名用户</span>
      <span v-else class="font-medium text-slate-600">{{ suggestion.author_name || '未知用户' }}</span>
    </p>
    <p class="mb-3 line-clamp-2 text-sm text-slate-500">{{ suggestion.description }}</p>
    <div class="flex items-center justify-between text-xs text-slate-400">
      <span>{{ suggestion.created_at }}</span>
      <el-button link type="primary" @click="$emit('view', suggestion.id)">查看详情</el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ suggestion: Object })
defineEmits(['view'])

const categoryLabel = computed(() => ({ layout: '布局美化', feature: '功能优化', bug: 'Bug反馈', other: '其他' }[props.suggestion.category] || '其他'))
const categoryClass = computed(() => ({
  layout: 'bg-blue-50 text-blue-600', feature: 'bg-green-50 text-green-600',
  bug: 'bg-red-50 text-red-600', other: 'bg-gray-100 text-gray-600'
}[props.suggestion.category] || 'bg-gray-100 text-gray-600'))

const statusLabel = computed(() => ({
  received: '已收到', pending_fix: '等待修改', fixing: '修改中',
  wont_fix: '不予修改', done: '修改成功'
}[props.suggestion.status] || '已收到'))
const statusClass = computed(() => ({
  received: 'bg-gray-100 text-gray-600', pending_fix: 'bg-amber-50 text-amber-600',
  fixing: 'bg-blue-50 text-blue-600', wont_fix: 'bg-red-50 text-red-600',
  done: 'bg-green-50 text-green-600'
}[props.suggestion.status] || 'bg-gray-100 text-gray-600'))
</script>
