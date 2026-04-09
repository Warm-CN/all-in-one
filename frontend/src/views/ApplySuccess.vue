<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center animate__animated animate__zoomIn">
      <!-- Success Icon -->
      <div class="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-green-100 mb-6">
        <el-icon class="text-4xl text-green-500"><Select /></el-icon>
      </div>

      <h2 class="text-3xl font-extrabold text-gray-900 mb-2">报名成功！</h2>
      <p class="text-gray-500 mb-8 leading-relaxed">
        我们已收到你的报名信息。<br/>
        后续的审核与面试安排将通过短信通知，你也可以随时回到本页面通过学号和手机号查询进度。
      </p>

      <div class="space-y-4">
        <el-button 
          type="primary" 
          size="large" 
          class="w-full h-12 text-base font-medium rounded-xl shadow-md"
          @click="goBackToQuery"
        >
          查看我的进度
        </el-button>
        
        <el-button 
          size="large" 
          class="w-full h-12 text-base font-medium rounded-xl"
          @click="goHome"
        >
          返回系统首页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Select } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const goBackToQuery = () => {
  router.push({ path: '/apply', query: { tab: 'query' } })
}

const goHome = () => {
  router.push('/home')
}
</script>
