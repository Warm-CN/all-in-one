<template>
  <el-container class="h-screen w-full bg-[#F8FAFC]">
    <!-- 侧边栏 -->
    <el-aside
      width="260px"
      class="h-full bg-white border-r border-gray-100 transition-all duration-300 flex flex-col z-20 shadow-[2px_0_12px_rgba(0,0,0,0.01)]"
    >
      <!-- Logo 区域 -->
      <div class="h-16 flex items-center justify-center border-b border-gray-50/50">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-white shadow-lg shadow-indigo-600/20 overflow-hidden p-1">
            <img :src="logo" alt="Logo" class="w-full h-full object-contain" />
          </div>
          <span class="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600 tracking-tight">
            无协ALL IN ONE
          </span>
        </div>
      </div>

      <!-- 菜单区域 -->
      <el-scrollbar class="flex-1">
        <el-menu
          :default-active="activeMenu"
          class="border-none w-full !bg-transparent py-4 px-3"
          router
        >
          <!-- 首页概览 -->
          <div class="px-4 py-2 mb-2 text-xs font-semibold text-gray-400 opacity-60">首页</div>
          <el-menu-item index="/home" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
            <el-icon class="group-hover:text-indigo-600 transition-colors"><HomeFilled /></el-icon>
            <span class="group-hover:text-indigo-600 font-medium group-[.is-active]:text-indigo-600">首页概览</span>
          </el-menu-item>

          <!-- 协会资源 (所有人可见) -->
          <div class="px-4 py-2 mt-4 mb-2 text-xs font-semibold text-gray-400 opacity-60">协会资源</div>

          <el-menu-item index="/rooms" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
            <el-icon class="group-hover:text-indigo-600 transition-colors"><Monitor /></el-icon>
            <span class="group-hover:text-indigo-600 font-medium">会议室预约</span>
          </el-menu-item>

          <el-menu-item index="/recruitment" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
            <el-icon class="group-hover:text-indigo-600 transition-colors"><UserFilled /></el-icon>
            <span class="group-hover:text-indigo-600 font-medium">招新面试</span>
          </el-menu-item>
          
           <el-menu-item index="/wireless-cup" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
            <el-icon class="group-hover:text-indigo-600 transition-colors"><Trophy /></el-icon>
            <span class="group-hover:text-indigo-600 font-medium">无线杯</span>
          </el-menu-item>

           <el-menu-item index="/telecom-cup" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
            <el-icon class="group-hover:text-indigo-600 transition-colors"><Medal /></el-icon>
            <span class="group-hover:text-indigo-600 font-medium">电信杯</span>
          </el-menu-item>
          
           <el-menu-item index="/contacts" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
            <el-icon class="group-hover:text-indigo-600 transition-colors"><Notebook /></el-icon>
            <span class="group-hover:text-indigo-600 font-medium">通讯录</span>
          </el-menu-item>

          <!-- 管理工具 (仅 Admin 可见) -->
          <template v-if="userStore.userRole === 'admin'">
            <div class="px-4 py-2 mt-4 mb-2 text-xs font-semibold text-gray-400 opacity-60">管理工具</div>

            <el-menu-item index="/users" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
                <el-icon class="group-hover:text-indigo-600 transition-colors"><User /></el-icon>
                <span class="group-hover:text-indigo-600 font-medium">成员管理</span>
            </el-menu-item>

            <el-menu-item index="/admin/schedule" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
                <el-icon class="group-hover:text-indigo-600 transition-colors"><Calendar /></el-icon>
                <span class="group-hover:text-indigo-600 font-medium">日程管理</span>
            </el-menu-item>

            <el-menu-item index="/admin/rooms" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
                <el-icon class="group-hover:text-indigo-600 transition-colors"><Setting /></el-icon>
                <span class="group-hover:text-indigo-600 font-medium">会议室管理</span>
            </el-menu-item>

            <el-menu-item index="/admin/recruitment" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
                <el-icon class="group-hover:text-indigo-600 transition-colors"><DataLine /></el-icon>
                <span class="group-hover:text-indigo-600 font-medium">招新数据</span>
            </el-menu-item>
            
            <el-menu-item index="/admin/contest" class="group mb-1 rounded-xl hover:bg-indigo-50 !h-12 !leading-12 transition-all duration-200 border-l-4 border-transparent">
                <el-icon class="group-hover:text-indigo-600 transition-colors"><Platform /></el-icon>
                <span class="group-hover:text-indigo-600 font-medium">比赛后台</span>
            </el-menu-item>
          </template>

        </el-menu>
      </el-scrollbar>

      <!-- 底部版权 -->
      <div class="h-12 border-t border-gray-50 flex items-center justify-center text-xs text-gray-400 bg-white/50 backdrop-blur-sm">
        <span>© 2024 All In One</span>
      </div>
    </el-aside>

    <!-- 右侧主体 -->
    <el-container class="bg-[#F8FAFC]">
      <!-- 顶部导航栏 -->
      <el-header class="!h-16 bg-white/80 backdrop-blur-md border-b border-gray-100 flex items-center justify-between px-6 sticky top-0 z-10 transition-all duration-300">
        <!-- 左侧面包屑 -->
        <div class="flex items-center gap-4">
           <el-breadcrumb separator="/" class="text-sm">
            <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <!-- 右侧用户区 -->
        <div class="flex items-center gap-3">
           <!-- GitHub 图标 -->
           <a href="https://github.com/WUT-Wireless/All-In-One" target="_blank" class="w-9 h-9 rounded-full flex items-center justify-center text-gray-400 hover:text-black hover:bg-gray-50 transition-all">
              <svg height="20" aria-hidden="true" viewBox="0 0 16 16" version="1.1" width="20" data-view-component="true" class="fill-current">
                  <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
              </svg>
           </a>

           <!-- 通知图标 -->
           <div class="relative w-9 h-9 rounded-full flex items-center justify-center cursor-pointer text-gray-400 hover:text-indigo-600 hover:bg-gray-50 transition-all">
              <el-icon :size="20"><Bell /></el-icon>
              <span v-if="pendingCount > 0" class="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
           </div>

          <el-dropdown trigger="click" @command="handleCommand">
            <div class="flex items-center gap-3 cursor-pointer group py-1 px-2 rounded-full hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-100">
              <el-avatar :size="32" class="bg-indigo-100 text-indigo-600 text-sm font-bold ring-2 ring-indigo-50 group-hover:ring-indigo-100 transition-all">
                {{ userStore.userName?.charAt(0) || 'U' }}
              </el-avatar>
              <div class="flex flex-col items-start mr-1">
                <span class="text-sm font-semibold text-gray-700 group-hover:text-indigo-700 transition-colors">{{ userStore.userName || '用户' }}</span>
                <span class="text-[10px] text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded leading-none mt-0.5" :class="{'!text-indigo-500 !bg-indigo-50': userStore.isAdmin}">
                    {{ userStore.userRole === 'admin' ? '系统管理员' : '普通成员' }}
                </span>
              </div>
              <el-icon class="text-gray-400 group-hover:text-indigo-500 transition-transform duration-300 group-hover:rotate-180"><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="!p-2 !rounded-xl !border-gray-100 !shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)]">
                <div class="px-4 py-2 border-b border-gray-50 mb-1">
                    <p class="text-xs text-gray-400">当前账号</p>
                    <p class="font-medium text-gray-700 truncate w-32">{{ userStore.studentId }}</p>
                </div>
                <el-dropdown-item command="settings" class="!rounded-lg !my-0.5 hover:!bg-indigo-50 hover:!text-indigo-600">
                    <el-icon><Setting /></el-icon>账号设置
                </el-dropdown-item>
                <el-divider class="!my-1 !border-gray-100" />
                <el-dropdown-item command="logout" class="!rounded-lg !my-0.5 !text-red-500 hover:!bg-red-50 hover:!text-red-600">
                    <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主要内容区 -->
      <el-main class="!p-6 h-[calc(100vh-64px)] overflow-hidden">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
             <div class="h-full w-full bg-white rounded-2xl shadow-[0_2px_12px_-4px_rgba(0,0,0,0.02)] border border-gray-100/50 p-6 overflow-auto custom-scrollbar">
                <component :is="Component" />
             </div>
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { getPendingUsers } from '@/api/user'
import logo from '@/assets/images/logo.png'
import {
  ElementPlus,
  HomeFilled,
  Monitor,
  UserFilled,
  Box,
  User,
  Bell,
  CaretBottom,
  Setting,
  Trophy,
  Medal,
  Notebook,
  DataLine,
  Platform,
  SwitchButton,
  Calendar
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const pendingCount = ref(0)

// 当前激活菜单
const activeMenu = computed(() => route.path)

// 当前路由名称（用于面包屑）
const currentRouteName = computed(() => {
  return route.meta.title || '当前页面'
})

// 处理下拉菜单命令
const handleCommand = (command) => {
  switch (command) {
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 检查是否有待审核用户
const checkPendingUsers = async () => {
    if (userStore.userRole === 'admin') {
        try {
            const res = await getPendingUsers()
            if (res.code === 200) {
                 // 接口返回的是列表
                 if (Array.isArray(res.data)) {
                    pendingCount.value = res.data.length
                 }
            }
        } catch (e) {
            console.error('Fetch pending users failed', e)
        }
    }
}

onMounted(() => {
    checkPendingUsers()
})
</script>

<style scoped>
/* 侧边栏菜单样式覆盖 */
:deep(.el-menu-item) {
    margin-bottom: 4px;
}
:deep(.el-menu-item.is-active) {
    background-color: #EEF2FF !important; /* indigo-50 */
    color: #4F46E5 !important; /* indigo-600 */
    font-weight: 600;
    border-left-color: #4F46E5 !important;
}
:deep(.el-menu-item:hover) {
    background-color: #FAFAFA; /* gray-50 */
}

/* 简单的过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 自定义滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #E2E8F0;
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #CBD5E1;
}
</style>