<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
    <div class="animate__animated animate__zoomIn w-full max-w-md rounded-2xl bg-white p-6 text-center shadow-xl sm:p-8">
      <!-- Success Icon -->
      <div class="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-green-100 mb-6">
        <el-icon class="text-4xl text-green-500"><Select /></el-icon>
      </div>

      <h2 class="text-3xl font-extrabold text-gray-900 mb-2">报名成功！</h2>
      <p class="text-gray-500 mb-8 leading-relaxed">
        我们已收到你的报名信息。<br/>
        后续的审核与面试安排将通过短信通知，你也可以随时回到本页面通过学号和手机号查询进度。
      </p>

      <div class="flex flex-col gap-4">
        <el-button 
          type="primary" 
          size="large" 
          class="!ml-0 !h-12 !w-full !rounded-xl text-base font-medium shadow-md"
          @click="goBackToQuery"
        >
          查看我的进度
        </el-button>
        
        <el-button 
          size="large" 
          class="!ml-0 !h-12 !w-full !rounded-xl !border-slate-200 !bg-slate-100 !text-slate-700 text-base font-medium hover:!border-slate-300 hover:!bg-slate-200 hover:!text-slate-800"
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
