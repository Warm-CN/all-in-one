<template>
  <el-drawer v-model="drawerVisible" title="提交共建意见" size="500px" :close-on-click-modal="false">
    <div class="flex h-full flex-col gap-4">
      <!-- 截图预览 + 元素方框 -->
      <div v-if="screenshot?.imageSrc" class="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
        <img
          ref="previewImg"
          :src="screenshot.imageSrc"
          class="block w-full"
          alt="页面截图"
          @load="onImgLoad"
        />
        <!-- 编号方框 -->
        <div
          v-for="(el, idx) in elements"
          :key="idx"
          class="absolute border-2 border-red-500"
          :style="boxStyle(el, idx)"
        >
          <span class="absolute -top-2 -left-2 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            {{ idx + 1 }}
          </span>
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
</template>

<script setup>
import { ref, watch, computed } from 'vue'

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

watch(() => props.visible, (v) => {
  if (v) {
    form.value = { title: '', category: 'other', description: '', is_anonymous: false }
    imgScale.value = 1
  }
})

function onImgLoad() {
  if (previewImg.value && props.screenshot?.width) {
    imgScale.value = previewImg.value.offsetWidth / props.screenshot.width
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
