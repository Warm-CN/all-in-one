<template>
  <div class="h-full flex flex-col bg-gray-50">
    <!-- 搜索栏 -->
    <div class="p-6 pb-0">
      <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-wrap gap-4 items-center">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索姓名或学号..."
          clearable
          @clear="fetchData"
          @keyup.enter="fetchData"
          class="!w-64"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchDepartment"
          placeholder="选择部门"
          clearable
          @change="fetchData"
          class="!w-48"
        >
          <el-option label="全部部门" value="" />
          <el-option label="科创部" value="科创部" />
          <el-option label="新媒体" value="新媒体" />
          <el-option label="宣传部" value="宣传部" />
          <el-option label="组织部" value="组织部" />
          <el-option label="外联部" value="外联部" />
          <el-option label="常委" value="常委" />
        </el-select>

        <el-button type="primary" @click="fetchData" class="!rounded-xl">
          <el-icon class="mr-1"><Search /></el-icon>
          查询
        </el-button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="flex-1 p-6 overflow-auto">
      <div v-loading="loading">
        <!-- Grid 布局展示卡片 -->
        <div v-if="contacts.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div 
            v-for="user in contacts" 
            :key="user.id" 
            class="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden flex flex-col"
          >
            <!-- 卡片头部装饰 -->
            <div class="h-1.5 bg-gradient-to-r from-blue-500 to-indigo-600"></div>

            <!-- 卡片内容 -->
            <div class="p-5 flex-1 flex flex-col">
              <div class="mb-4 flex items-start justify-between">
                <div>
                  <h3 class="text-lg font-bold text-gray-800">{{ user.real_name || user.full_name }}</h3>
                  <div class="text-sm text-gray-500 mt-1.5 flex items-center gap-2">
                    <span class="bg-gray-100 px-2 py-0.5 rounded text-xs">{{ user.department || '未分配' }}</span>
                    <span v-if="user.position" class="bg-blue-50 text-blue-600 px-2 py-0.5 rounded text-xs">{{ user.position }}</span>
                  </div>
                </div>
                <el-tag size="small" :type="user.role === 'admin' ? 'danger' : 'info'" effect="light" round>
                  {{ user.role === 'admin' ? 'Admin' : 'Member' }}
                </el-tag>
              </div>

              <div class="space-y-3 mt-auto">
                <div class="flex items-center gap-3 text-sm text-gray-600 group cursor-pointer" @click="copyText(user.phone)">
                  <div class="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center shrink-0 group-hover:bg-blue-50 transition-colors">
                    <el-icon class="group-hover:text-blue-600"><Iphone /></el-icon>
                  </div>
                  <span class="truncate active:text-blue-600 transition-colors select-all">{{ user.phone || '暂无手机号' }}</span>
                </div>
                
                <div class="flex items-center gap-3 text-sm text-gray-600 group cursor-pointer" @click="copyText(user.email)">
                  <div class="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center shrink-0 group-hover:bg-blue-50 transition-colors">
                    <el-icon class="group-hover:text-blue-600"><Message /></el-icon>
                  </div>
                  <span class="truncate active:text-blue-600 transition-colors select-all">{{ user.email || '暂无邮箱' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
          <el-icon :size="64" class="mb-4 text-gray-200"><UserFilled /></el-icon>
          <p class="text-lg">未找到匹配的通讯录成员</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Postcard, Iphone, Message, UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getContacts } from '@/api/contacts'

const searchKeyword = ref('')
const searchDepartment = ref('')
const contacts = ref([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getContacts({
      keyword: searchKeyword.value || undefined,
      department: searchDepartment.value || undefined
    })
    if (res.code === 200) {
      contacts.value = res.data
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取通讯录失败')
  } finally {
    loading.value = false
  }
}

const copyText = async (text) => {
  if (!text) return
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text)
      ElMessage.success('复制成功')
    } catch (e) {
      ElMessage.error('复制失败')
    }
  } else {
    // 降级处理
    ElMessage.warning('浏览器不支持自动复制，请手动复制')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* 可以在这里添加额外的样式 */
</style>
