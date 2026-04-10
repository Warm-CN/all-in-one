<template>
  <div class="flex h-full flex-col items-center justify-center p-6 text-center sm:p-12">
    <div class="w-24 h-24 bg-indigo-50 rounded-full flex items-center justify-center mb-6">
      <el-icon class="text-indigo-500 text-4xl"><Tools /></el-icon>
    </div>
    <h1 class="text-2xl font-bold text-gray-800 mb-2">{{ title }}</h1>
    <p class="text-gray-500 max-w-md">此功能模块正在紧锣密鼓地开发中，敬请期待！</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Tools } from '@element-plus/icons-vue'

const route = useRoute()
const title = computed(() => route.meta.title || 'Coming Soon')
</script>
