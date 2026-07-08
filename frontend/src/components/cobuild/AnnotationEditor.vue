<template>
  <div class="fixed inset-0 z-50 flex bg-black/60" v-if="visible">
    <div class="flex-1 overflow-auto p-6">
      <div class="mx-auto" style="max-width: 900px;">
        <ScreenshotCanvas
          :image-src="currentScreenshot.imageSrc"
          :tool="activeTool"
          :annotations="currentAnnotations"
          @add-annotation="onAddAnnotation"
        />
      </div>
    </div>
    <div class="w-96 shrink-0 overflow-y-auto bg-white p-6 shadow-xl">
      <h3 class="mb-4 text-lg font-bold">批注工具</h3>
      <div class="mb-4 flex gap-2">
        <el-button :type="activeTool === 'rect' ? 'primary' : 'default'" @click="activeTool = 'rect'">矩形框选</el-button>
        <el-button :type="activeTool === 'freehand' ? 'primary' : 'default'" @click="activeTool = 'freehand'">任意形状</el-button>
        <el-button :type="activeTool === 'text' ? 'primary' : 'default'" @click="activeTool = 'text'">文字标注</el-button>
      </div>
      <el-button @click="undoLast" class="mb-2">撤销</el-button>
      <el-button @click="clearAll" class="mb-2">清空</el-button>
      <h4 class="mb-2 mt-4 text-sm font-bold">截图列表 ({{ screenshots.length }})</h4>
      <div class="flex flex-wrap gap-2 mb-4">
        <div
          v-for="(sc, idx) in screenshots"
          :key="idx"
          @click="switchScreenshot(idx)"
          :class="['cursor-pointer rounded border-2 p-1', idx === currentIndex ? 'border-blue-500' : 'border-gray-200']"
        >
          <img :src="sc.imageSrc" class="h-12 w-16 object-cover" />
          <div class="text-center text-xs">图{{ idx + 1 }}</div>
        </div>
      </div>
      <el-button @click="$emit('add-screenshot')" class="mb-4">+ 添加下一张</el-button>
      <h4 class="mb-2 text-sm font-bold">批注清单</h4>
      <div class="mb-4 space-y-2">
        <div v-for="(ann, idx) in currentAnnotations" :key="idx" class="rounded border p-2 text-sm">
          <span class="font-bold">框{{ idx + 1 }}</span>
          <span class="text-gray-500">({{ ann.type }})</span>
          <p>{{ ann.text }}</p>
          <el-button link type="danger" size="small" @click="removeAnnotation(idx)">删除</el-button>
        </div>
        <p v-if="currentAnnotations.length === 0" class="text-xs text-gray-400">暂无批注</p>
      </div>
      <h4 class="mb-2 text-sm font-bold">意见信息</h4>
      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" class="w-full">
            <el-option label="布局美化" value="layout" />
            <el-option label="功能优化" value="feature" />
            <el-option label="Bug反馈" value="bug" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="详细描述" />
        </el-form-item>
        <el-button type="primary" @click="onSubmit" :disabled="!canSubmit" class="w-full">提交意见</el-button>
        <el-button @click="$emit('cancel')" class="mt-2 w-full">取消</el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ScreenshotCanvas from './ScreenshotCanvas.vue'

const props = defineProps({
  visible: Boolean,
  screenshots: Array,
  pageUrl: String
})
const emit = defineEmits(['cancel', 'submit', 'add-screenshot'])

const activeTool = ref('rect')
const currentIndex = ref(0)
const form = ref({ title: '', category: 'other', description: '' })

const currentScreenshot = computed(() => props.screenshots[currentIndex.value] || { imageSrc: '' })
const currentAnnotations = computed(() => currentScreenshot.value.annotations || [])
const canSubmit = computed(() => form.value.title && form.value.description)

function switchScreenshot(idx) {
  currentIndex.value = idx
}

function onAddAnnotation(ann) {
  ElMessageBox.prompt('请输入该批注的文字说明', '批注说明', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValidator: (val) => !!val || '必须输入文字说明'
  }).then(({ value }) => {
    ann.text = value
    ann.color = '#EF4444'
    currentScreenshot.value.annotations.push(ann)
  }).catch(() => {})
}

function removeAnnotation(idx) {
  currentScreenshot.value.annotations.splice(idx, 1)
}

function undoLast() {
  currentScreenshot.value.annotations.pop()
}

function clearAll() {
  currentScreenshot.value.annotations = []
}

function onSubmit() {
  emit('submit', {
    title: form.value.title,
    description: form.value.description,
    category: form.value.category,
    page_url: props.pageUrl,
    screenshots: props.screenshots
  })
}

watch(() => props.visible, (v) => {
  if (v) {
    currentIndex.value = 0
    form.value = { title: '', category: 'other', description: '' }
  }
})
</script>
