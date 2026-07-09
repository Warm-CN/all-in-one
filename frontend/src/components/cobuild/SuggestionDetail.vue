<template>
  <el-drawer v-model="visible" size="70%">
    <template #header>
      <div v-if="detail" class="flex flex-col gap-1">
        <h2 class="text-xl font-bold text-slate-800">{{ detail.title }}</h2>
        <p class="text-sm text-slate-400">
          提出者:
          <span v-if="detail.is_anonymous" class="text-slate-400">匿名用户</span>
          <span v-else class="font-medium text-slate-600">{{ detail.author_name || '未知' }}</span>
        </p>
      </div>
      <span v-else>详情</span>
    </template>
    <div v-if="detail" class="flex flex-col gap-4">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="分类">{{ categoryLabel }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType">{{ statusLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="关联页面">{{ pageLabel }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ detail.description }}</el-descriptions-item>
      </el-descriptions>

      <!-- 截图 + 元素方框 -->
      <div v-if="firstScreenshot" class="relative overflow-auto rounded-xl border border-slate-200 bg-slate-50">
        <div class="relative inline-block">
          <img v-if="screenshotBlobUrl" :src="screenshotBlobUrl" class="block" alt="页面截图" @load="onImgLoad" ref="screenshotImg" />
          <div v-else class="flex items-center justify-center" style="width: 400px; height: 200px;">
            <el-icon class="is-loading" :size="24"><Loading /></el-icon>
            <span class="ml-2 text-sm text-slate-400">加载截图...</span>
          </div>
          <!-- 编号方框 -->
          <div
            v-for="(ann, idx) in elementAnnotations"
            :key="ann.id || idx"
            class="absolute border-2 border-red-500"
            :style="boxStyle(ann, idx)"
          >
            <span class="absolute -top-2 -left-2 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
              {{ idx + 1 }}
            </span>
          </div>
        </div>
      </div>

      <!-- 元素问题清单 -->
      <div v-if="elementAnnotations.length > 0">
        <h4 class="mb-2 font-bold text-slate-700">问题元素清单</h4>
        <div class="space-y-2">
          <div
            v-for="(ann, idx) in elementAnnotations"
            :key="ann.id || idx"
            class="rounded-lg border border-slate-200 p-3"
          >
            <div class="flex items-center gap-2">
              <span class="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">{{ idx + 1 }}</span>
              <span v-if="annCoords(ann).pageName" class="rounded bg-emerald-50 px-1.5 py-0.5 text-xs font-medium text-emerald-600">{{ annCoords(ann).pageName }}</span>
              <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-600">{{ annCoords(ann).tag }}</span>
              <span v-if="annCoords(ann).component" class="text-xs text-indigo-500">{{ annCoords(ann).component }}.vue</span>
            </div>
            <p v-if="annCoords(ann).text" class="mt-1 text-xs text-slate-400 truncate">元素文本: {{ annCoords(ann).text }}</p>
            <p v-if="annCoords(ann).selector" class="mt-0.5 text-xs text-slate-400 truncate">选择器: {{ annCoords(ann).selector }}</p>
            <p class="mt-1 text-sm text-slate-700">{{ ann.text }}</p>
          </div>
        </div>
      </div>

      <!-- 状态管理 -->
      <template v-if="isAdmin">
        <h4 class="mb-2 font-bold text-slate-700">状态管理</h4>
        <div class="flex flex-wrap gap-2">
          <el-select v-model="newStatus" placeholder="选择状态" class="w-40">
            <el-option label="等待修改" value="pending_fix" />
            <el-option label="修改中" value="fixing" />
            <el-option label="不予修改" value="wont_fix" />
            <el-option label="修改成功" value="done" />
          </el-select>
          <el-input v-model="statusReason" placeholder="说明/原因" class="w-60" />
          <el-button type="primary" @click="onStatusUpdate">更新</el-button>
        </div>
      </template>

      <!-- 讨论区 -->
      <div>
        <h4 class="mb-2 font-bold text-slate-700">讨论区</h4>
        <DiscussionThread
          :replies="detail.replies"
          @endorse="onEndorse"
          @reply="onReply"
        />
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import DiscussionThread from './DiscussionThread.vue'
import { updateSuggestionStatus, createReply, toggleEndorse, fetchScreenshotImage } from '@/api/suggestion'
import { getPageLabel } from '@/composables/cobuildData'

const props = defineProps({
  modelValue: Boolean,
  detail: Object,
  isAdmin: Boolean
})
const emit = defineEmits(['update:modelValue', 'refresh'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})
const newStatus = ref('')
const statusReason = ref('')
const imgScale = ref(1)
const screenshotImg = ref(null)
const screenshotBlobUrl = ref('')

watch(() => props.detail?.id, async (newId) => {
  if (screenshotBlobUrl.value) URL.revokeObjectURL(screenshotBlobUrl.value)
  screenshotBlobUrl.value = ''
  imgScale.value = 1
  if (!newId) return
  const sc = props.detail?.screenshots?.[0]
  if (!sc) return
  try {
    const blob = await fetchScreenshotImage(sc.id)
    screenshotBlobUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    console.error('Failed to load screenshot:', e)
  }
}, { immediate: true })

onUnmounted(() => {
  if (screenshotBlobUrl.value) URL.revokeObjectURL(screenshotBlobUrl.value)
})

const categoryLabel = computed(() => ({ layout: '布局美化', feature: '功能优化', bug: 'Bug反馈', other: '其他' }[props.detail?.category] || ''))
const statusLabel = computed(() => ({ received: '已收到', pending_fix: '等待修改', fixing: '修改中', wont_fix: '不予修改', done: '修改成功' }[props.detail?.status] || ''))
const statusType = computed(() => ({ received: 'info', pending_fix: 'warning', fixing: 'primary', wont_fix: 'danger', done: 'success' }[props.detail?.status] || 'info'))
const pageLabel = computed(() => getPageLabel(props.detail?.page_url) || '未关联')

const firstScreenshot = computed(() => {
  return props.detail?.screenshots?.[0] || null
})

const elementAnnotations = computed(() => {
  if (!firstScreenshot.value) return []
  return firstScreenshot.value.annotations || []
})

function annCoords(ann) {
  if (typeof ann.coords === 'string') {
    try { return JSON.parse(ann.coords) } catch { return {} }
  }
  return ann.coords || {}
}

function onImgLoad() {
  // 计算缩放比例(如果图片被CSS缩放了)
  if (screenshotImg.value && firstScreenshot.value) {
    const naturalW = firstScreenshot.value.width || screenshotImg.value.naturalWidth
    const displayedW = screenshotImg.value.offsetWidth
    imgScale.value = displayedW / naturalW
  }
}

function boxStyle(ann, idx) {
  const c = annCoords(ann)
  const s = imgScale.value
  return {
    left: (c.x || 0) * s + 'px',
    top: (c.y || 0) * s + 'px',
    width: (c.w || 0) * s + 'px',
    height: (c.h || 0) * s + 'px'
  }
}

async function onStatusUpdate() {
  if (!newStatus.value) return ElMessage.warning('请选择状态')
  try {
    await updateSuggestionStatus(props.detail.id, { status: newStatus.value, reason: statusReason.value })
    ElMessage.success('状态已更新')
    newStatus.value = ''
    statusReason.value = ''
    emit('refresh')
  } catch (e) { ElMessage.error('更新失败') }
}

async function onEndorse(replyId) {
  try {
    await toggleEndorse(replyId)
    emit('refresh')
  } catch (e) { ElMessage.error('操作失败') }
}

async function onReply(replyData) {
  try {
    await createReply(props.detail.id, { content: replyData.content, is_anonymous: replyData.is_anonymous })
    ElMessage.success('评论成功')
    emit('refresh')
  } catch (e) { ElMessage.error('评论失败') }
}
</script>
