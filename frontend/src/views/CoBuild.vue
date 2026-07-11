<template>
  <div class="flex h-full flex-col gap-4 p-4 lg:p-6">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 shadow-sm">
          <el-icon :size="20"><EditPen /></el-icon>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-slate-800">共建</h1>
          <p class="text-xs text-slate-400">提交建议,共同建设更好的系统</p>
        </div>
      </div>
      <el-button type="primary" @click="showLauncher = true">提建议</el-button>
    </div>

    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <SuggestionCard
        v-for="s in suggestions"
        :key="s.id"
        :suggestion="s"
        @view="openDetail"
      />
    </div>
    <div v-if="suggestions.length === 0" class="py-12 text-center text-slate-400">
      暂无意见,点击"提建议"提交第一条
    </div>

    <ScreenshotLauncher
      v-model:visible="showLauncher"
      @start-screenshot="startCobuild"
    />

    <SuggestionForm
      :visible="showForm"
      :screenshot="currentScreenshot"
      :elements="currentElements"
      :page-url="currentPageUrl"
      @cancel="onFormCancel"
      @submit="submitSuggestion"
    />

    <SuggestionDetail
      v-model="showDetail"
      :detail="currentDetail"
      :is-admin="userStore.isAdmin"
      @refresh="loadDetail"
      @delete="loadList"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { EditPen } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { getSuggestions, getSuggestionDetail, createSuggestion } from '@/api/suggestion'
import { cobuildState } from '@/composables/cobuildData'
import ScreenshotLauncher from '@/components/cobuild/ScreenshotLauncher.vue'
import SuggestionForm from '@/components/cobuild/SuggestionForm.vue'
import SuggestionCard from '@/components/cobuild/SuggestionCard.vue'
import SuggestionDetail from '@/components/cobuild/SuggestionDetail.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const suggestions = ref([])
const showLauncher = ref(false)
const showForm = ref(false)
const showDetail = ref(false)
const currentDetail = ref(null)
const currentPageUrl = ref('')
const currentScreenshot = ref({})
const currentElements = ref([])

onMounted(() => {
  loadList()
  checkPendingData()
})

watch(() => route.path, (path) => {
  if (path === '/co-build') {
    checkPendingData()
  }
})

function checkPendingData() {
  if (cobuildState.pendingData) {
    const data = cobuildState.pendingData
    cobuildState.pendingData = null

    // 如果已有进行中的数据,追加并更新截图
    if (cobuildState.inProgress) {
      cobuildState.inProgress.elements.push(...data.elements)
      cobuildState.inProgress.screenshot = data.screenshot
      cobuildState.inProgress.pageUrl = data.pageUrl
      cobuildState.inProgress.pageName = data.pageName
    } else {
      cobuildState.inProgress = {
        pageUrl: data.pageUrl,
        pageName: data.pageName,
        screenshot: data.screenshot,
        elements: data.elements
      }
    }

    currentScreenshot.value = cobuildState.inProgress.screenshot
    currentElements.value = cobuildState.inProgress.elements
    currentPageUrl.value = cobuildState.inProgress.pageUrl
    showForm.value = true
    return
  }

  // 有进行中的数据(从其他页面跳回但没有新数据)
  if (cobuildState.inProgress && cobuildState.inProgress.elements.length > 0) {
    currentScreenshot.value = cobuildState.inProgress.screenshot
    currentElements.value = cobuildState.inProgress.elements
    currentPageUrl.value = cobuildState.inProgress.pageUrl
    showForm.value = true
  }
}

async function loadList() {
  try {
    const res = await getSuggestions({ page: 1, page_size: 50 })
    if (res.code === 200) suggestions.value = res.data.items
  } catch (e) { ElMessage.error('加载列表失败') }
}

function startCobuild(pageUrl) {
  if (!cobuildState.inProgress) {
    cobuildState.inProgress = {
      pageUrl,
      screenshot: {},
      elements: []
    }
  } else {
    cobuildState.inProgress.pageUrl = pageUrl
  }
  currentPageUrl.value = pageUrl
  showLauncher.value = false

  // 导航到目标页面并进入元素选择模式
  router.push(pageUrl + '?cobuild=1')
}

function onFormCancel() {
  cobuildState.inProgress = null
  cobuildState.pendingData = null
  currentElements.value = []
  currentScreenshot.value = {}
  showForm.value = false
}

async function openDetail(id) {
  showDetail.value = true
  await loadDetail(id)
}

async function loadDetail(id) {
  try {
    const res = await getSuggestionDetail(id || currentDetail.value?.id)
    if (res.code === 200) currentDetail.value = res.data
  } catch (e) { ElMessage.error('加载详情失败') }
}

async function submitSuggestion(formData) {
  try {
    const payload = {
      title: formData.title,
      description: formData.description,
      category: formData.category,
      page_url: formData.page_url,
      is_anonymous: formData.is_anonymous || false,
      screenshots: [{
        image_data: formData.screenshot.imageSrc,
        width: formData.screenshot.width,
        height: formData.screenshot.height,
        annotations: formData.elements.map(el => ({
          type: 'element',
          coords: {
            tag: el.tag,
            class: el.class,
            text: el.text,
            selector: el.selector,
            component: el.component,
            pageName: el.pageName || '',
            x: el.rect.x,
            y: el.rect.y,
            w: el.rect.w,
            h: el.rect.h
          },
          text: el.description,
          color: '#EF4444'
        }))
      }]
    }
    const res = await createSuggestion(payload)
    if (res.code === 200) {
      ElMessage.success('提交成功')
      cobuildState.inProgress = null
      cobuildState.pendingData = null
      currentElements.value = []
      currentScreenshot.value = {}
      showForm.value = false
      loadList()
    }
  } catch (e) { ElMessage.error('提交失败') }
}
</script>
