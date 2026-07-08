<template>
  <div class="flex h-full flex-col gap-4 p-4 lg:p-6">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 shadow-sm">
          <el-icon :size="16"><EditPen /></el-icon>
        </div>
        <h1 class="text-xl font-bold text-slate-800">共建</h1>
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
      @start-screenshot="startScreenshot"
    />

    <AnnotationEditor
      :visible="showEditor"
      :screenshots="editorScreenshots"
      :page-url="currentPageUrl"
      @cancel="showEditor = false"
      @add-screenshot="addScreenshot"
      @submit="submitSuggestion"
    />

    <SuggestionDetail
      v-model="showDetail"
      :detail="currentDetail"
      :is-admin="userStore.isAdmin"
      @refresh="loadDetail"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { EditPen } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { getSuggestions, getSuggestionDetail, createSuggestion } from '@/api/suggestion'
import ScreenshotLauncher from '@/components/cobuild/ScreenshotLauncher.vue'
import AnnotationEditor from '@/components/cobuild/AnnotationEditor.vue'
import SuggestionCard from '@/components/cobuild/SuggestionCard.vue'
import SuggestionDetail from '@/components/cobuild/SuggestionDetail.vue'

const userStore = useUserStore()
const suggestions = ref([])
const showLauncher = ref(false)
const showEditor = ref(false)
const showDetail = ref(false)
const currentDetail = ref(null)
const currentPageUrl = ref('')
const editorScreenshots = ref([])

onMounted(loadList)

async function loadList() {
  try {
    const res = await getSuggestions({ page: 1, page_size: 50 })
    if (res.code === 200) suggestions.value = res.data.items
  } catch (e) { ElMessage.error('加载列表失败') }
}

function startScreenshot(pageUrl) {
  currentPageUrl.value = pageUrl
  editorScreenshots.value = []
  showLauncher.value = false
  const url = `${window.location.origin}${pageUrl}?screenshot=1`
  window.open(url, '_blank')
  window.addEventListener('message', onScreenshotMessage, { once: true })
  showEditor.value = true
}

function onScreenshotMessage(e) {
  if (e.data?.type === 'screenshot') {
    editorScreenshots.value.push({
      imageSrc: e.data.imageSrc,
      width: e.data.width,
      height: e.data.height,
      annotations: []
    })
  }
}

function addScreenshot() {
  const url = `${window.location.origin}${currentPageUrl.value}?screenshot=1`
  window.open(url, '_blank')
  window.addEventListener('message', onScreenshotMessage, { once: true })
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
      screenshots: formData.screenshots.map(sc => ({
        image_data: sc.imageSrc,
        width: sc.width,
        height: sc.height,
        annotations: sc.annotations
      }))
    }
    const res = await createSuggestion(payload)
    if (res.code === 200) {
      ElMessage.success('提交成功')
      showEditor.value = false
      loadList()
    }
  } catch (e) { ElMessage.error('提交失败') }
}
</script>
