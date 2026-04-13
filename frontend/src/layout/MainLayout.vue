<template>
  <el-container class="main-shell h-screen min-h-screen w-full overflow-hidden bg-[#F5F7FB]">
    <el-aside
      width="248px"
      class="hidden h-screen min-h-screen flex-col overflow-hidden border-r border-slate-200/80 bg-white/95 shadow-[8px_0_32px_-24px_rgba(15,23,42,0.24)] md:flex"
    >
      <div class="flex h-16 shrink-0 items-center justify-center border-b border-slate-200/80 px-4">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center overflow-hidden rounded-xl bg-white p-1 shadow-lg shadow-indigo-600/15">
            <img :src="logo" alt="Logo" class="h-full w-full object-contain" />
          </div>
          <div>
            <div class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Club Suite</div>
            <div class="text-base font-bold tracking-tight text-slate-800">无线协 ALL IN ONE</div>
          </div>
        </div>
      </div>

      <el-scrollbar class="sidebar-scroll min-h-0 flex-1">
        <el-menu :default-active="activeMenu" class="border-none !bg-transparent px-3 py-4" router>
          <div class="menu-group-title">首页</div>
          <el-menu-item index="/home" class="menu-item">
            <el-icon><HomeFilled /></el-icon>
            <span>首页总览</span>
          </el-menu-item>

          <div class="menu-group-title">协会资源</div>
          <el-menu-item index="/rooms" class="menu-item">
            <el-icon><Monitor /></el-icon>
            <span>会议室预约</span>
          </el-menu-item>
          <el-menu-item index="/recruitment" class="menu-item">
            <el-icon><UserFilled /></el-icon>
            <span>招新面试</span>
          </el-menu-item>
          <el-menu-item index="/wireless-cup" class="menu-item">
            <el-icon><Trophy /></el-icon>
            <span>无线杯</span>
          </el-menu-item>
          <el-menu-item index="/telecom-cup" class="menu-item">
            <el-icon><Medal /></el-icon>
            <span>电信杯</span>
          </el-menu-item>
          <el-menu-item index="/teams-center" class="menu-item">
            <el-icon><Medal /></el-icon>
            <span>竞赛队伍管理</span>
          </el-menu-item>
          <el-menu-item index="/contacts" class="menu-item">
            <el-icon><Notebook /></el-icon>
            <span>通讯录</span>
          </el-menu-item>

          <template v-if="userStore.userRole === 'admin'">
            <div class="menu-group-title">管理工具</div>
            <el-menu-item index="/users" class="menu-item">
              <el-icon><User /></el-icon>
              <span>成员管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/schedule" class="menu-item">
              <el-icon><Calendar /></el-icon>
              <span>日程管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/rooms" class="menu-item">
              <el-icon><Setting /></el-icon>
              <span>会议室管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/management" class="menu-item">
              <el-icon><DataLine /></el-icon>
              <span>后台管理</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>

      <div class="mt-auto shrink-0 border-t border-slate-200/80 bg-gradient-to-b from-white to-slate-50 px-4 py-3 text-center text-xs font-medium text-slate-400">
        © 2026 All In One
      </div>
    </el-aside>

    <el-container class="min-w-0 flex-1 bg-[radial-gradient(circle_at_top,#ffffff_0%,#f7f9fc_55%,#f3f6fb_100%)]">
      <el-header
        class="sticky top-0 z-10 flex min-h-16 shrink-0 items-center justify-between gap-3 border-b border-slate-200/80 bg-white/88 px-3 py-3 backdrop-blur-md sm:px-4 md:px-6"
      >
        <div class="flex min-w-0 items-center gap-2 sm:gap-4">
          <el-button class="!h-9 !w-9 !p-1 md:hidden" text circle @click="isDrawerOpen = true">
            <el-icon :size="20"><Expand /></el-icon>
          </el-button>

          <div class="min-w-0">
            <div class="truncate text-base font-semibold text-slate-700 sm:hidden">{{ currentRouteName }}</div>
            <el-breadcrumb separator="/" class="hidden text-sm sm:flex">
              <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
        </div>

        <div class="flex items-center gap-1 sm:gap-3">
          <a
            href="https://github.com/Warm-CN/all-in-one"
            target="_blank"
            class="hidden h-9 w-9 items-center justify-center rounded-full text-gray-400 transition-all hover:bg-gray-50 hover:text-black sm:flex"
          >
            <svg
              height="20"
              width="20"
              viewBox="0 0 16 16"
              aria-hidden="true"
              version="1.1"
              class="fill-current"
            >
              <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z" />
            </svg>
          </a>

          <div class="relative hidden h-9 w-9 items-center justify-center rounded-full text-gray-400 transition-all hover:bg-gray-50 hover:text-indigo-600 sm:flex">
            <el-icon :size="20"><Bell /></el-icon>
            <span
              v-if="pendingCount > 0"
              class="absolute right-2 top-2 h-2 w-2 rounded-full border border-white bg-red-500"
            ></span>
          </div>

          <el-dropdown trigger="click" @command="handleCommand">
            <div
              class="flex items-center gap-2 rounded-full border border-transparent bg-white/70 px-1.5 py-1 transition-colors hover:border-gray-100 hover:bg-gray-50 sm:px-2"
            >
              <el-avatar
                :size="32"
                class="bg-indigo-100 text-sm font-bold text-indigo-600 ring-2 ring-indigo-50 transition-all"
              >
                {{ userStore.userName?.charAt(0) || 'U' }}
              </el-avatar>
              <div class="hidden min-w-0 flex-col items-start sm:flex">
                <span class="max-w-28 truncate text-sm font-semibold text-gray-700">
                  {{ userStore.userName || '用户' }}
                </span>
                <span
                  class="mt-0.5 rounded bg-gray-100 px-1.5 py-0.5 text-[10px] leading-none text-gray-400"
                  :class="{ '!bg-indigo-50 !text-indigo-500': userStore.isAdmin }"
                >
                  {{ userStore.userRole === 'admin' ? '系统管理员' : '普通成员' }}
                </span>
              </div>
              <el-icon class="hidden text-gray-400 transition-transform duration-300 sm:block">
                <CaretBottom />
              </el-icon>
            </div>

            <template #dropdown>
              <el-dropdown-menu class="!rounded-xl !border-gray-100 !p-2 !shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)]">
                <div class="mb-1 border-b border-gray-50 px-4 py-2">
                  <p class="text-xs text-gray-400">当前账号</p>
                  <p class="w-32 truncate font-medium text-gray-700">{{ userStore.studentId }}</p>
                </div>
                <el-dropdown-item command="settings" class="!my-0.5 !rounded-lg hover:!bg-indigo-50 hover:!text-indigo-600">
                  <el-icon><Setting /></el-icon>账号设置
                </el-dropdown-item>
                <el-divider class="!my-1 !border-gray-100" />
                <el-dropdown-item command="logout" class="!my-0.5 !rounded-lg !text-red-500 hover:!bg-red-50 hover:!text-red-600">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="flex min-h-0 flex-1 overflow-hidden !p-3 sm:!p-4 lg:!p-5">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <section
              class="mx-auto flex h-full w-full max-w-[1480px] min-w-0 flex-col overflow-hidden rounded-[24px] border border-slate-200/85 bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(248,250,252,0.94))] shadow-[0_18px_60px_-34px_rgba(15,23,42,0.28)]"
            >
              <div class="page-scroll-shell min-h-0 flex-1 overflow-y-auto overflow-x-hidden px-4 py-5 sm:px-5 sm:py-6 lg:px-6 lg:py-7">
                <component :is="Component" />
              </div>
            </section>
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>

  <el-drawer
    v-model="isDrawerOpen"
    direction="ltr"
    size="84vw"
    :with-header="false"
    class="mobile-nav-drawer !p-0"
  >
    <div class="flex h-full flex-col bg-white">
      <div class="flex h-16 items-center justify-center border-b border-gray-100 px-4">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center overflow-hidden rounded-xl bg-white p-1 shadow-lg shadow-indigo-600/15">
            <img :src="logo" alt="Logo" class="h-full w-full object-contain" />
          </div>
          <div>
            <div class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Club Suite</div>
            <div class="text-base font-bold tracking-tight text-slate-800">无线协 ALL IN ONE</div>
          </div>
        </div>
      </div>

      <el-scrollbar class="min-h-0 flex-1">
        <el-menu
          :default-active="activeMenu"
          class="border-none !bg-transparent px-3 py-4"
          router
          @select="isDrawerOpen = false"
        >
          <div class="menu-group-title">首页</div>
          <el-menu-item index="/home" class="menu-item">
            <el-icon><HomeFilled /></el-icon>
            <span>首页总览</span>
          </el-menu-item>

          <div class="menu-group-title">协会资源</div>
          <el-menu-item index="/rooms" class="menu-item">
            <el-icon><Monitor /></el-icon>
            <span>会议室预约</span>
          </el-menu-item>
          <el-menu-item index="/recruitment" class="menu-item">
            <el-icon><UserFilled /></el-icon>
            <span>招新面试</span>
          </el-menu-item>
          <el-menu-item index="/wireless-cup" class="menu-item">
            <el-icon><Trophy /></el-icon>
            <span>无线杯</span>
          </el-menu-item>
          <el-menu-item index="/telecom-cup" class="menu-item">
            <el-icon><Medal /></el-icon>
            <span>电信杯</span>
          </el-menu-item>
          <el-menu-item index="/teams-center" class="menu-item">
            <el-icon><Medal /></el-icon>
            <span>竞赛队伍管理</span>
          </el-menu-item>
          <el-menu-item index="/contacts" class="menu-item">
            <el-icon><Notebook /></el-icon>
            <span>通讯录</span>
          </el-menu-item>

          <template v-if="userStore.userRole === 'admin'">
            <div class="menu-group-title">管理工具</div>
            <el-menu-item index="/users" class="menu-item">
              <el-icon><User /></el-icon>
              <span>成员管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/schedule" class="menu-item">
              <el-icon><Calendar /></el-icon>
              <span>日程管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/rooms" class="menu-item">
              <el-icon><Setting /></el-icon>
              <span>会议室管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/management" class="menu-item">
              <el-icon><DataLine /></el-icon>
              <span>后台管理</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>
    </div>
  </el-drawer>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { getPendingUsers } from '@/api/user'
import logo from '@/assets/images/logo.png'
import {
  HomeFilled,
  Monitor,
  UserFilled,
  User,
  Bell,
  CaretBottom,
  Setting,
  Trophy,
  Medal,
  Notebook,
  DataLine,
  SwitchButton,
  Calendar,
  Expand
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const pendingCount = ref(0)
const isDrawerOpen = ref(false)

const activeMenu = computed(() => route.path)

const currentRouteName = computed(() => {
  return route.meta.title || '当前页面'
})

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

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const checkPendingUsers = async () => {
  if (userStore.userRole === 'admin') {
    try {
      const res = await getPendingUsers()
      if (res.code === 200 && Array.isArray(res.data)) {
        pendingCount.value = res.data.length
      }
    } catch (error) {
      console.error('Fetch pending users failed', error)
    }
  }
}

onMounted(() => {
  checkPendingUsers()
})
</script>

<style scoped>
.menu-group-title {
  margin: 14px 0 8px;
  padding: 0 16px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: #94a3b8;
}

.menu-item {
  margin-bottom: 6px;
  border-left: 4px solid transparent;
  border-radius: 14px;
  transition: all 0.2s ease;
}

.sidebar-scroll :deep(.el-scrollbar__wrap) {
  overflow-x: hidden;
}

:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
}

:deep(.el-menu-item.is-active) {
  border-left-color: #4f46e5 !important;
  background-color: #eef2ff !important;
  color: #4f46e5 !important;
  font-weight: 600;
}

:deep(.el-menu-item:hover) {
  background-color: #f8fafc !important;
}

:deep(.el-menu-item .el-icon) {
  color: inherit;
}

:deep(.mobile-nav-drawer .el-drawer__body) {
  padding: 0 !important;
}

:deep(.mobile-nav-drawer .el-drawer) {
  max-width: 320px;
}

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

@media (max-width: 640px) {
  :deep(.el-main) {
    min-height: calc(100vh - 73px);
  }

  .page-scroll-shell {
    padding-top: 18px;
    padding-bottom: 20px;
  }
}
</style>
