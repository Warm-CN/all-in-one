<template>
  <el-drawer v-model="visible" size="100%" class="cobuild-detail-drawer">
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
      <div v-if="firstScreenshot">
        <div
          class="relative cursor-pointer overflow-hidden rounded-xl border border-slate-200 bg-slate-50"
          style="height: 200px;"
          @click="previewFull = true"
        >
          <div v-if="screenshotBlobUrl" class="relative" :style="{ width: (firstScreenshot.width || 400) + 'px', transformOrigin: 'top left', transform: `scale(${previewScale})` }">
            <img :src="screenshotBlobUrl" class="block" alt="页面截图" @load="onImgLoad" ref="screenshotImg" />
            <!-- 编号方框 -->
            <div
              v-for="(ann, idx) in elementAnnotations"
              :key="ann.id || idx"
              class="absolute border-2 border-blue-500"
              :style="boxStyle(ann, idx)"
            >
              <span class="absolute -top-2 -left-2 flex h-5 w-5 items-center justify-center rounded-full bg-blue-500 text-[10px] font-bold text-white">
                {{ idx + 1 }}
              </span>
            </div>
          </div>
          <div v-else class="flex h-full items-center justify-center">
            <el-icon class="is-loading" :size="24"><Loading /></el-icon>
            <span class="ml-2 text-sm text-slate-400">加载截图...</span>
          </div>
        </div>
        <div class="mt-1 flex items-center justify-center gap-1">
          <el-icon :size="14" class="text-slate-400"><ZoomIn /></el-icon>
          <span class="text-xs text-slate-400">点击查看完整截图</span>
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
              <span class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-500 text-[10px] font-bold text-white">{{ idx + 1 }}</span>
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
        <div class="flex items-center justify-between">
          <h4 class="font-bold text-slate-700">状态管理</h4>
          <el-button type="danger" size="small" plain @click="onDeleteSuggestion">删除意见</el-button>
        </div>
        <div class="flex flex-wrap gap-2">
          <el-select v-model="newStatus" placeholder="选择状态" class="w-40">
            <el-option
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
              :disabled="opt.disabled"
            />
          </el-select>
          <el-input v-if="newStatus === 'wont_fix'" v-model="statusReason" placeholder="必须填写说明/原因" class="w-60" />
          <el-input v-else v-model="statusReason" placeholder="说明/原因（可选）" class="w-60" />
          <el-button type="primary" :disabled="!newStatus || (newStatus === 'wont_fix' && !statusReason)" @click="onStatusUpdate">更新</el-button>
        </div>
      </template>

      <!-- 讨论区 -->
      <div>
        <h4 class="mb-2 font-bold text-slate-700">讨论区</h4>
        <DiscussionThread
          :replies="detail.replies"
          :is-admin="isAdmin"
          @endorse="onEndorse"
          @reply="onReply"
          @delete-reply="onDeleteReply"
        />
      </div>
    </div>
  </el-drawer>

  <!-- 全屏预览截图（含标注） -->
  <el-image-viewer
    v-if="previewFull && fullImageSrc"
    :url-list="[fullImageSrc]"
    @close="previewFull = false"
  />
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, ZoomIn } from '@element-plus/icons-vue'
import DiscussionThread from './DiscussionThread.vue'
import { updateSuggestionStatus, createReply, toggleEndorse, deleteReply, deleteSuggestion, fetchScreenshotImage } from '@/api/suggestion'
import { getPageLabel } from '@/composables/cobuildData'

const props = defineProps({
  modelValue: Boolean,
  detail: Object,
  isAdmin: Boolean
})
const emit = defineEmits(['update:modelValue', 'refresh', 'delete'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})
const newStatus = ref('')
const statusReason = ref('')
const imgScale = ref(1)
const screenshotImg = ref(null)
const screenshotBlobUrl = ref('')
const previewFull = ref(false)
const previewScale = ref(1)
const fullImageSrc = ref('')

watch(() => props.detail?.id, async (newId) => {
  if (screenshotBlobUrl.value) URL.revokeObjectURL(screenshotBlobUrl.value)
  screenshotBlobUrl.value = ''
  imgScale.value = 1
  previewScale.value = 1
  fullImageSrc.value = ''
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

const VALID_TRANSITIONS = {
  received: ['pending_fix', 'wont_fix'],
  pending_fix: ['fixing', 'wont_fix'],
  fixing: ['done', 'wont_fix'],
  done: [],
  wont_fix: ['pending_fix'],
}

const statusOptions = computed(() => {
  const current = props.detail?.status || 'received'
  const allowed = VALID_TRANSITIONS[current] || []
  return [
    { label: '等待修改', value: 'pending_fix', disabled: !allowed.includes('pending_fix') },
    { label: '修改中', value: 'fixing', disabled: !allowed.includes('fixing') },
    { label: '不予修改', value: 'wont_fix', disabled: !allowed.includes('wont_fix') },
    { label: '修改成功', value: 'done', disabled: !allowed.includes('done') },
  ]
})

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
  if (screenshotImg.value) {
    const container = screenshotImg.value.closest('.cursor-pointer')
    const containerW = container ? container.offsetWidth : 300
    const naturalW = firstScreenshot.value?.width || screenshotImg.value.naturalWidth
    if (naturalW > 0) {
      previewScale.value = Math.min(1, containerW / naturalW)
    }
    if (firstScreenshot.value?.width) {
      imgScale.value = (naturalW * previewScale.value) / firstScreenshot.value.width
    }
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

async function buildFullImage() {
  if (!screenshotBlobUrl.value) return
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.src = screenshotBlobUrl.value
  await new Promise((resolve, reject) => {
    img.onload = resolve
    img.onerror = reject
  })

  const sc = firstScreenshot.value
  const w = sc?.width || img.naturalWidth
  const h = sc?.height || img.naturalHeight
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  ctx.drawImage(img, 0, 0, w, h)

  // 绘制蓝框 + 编号
  elementAnnotations.value.forEach((ann, idx) => {
    const c = annCoords(ann)
    const x = c.x || 0
    const y = c.y || 0
    const rw = c.w || 0
    const rh = c.h || 0

    ctx.fillStyle = 'rgba(59, 130, 246, 0.08)'
    ctx.fillRect(x, y, rw, rh)
    ctx.strokeStyle = '#3B82F6'
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, rw, rh)

    const badgeR = 11
    const bx = x - 2
    const by = y - 2
    ctx.fillStyle = '#3B82F6'
    ctx.beginPath()
    ctx.arc(bx, by, badgeR, 0, Math.PI * 2)
    ctx.fill()

    ctx.fillStyle = '#FFFFFF'
    ctx.font = 'bold 11px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(String(idx + 1), bx, by)
  })

  fullImageSrc.value = canvas.toDataURL('image/jpeg', 0.85)
}

watch(previewFull, async (v) => {
  if (v && !fullImageSrc.value && screenshotBlobUrl.value) {
    await buildFullImage()
  }
})

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

async function onDeleteReply(replyId) {
  try {
    await deleteReply(replyId)
    ElMessage.success('评论已删除')
    emit('refresh')
  } catch (e) { ElMessage.error('删除失败') }
}

function onDeleteSuggestion() {
  ElMessageBox.confirm('确定删除这条意见吗？所有评论和截图将一并删除。', '删除意见', { type: 'warning' })
    .then(async () => {
      try {
        await deleteSuggestion(props.detail.id)
        ElMessage.success('意见已删除')
        visible.value = false
        emit('delete')
      } catch (e) { ElMessage.error('删除失败') }
    })
    .catch(() => {})
}
</script>

<style scoped>
@media (min-width: 640px) {
  .cobuild-detail-drawer :deep(.el-drawer) {
    width: 70% !important;
  }
}
</style>
