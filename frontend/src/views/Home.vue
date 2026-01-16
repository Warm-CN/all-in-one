<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎回来</span>
        </div>
      </template>
      
      <div class="user-info">
        <h2>你好，{{ userStore.userName }}！</h2>
        <p>学号：{{ userStore.studentId }}</p>
        <p>角色：
          <el-tag v-if="userStore.isAdmin" type="danger">管理员</el-tag>
          <el-tag v-else-if="userStore.isMember" type="success">成员</el-tag>
          <el-tag v-else type="info">访客</el-tag>
        </p>
      </div>
      
      <el-divider />
      
      <div class="actions">
        <el-button type="primary" @click="refreshInfo">刷新用户信息</el-button>
        <el-button type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

onMounted(() => {
  // 页面加载时可以刷新用户信息
  console.log('用户信息:', userStore.userInfo)
})

/**
 * 刷新用户信息
 */
const refreshInfo = async () => {
  const success = await userStore.getUserInfo()
  if (success) {
    ElMessage.success('用户信息已更新')
  } else {
    ElMessage.error('获取用户信息失败')
  }
}

/**
 * 退出登录
 */
const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
}
</script>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.welcome-card {
  margin-top: 50px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  padding: 20px 0;
}

.user-info h2 {
  margin: 0 0 15px 0;
  color: #303133;
}

.user-info p {
  margin: 10px 0;
  color: #606266;
  font-size: 16px;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>
