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
          <div class="min-w-0">
            <div class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Club Suite</div>
            <div class="max-w-[162px] truncate text-base font-bold tracking-tight text-slate-800">无线协 ALL IN ONE</div>
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
          <el-menu-item index="/teams-center" class="menu-item">
            <el-icon><Trophy /></el-icon>
            <span>竞赛队伍</span>
          </el-menu-item>
          <el-menu-item index="/contacts" class="menu-item">
            <el-icon><Notebook /></el-icon>
            <span>通讯录</span>
          </el-menu-item>
          <el-menu-item index="/co-build" class="menu-item">
            <el-icon><EditPen /></el-icon>
            <span>共建</span>
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
            <el-menu-item index="/admin/recruitment" class="menu-item">
              <el-icon><UserFilled /></el-icon>
              <span>招新管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/events" class="menu-item">
              <el-icon><DataLine /></el-icon>
              <span>赛事管理</span>
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
          <div class="min-w-0">
            <div class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Club Suite</div>
            <div class="max-w-[190px] truncate text-base font-bold tracking-tight text-slate-800">无线协 ALL IN ONE</div>
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
          <el-menu-item index="/teams-center" class="menu-item">
            <el-icon><Trophy /></el-icon>
            <span>竞赛队伍</span>
          </el-menu-item>
          <el-menu-item index="/contacts" class="menu-item">
            <el-icon><Notebook /></el-icon>
            <span>通讯录</span>
          </el-menu-item>
          <el-menu-item index="/co-build" class="menu-item">
            <el-icon><EditPen /></el-icon>
            <span>共建</span>
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
            <el-menu-item index="/admin/recruitment" class="menu-item">
              <el-icon><UserFilled /></el-icon>
              <span>招新管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/events" class="menu-item">
              <el-icon><DataLine /></el-icon>
              <span>赛事管理</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>
    </div>
  </el-drawer>

  <!-- 元素选择模式 -->
  <template v-if="cobuildMode">
    <!-- 浮动工具栏 -->
    <transition name="slide-down">
      <div
        class="fixed left-2 right-2 top-20 z-[3000] flex flex-col items-center gap-2 rounded-2xl bg-white/95 px-3 py-2.5 shadow-lg ring-1 ring-slate-200 backdrop-blur-md sm:left-1/2 sm:right-auto sm:w-auto sm:max-w-[90vw] sm:-translate-x-1/2 sm:flex-row sm:items-center sm:gap-4 sm:px-5 sm:py-3"
      >
        <div class="flex items-center gap-2">
          <el-icon :size="18" class="text-indigo-500"><EditPen /></el-icon>
          <span class="text-sm font-semibold text-slate-700">元素选择模式</span>
        </div>
        <span class="hidden text-xs text-slate-400 sm:inline">点击页面元素添加问题描述</span>
        <div class="flex items-center gap-2">
          <span class="rounded-full bg-indigo-500 px-2.5 py-0.5 text-xs font-bold text-white">{{ selections.length }}</span>
          <el-button type="primary" size="small" :loading="capturing" @click="finishSelection">
            完成
          </el-button>
          <el-button size="small" plain @click="cancelSelection">取消</el-button>
        </div>
      </div>
    </transition>

    <!-- 视觉覆盖层(pointer-events: none, 不拦截事件) -->
    <div class="pointer-events-none fixed inset-0 z-[2900]">
      <!-- 悬停高亮框 -->
      <div
        v-if="hoverRect.visible"
        class="absolute rounded border-2 border-blue-500 bg-blue-500/10 transition-all duration-75"
        :style="{ left: hoverRect.x + 'px', top: hoverRect.y + 'px', width: hoverRect.w + 'px', height: hoverRect.h + 'px' }"
      ></div>

      <!-- 已选元素方框 -->
      <div
        v-for="(sel, idx) in selections"
        :key="sel.id"
        class="absolute rounded border-2 border-blue-500/80 bg-blue-500/5"
        :style="{ left: sel.rect.x + 'px', top: sel.rect.y + 'px', width: sel.rect.w + 'px', height: sel.rect.h + 'px' }"
      ></div>

      <!-- 编号徽章(pointer-events: auto, 可点击编辑) -->
      <div
        v-for="(sel, idx) in selections"
        :key="'badge-' + sel.id"
        class="pointer-events-auto absolute flex h-6 w-6 cursor-pointer items-center justify-center rounded-full bg-blue-500 text-xs font-bold text-white shadow-lg ring-2 ring-white transition-transform hover:scale-110"
        :style="{ left: (sel.rect.x + sel.rect.w - 12) + 'px', top: (sel.rect.y - 12) + 'px' }"
        @click.stop="editSelection(sel.id)"
      >{{ idx + 1 }}</div>

      <!-- 输入气泡 -->
      <div
        v-if="editingId !== null"
        class="pointer-events-auto fixed inset-0 z-[3100] flex items-center justify-center bg-black/20 sm:absolute sm:inset-auto sm:bg-transparent"
        :style="bubbleStyle"
        @click.self="cancelEdit"
      >
        <div class="w-[min(20rem,calc(100vw-2rem))] rounded-xl bg-white p-3 shadow-2xl ring-2 ring-indigo-500">
          <div class="mb-2 flex items-center gap-2 border-b border-slate-100 pb-2">
            <span class="rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">{{ editingElement?.tag }}</span>
            <span v-if="editingElement?.component" class="text-xs text-indigo-500">{{ editingElement.component }}</span>
          </div>
          <textarea
            ref="bubbleInput"
            v-model="inputText"
            placeholder="描述这个问题..."
            rows="3"
            class="w-full resize-none rounded-lg border border-slate-200 p-2 text-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
            @keydown.enter.prevent="confirmEdit"
            @keydown.escape="cancelEdit"
          ></textarea>
          <div class="mt-2 flex justify-end gap-2">
            <button
              v-if="editingIndex >= 0"
              @click.stop="deleteSelection"
              class="rounded-lg px-2.5 py-1 text-xs text-red-500 hover:bg-red-50"
            >删除</button>
            <button @click.stop="cancelEdit" class="rounded-lg px-2.5 py-1 text-xs text-slate-500 hover:bg-slate-50">取消</button>
            <button @click.stop="confirmEdit" class="rounded-lg bg-indigo-500 px-3 py-1 text-xs font-medium text-white hover:bg-indigo-600">确认</button>
          </div>
        </div>
      </div>
    </div>
  </template>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { getPendingUsers } from '@/api/user'
import { cobuildState, getPageLabel } from '@/composables/cobuildData'
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
  Notebook,
  DataLine,
  SwitchButton,
  Calendar,
  Expand,
  EditPen,
  Camera
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
  initCobuildMode()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})

function onResize() {
  isMobile.value = window.innerWidth < 640
}

// ==================== 元素选择模式 ====================
const cobuildMode = ref(false)
const capturing = ref(false)
const selections = ref([])
const hoverRect = ref({ x: 0, y: 0, w: 0, h: 0, visible: false })
const editingId = ref(null)
const inputText = ref('')
const bubbleInput = ref(null)
const isMobile = ref(window.innerWidth < 640)
let selIdCounter = 0
let pendingElement = null
let touchEndTime = 0 // 记录 touchend 时间，用于过滤合成 click

const editingElement = computed(() => {
  if (editingId.value === null) return null
  if (editingId.value === 'new') return pendingElement
  return selections.value.find(s => s.id === editingId.value) || null
})

const editingIndex = computed(() => {
  if (typeof editingId.value === 'number') {
    return selections.value.findIndex(s => s.id === editingId.value)
  }
  return -1
})

const bubbleStyle = computed(() => {
  const el = editingElement.value
  if (!el) return {}

  // 手机端：居中但偏离所选元素（元素在上半 → 气泡靠下，元素在下半 → 气泡靠上）
  if (isMobile.value) {
    const elementCenterY = el.rect.y + el.rect.h / 2
    const screenCenterY = window.innerHeight / 2
    const dialogH = 200
    let marginTop = 0
    if (elementCenterY < screenCenterY) {
      // 元素在上半，气泡往下偏
      marginTop = Math.min(80, (screenCenterY - elementCenterY) / 2)
    } else {
      // 元素在下半，气泡往上偏
      marginTop = -Math.min(80, (elementCenterY - screenCenterY) / 2)
    }
    return {
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      marginTop: marginTop + 'px',
    }
  }

  // 桌面端：气泡出现在元素右侧，空间不够则在左侧
  const bubbleW = 280
  const bubbleH = 180
  let left = el.rect.x + el.rect.w + 8
  if (left + bubbleW > window.innerWidth) {
    left = el.rect.x - bubbleW - 8
  }
  let top = el.rect.y
  if (top + bubbleH > window.innerHeight) {
    top = window.innerHeight - bubbleH - 10
  }
  if (top < 10) top = 10
  return { left: left + 'px', top: top + 'px' }
})

function initCobuildMode() {
  const params = new URLSearchParams(window.location.search)
  if (params.get('cobuild') === '1') {
    enterCobuildMode()
  }
}

watch(() => route.fullPath, (fullPath) => {
  const params = new URLSearchParams(fullPath.split('?')[1] || '')
  if (params.get('cobuild') === '1') {
    enterCobuildMode()
  } else {
    exitCobuildMode()
  }
})

function enterCobuildMode() {
  if (cobuildMode.value) return
  cobuildMode.value = true
  selections.value = []
  editingId.value = null

  // 如果有进行中的数据,恢复已有选择
  if (cobuildState.inProgress && cobuildState.inProgress.elements) {
    selections.value = cobuildState.inProgress.elements.map(e => ({ ...e, id: ++selIdCounter }))
  }

  document.addEventListener('mouseover', onMouseOver, true)
  document.addEventListener('mouseout', onMouseOut, true)
  document.addEventListener('click', onDocumentClick, true)
  document.addEventListener('scroll', onScroll, true)
  document.addEventListener('touchend', onTouchEnd, { capture: true, passive: false })
  document.addEventListener('touchstart', onTouchStart, { capture: true, passive: true })
  document.addEventListener('touchmove', onTouchMove, { capture: true, passive: true })
}

function exitCobuildMode() {
  if (!cobuildMode.value) return
  cobuildMode.value = false
  selections.value = []
  editingId.value = null
  hoverRect.value.visible = false

  document.removeEventListener('mouseover', onMouseOver, true)
  document.removeEventListener('mouseout', onMouseOut, true)
  document.removeEventListener('click', onDocumentClick, true)
  document.removeEventListener('scroll', onScroll, true)
  document.removeEventListener('touchend', onTouchEnd, { capture: true })
  document.removeEventListener('touchstart', onTouchStart, { capture: true })
  document.removeEventListener('touchmove', onTouchMove, { capture: true })
}

function onMouseOver(e) {
  if (!cobuildMode.value || editingId.value !== null) return
  const el = e.target
  // 忽略覆盖层元素
  if (el.closest('.pointer-events-none') || el.closest('[class*="z-[29"]') || el.closest('[class*="z-[30"]') || el.closest('[class*="z-[31"]')) return
  // 忽略太小的元素
  const rect = el.getBoundingClientRect()
  if (rect.width < 20 || rect.height < 10) return

  hoverRect.value = {
    x: rect.left,
    y: rect.top,
    w: rect.width,
    h: rect.height,
    visible: true
  }
}

function onMouseOut(e) {
  if (!cobuildMode.value) return
  // 仅在鼠标离开主内容区域时才隐藏高亮框,避免子元素间移动时闪烁
  const main = document.querySelector('.el-main')
  if (main && e.relatedTarget && !main.contains(e.relatedTarget)) {
    hoverRect.value.visible = false
  }
}

function onScroll() {
  // 滚动时更新已选元素的位置
  selections.value.forEach(sel => {
    const el = findElementBySelector(sel.selector, sel.tag, sel.text)
    if (el) {
      const rect = el.getBoundingClientRect()
      sel.rect = { x: rect.left, y: rect.top, w: rect.width, h: rect.height }
    }
  })
}

function onDocumentClick(e) {
  if (!cobuildMode.value) return
  if (editingId.value !== null) return
  // 过滤触摸产生的合成 click（touchend 已处理过）
  if (touchEndTime && Date.now() - touchEndTime < 500) return
  if (e.target.closest('[class*="z-[29"]') || e.target.closest('[class*="z-[30"]') || e.target.closest('[class*="z-[31"]')) return

  e.preventDefault()
  e.stopPropagation()

  const el = e.target
  const rect = el.getBoundingClientRect()

  const existing = selections.value.find(s => {
    return Math.abs(s.rect.x - rect.left) < 5 && Math.abs(s.rect.y - rect.top) < 5
  })
  if (existing) {
    editSelection(existing.id)
    return
  }

  pendingElement = {
    tag: el.tagName.toLowerCase(),
    class: Array.from(el.classList || []).filter(c => !c.startsWith('el-') && !c.startsWith('is-') && !c.startsWith('fade-')).join(' ').slice(0, 200),
    text: (el.textContent || '').trim().slice(0, 200),
    selector: getSelector(el),
    component: getComponentName(el),
    rect: { x: rect.left, y: rect.top, w: rect.width, h: rect.height }
  }

  editingId.value = 'new'
  inputText.value = ''
  hoverRect.value.visible = false

  nextTick(() => {
    bubbleInput.value?.focus()
  })
}

let touchStartX = 0
let touchStartY = 0
let touchMoved = false

function onTouchStart(e) {
  if (!cobuildMode.value || editingId.value !== null) return
  const touch = e.touches[0]
  if (!touch) return
  touchStartX = touch.clientX
  touchStartY = touch.clientY
  touchMoved = false
}

function onTouchMove(e) {
  if (!cobuildMode.value) return
  const touch = e.touches[0]
  if (!touch) return
  const dx = Math.abs(touch.clientX - touchStartX)
  const dy = Math.abs(touch.clientY - touchStartY)
  if (dx > 10 || dy > 10) touchMoved = true
}

function onTouchEnd(e) {
  if (!cobuildMode.value) return
  if (editingId.value !== null) return

  // 记录 touchend 时间，让后续合成 click 被过滤
  touchEndTime = Date.now()

  // 滑动操作不拦截，允许页面滚动
  if (touchMoved) {
    hoverRect.value.visible = false
    return
  }

  const touch = e.changedTouches[0]
  if (!touch) return

  // 用 touch 坐标找到实际元素
  const el = document.elementFromPoint(touch.clientX, touch.clientY) || e.target
  if (!el || el === document || el === document.body) return

  // 忽略覆盖层和工具栏
  if (el.closest('[class*="z-[29"]') || el.closest('[class*="z-[30"]') || el.closest('[class*="z-[31"]')) return

  // 拦截触摸事件，阻止后续合成 click 和默认行为
  e.preventDefault()
  e.stopImmediatePropagation()

  const rect = el.getBoundingClientRect()

  // 检查是否已选中
  const existing = selections.value.find(s => {
    return Math.abs(s.rect.x - rect.left) < 5 && Math.abs(s.rect.y - rect.top) < 5
  })
  if (existing) {
    editSelection(existing.id)
    return
  }

  // 收集元素信息
  pendingElement = {
    tag: el.tagName.toLowerCase(),
    class: Array.from(el.classList || []).filter(c => !c.startsWith('el-') && !c.startsWith('is-') && !c.startsWith('fade-')).join(' ').slice(0, 200),
    text: (el.textContent || '').trim().slice(0, 200),
    selector: getSelector(el),
    component: getComponentName(el),
    rect: { x: rect.left, y: rect.top, w: rect.width, h: rect.height }
  }

  editingId.value = 'new'
  inputText.value = ''
  hoverRect.value.visible = false

  nextTick(() => {
    bubbleInput.value?.focus()
  })
}

function getSelector(el) {
  const parts = []
  let node = el
  let depth = 0
  while (node && node !== document.body && depth < 5) {
    let selector = node.tagName.toLowerCase()
    if (node.id) {
      selector += '#' + node.id
      parts.unshift(selector)
      break
    }
    const classes = Array.from(node.classList || [])
      .filter(c => !c.startsWith('el-') && !c.startsWith('is-') && !c.startsWith('fade-') && !c.startsWith('page-') && !c.startsWith('transition'))
      .slice(0, 2)
    if (classes.length) {
      selector += '.' + classes.join('.')
    }
    parts.unshift(selector)
    node = node.parentElement
    depth++
  }
  return parts.join(' > ')
}

function getComponentName(el) {
  let node = el
  while (node && node !== document.body) {
    if (node.__vueParentComponent) {
      const comp = node.__vueParentComponent
      const type = comp.type || {}
      const name = type.__name || type.name
      if (name) return name
      if (type.__file) {
        return type.__file.split('/').pop().replace(/\.\w+$/, '')
      }
    }
    node = node.parentElement
  }
  return ''
}

function findElementBySelector(selector, tag, text) {
  // 简单的查找:通过 selector 找到元素,验证 tag 和 text
  try {
    const el = document.querySelector(selector)
    if (el && el.tagName.toLowerCase() === tag) return el
  } catch (e) {}
  // Fallback: 搜索相同 tag+text 的元素
  const candidates = document.getElementsByTagName(tag.charAt(0).toUpperCase() + tag.slice(1))
  for (const el of candidates) {
    if ((el.textContent || '').trim().startsWith(text.slice(0, 20))) return el
  }
  return null
}

function editSelection(id) {
  const sel = selections.value.find(s => s.id === id)
  if (!sel) return
  editingId.value = id
  inputText.value = sel.description
  nextTick(() => {
    bubbleInput.value?.focus()
  })
}

function confirmEdit() {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入问题描述')
    return
  }
  if (editingId.value === 'new') {
    // 新增
    selections.value.push({
      id: ++selIdCounter,
      ...pendingElement,
      description: inputText.value.trim()
    })
  } else {
    // 编辑
    const sel = selections.value.find(s => s.id === editingId.value)
    if (sel) sel.description = inputText.value.trim()
  }
  editingId.value = null
  inputText.value = ''
  pendingElement = null
}

function cancelEdit() {
  editingId.value = null
  inputText.value = ''
  pendingElement = null
}

function deleteSelection() {
  if (typeof editingId.value === 'number') {
    const idx = selections.value.findIndex(s => s.id === editingId.value)
    if (idx >= 0) selections.value.splice(idx, 1)
  }
  editingId.value = null
  inputText.value = ''
}

async function finishSelection() {
  if (selections.value.length === 0) {
    ElMessage.warning('请至少选择一个元素')
    return
  }
  if (capturing.value) return
  capturing.value = true

  // 立即移除事件监听，防止 touchend/click 干扰后续操作
  document.removeEventListener('mouseover', onMouseOver, true)
  document.removeEventListener('mouseout', onMouseOut, true)
  document.removeEventListener('click', onDocumentClick, true)
  document.removeEventListener('scroll', onScroll, true)
  document.removeEventListener('touchend', onTouchEnd, { capture: true })
  document.removeEventListener('touchstart', onTouchStart, { capture: true })
  document.removeEventListener('touchmove', onTouchMove, { capture: true })

  // 临时退出模式,隐藏所有覆盖层
  cobuildMode.value = false
  editingId.value = null
  hoverRect.value.visible = false
  await new Promise(r => setTimeout(r, 300))

  try {
    // 截取主内容区域
    const target = document.querySelector('.el-main') || document.body
    const targetRect = target.getBoundingClientRect()

    let screenshotData = { imageSrc: '', width: 0, height: 0 }

    // 截图超时保护（5秒）
    const screenshotPromise = (async () => {
      try {
        const { toJpeg } = await import('html-to-image')
        const dataUrl = await toJpeg(target, {
          quality: 0.7,
          backgroundColor: '#ffffff',
          pixelRatio: isMobile.value ? 2 : 1,
          skipFonts: true,
          cacheBust: true,
        })
        if (dataUrl && dataUrl.length > 1000) {
          return {
            imageSrc: dataUrl,
            width: Math.round(targetRect.width),
            height: Math.round(targetRect.height)
          }
        } else {
          throw new Error('Screenshot data too small, likely blank')
        }
      } catch (captureErr) {
        console.warn('html-to-image failed, generating placeholder:', captureErr)
        const ph = document.createElement('canvas')
        ph.width = Math.round(targetRect.width)
        ph.height = Math.round(targetRect.height)
        const ctx = ph.getContext('2d')
        ctx.fillStyle = '#f8fafc'
        ctx.fillRect(0, 0, ph.width, ph.height)
        ctx.fillStyle = '#94a3b8'
        ctx.font = '14px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText('页面截图不可用 - 见下方元素清单', ph.width / 2, ph.height / 2)
        return {
          imageSrc: ph.toDataURL('image/jpeg', 0.7),
          width: ph.width,
          height: ph.height
        }
      }
    })()

    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Screenshot timeout')), 5000)
    )

    screenshotData = await Promise.race([screenshotPromise, timeoutPromise])

    // 调整元素位置(相对于截图区域)
    const pageName = getPageLabel(route.path)
    const elements = selections.value.map(s => ({
      tag: s.tag,
      class: s.class,
      text: s.text,
      selector: s.selector,
      component: s.component,
      pageName,
      rect: {
        x: Math.round(s.rect.x - targetRect.left),
        y: Math.round(s.rect.y - targetRect.top),
        w: Math.round(s.rect.w),
        h: Math.round(s.rect.h)
      },
      description: s.description
    }))

    // 存入共享状态
    cobuildState.pendingData = {
      pageUrl: route.path,
      pageName,
      screenshot: screenshotData,
      elements
    }

    // 导航回共建页
    router.push('/co-build')
  } catch (err) {
    console.error('Capture failed', err)
    ElMessage.error('截图失败,请重试')
    cobuildMode.value = true
    // 重新添加事件监听
    document.addEventListener('mouseover', onMouseOver, true)
    document.addEventListener('mouseout', onMouseOut, true)
    document.addEventListener('click', onDocumentClick, true)
    document.addEventListener('scroll', onScroll, true)
    document.addEventListener('touchend', onTouchEnd, { capture: true, passive: false })
    document.addEventListener('touchstart', onTouchStart, { capture: true, passive: true })
    document.addEventListener('touchmove', onTouchMove, { capture: true, passive: true })
  } finally {
    capturing.value = false
  }
}

function cancelSelection() {
  exitCobuildMode()
  router.push('/co-build')
}
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
  min-width: 0;
}

:deep(.el-menu-item span) {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.slide-down-enter-active,
.slide-down-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
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
