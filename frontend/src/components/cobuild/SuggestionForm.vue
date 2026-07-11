<template>
  <el-drawer v-model="drawerVisible" title="提交共建意见" size="100%" :close-on-click-modal="false" class="cobuild-drawer">
    <div class="flex h-full flex-col gap-4">
      <!-- 截图预览 + 元素方框 -->
      <div v-if="screenshot?.imageSrc">
        <div
          class="relative cursor-pointer overflow-hidden rounded-xl border border-slate-200 bg-slate-50"
          style="height: 200px;"
          @click="previewFull = true"
        >
          <div class="relative" :style="{ width: screenshot.width + 'px', transformOrigin: 'top left', transform: `scale(${previewScale})` }">
            <img
              ref="previewImg"
              :src="screenshot.imageSrc"
              class="block"
              alt="页面截图"
              @load="onImgLoad"
            />
            <!-- 编号方框 -->
            <div
              v-for="(el, idx) in elements"
              :key="idx"
              class="absolute border-2 border-blue-500"
              :style="boxStyle(el, idx)"
            >
              <span class="absolute -top-2 -left-2 flex h-5 w-5 items-center justify-center rounded-full bg-blue-500 text-[10px] font-bold text-white">
                {{ idx + 1 }}
              </span>
            </div>
          </div>
        </div>
        <div class="mt-1 flex items-center justify-center gap-1">
          <el-icon :size="14" class="text-slate-400"><ZoomIn /></el-icon>
          <span class="text-xs text-slate-400">点击查看完整截图</span>
        </div>
      </div>

      <!-- 元素清单 -->
      <div class="space-y-2">
        <h4 class="text-sm font-bold text-slate-700">问题元素清单 ({{ elements.length }})</h4>
        <div
          v-for="(el, idx) in elements"
          :key="idx"
          class="rounded-lg border border-slate-200 p-3"
        >
          <div class="flex items-center gap-2">
            <span class="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">{{ idx + 1 }}</span>
            <span v-if="el.pageName" class="rounded bg-emerald-50 px-1.5 py-0.5 text-xs font-medium text-emerald-600">{{ el.pageName }}</span>
            <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-600">{{ el.tag }}</span>
            <span v-if="el.component" class="text-xs text-indigo-500">{{ el.component }}.vue</span>
          </div>
          <p v-if="el.text" class="mt-1 text-xs text-slate-400 truncate">{{ el.text }}</p>
          <p class="mt-1 text-sm text-slate-700">{{ el.description }}</p>
        </div>
      </div>

      <!-- 意见表单 -->
      <el-form label-position="top" class="mt-2">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="一句话概括问题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" class="w-full">
            <el-option label="布局美化" value="layout" />
            <el-option label="功能优化" value="feature" />
            <el-option label="Bug反馈" value="bug" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="补充描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="其他需要说明的内容(可选)" />
        </el-form-item>
        <el-form-item label="署名方式">
          <el-radio-group v-model="form.is_anonymous">
            <el-radio :value="false">实名</el-radio>
            <el-radio :value="true">匿名</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="flex gap-2">
        <el-button @click="onCancel">取消</el-button>
        <el-button type="primary" :disabled="!form.title" @click="onSubmit">提交意见</el-button>
      </div>
    </template>
  </el-drawer>

  <!-- 全屏预览截图（含标注） -->
  <el-image-viewer
    v-if="previewFull && fullImageSrc"
    :url-list="[fullImageSrc]"
    @close="previewFull = false"
  />
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ZoomIn } from '@element-plus/icons-vue'

const props = defineProps({
  visible: Boolean,
  screenshot: { type: Object, default: () => ({}) },
  elements: { type: Array, default: () => [] },
  pageUrl: String
})
const emit = defineEmits(['cancel', 'submit'])

const drawerVisible = computed({
  get: () => props.visible,
  set: (v) => { if (!v) emit('cancel') }
})

const form = ref({ title: '', category: 'other', description: '', is_anonymous: false })
const imgScale = ref(1)
const previewImg = ref(null)
const previewFull = ref(false)
const previewScale = ref(1)
const fullImageSrc = ref('')

watch(() => props.visible, (v) => {
  if (v) {
    form.value = { title: '', category: 'other', description: '', is_anonymous: false }
    imgScale.value = 1
    previewScale.value = 1
    fullImageSrc.value = ''
  }
})

function onImgLoad() {
  if (previewImg.value) {
    const container = previewImg.value.closest('.cursor-pointer')
    const containerW = container ? container.offsetWidth : 300
    const naturalW = props.screenshot?.width || previewImg.value.naturalWidth
    if (naturalW > 0) {
      previewScale.value = Math.min(1, containerW / naturalW)
    }
    if (props.screenshot?.width) {
      imgScale.value = (naturalW * previewScale.value) / props.screenshot.width
    }
  }
}

function boxStyle(el, idx) {
  const s = imgScale.value
  return {
    left: (el.rect?.x || 0) * s + 'px',
    top: (el.rect?.y || 0) * s + 'px',
    width: (el.rect?.w || 0) * s + 'px',
    height: (el.rect?.h || 0) * s + 'px'
  }
}

async function buildFullImage() {
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.src = props.screenshot.imageSrc
  await new Promise((resolve, reject) => {
    img.onload = resolve
    img.onerror = reject
  })

  const w = props.screenshot.width || img.naturalWidth
  const h = props.screenshot.height || img.naturalHeight
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  ctx.drawImage(img, 0, 0, w, h)

  // 绘制红框 + 编号
  props.elements.forEach((el, idx) => {
    const r = el.rect || {}
    const x = r.x || 0
    const y = r.y || 0
    const rw = r.w || 0
    const rh = r.h || 0

    // 半透明蓝色填充
    ctx.fillStyle = 'rgba(59, 130, 246, 0.08)'
    ctx.fillRect(x, y, rw, rh)

    // 蓝色边框
    ctx.strokeStyle = '#3B82F6'
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, rw, rh)

    // 编号徽章
    const badgeR = 11
    const bx = x - 2
    const by = y - 2
    ctx.fillStyle = '#3B82F6'
    ctx.beginPath()
    ctx.arc(bx, by, badgeR, 0, Math.PI * 2)
    ctx.fill()

    // 编号文字
    ctx.fillStyle = '#FFFFFF'
    ctx.font = 'bold 11px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(String(idx + 1), bx, by)
  })

  fullImageSrc.value = canvas.toDataURL('image/jpeg', 0.85)
}

watch(previewFull, async (v) => {
  if (v && !fullImageSrc.value && props.screenshot?.imageSrc) {
    await buildFullImage()
  }
})

function onSubmit() {
  emit('submit', {
    title: form.value.title,
    description: form.value.description || '见元素清单',
    category: form.value.category,
    page_url: props.pageUrl,
    is_anonymous: form.value.is_anonymous,
    screenshot: props.screenshot,
    elements: props.elements
  })
}

function onCancel() {
  emit('cancel')
}
</script>

<style scoped>
@media (min-width: 640px) {
  .cobuild-drawer :deep(.el-drawer) {
    width: 500px !important;
  }
}
</style>
