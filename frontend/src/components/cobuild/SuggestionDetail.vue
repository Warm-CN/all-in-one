<template>
  <el-drawer v-model="visible" :title="detail?.title || '详情'" size="60%">
    <div v-if="detail">
      <el-descriptions :column="2" border class="mb-4">
        <el-descriptions-item label="分类">{{ categoryLabel }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType">{{ statusLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="关联页面">{{ detail.page_url }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ detail.description }}</el-descriptions-item>
      </el-descriptions>
      <h4 class="mb-2 font-bold">批注文字清单</h4>
      <div class="mb-4 space-y-1">
        <div v-for="sc in detail.screenshots" :key="sc.id" class="rounded border p-2">
          <p class="text-xs font-semibold text-slate-500">截图 {{ sc.index }}</p>
          <div v-for="ann in sc.annotations" :key="ann.id" class="text-sm">
            框 {{ ann.index }} ({{ ann.type }}): {{ ann.text }}
          </div>
        </div>
      </div>
      <h4 class="mb-2 font-bold">截图</h4>
      <div class="mb-4 flex flex-wrap gap-2">
        <div v-for="sc in detail.screenshots" :key="sc.id">
          <img :src="screenshotImageUrl(sc.id)" class="h-24 rounded border" />
        </div>
      </div>
      <template v-if="isAdmin">
        <h4 class="mb-2 font-bold">状态管理</h4>
        <div class="mb-4 flex gap-2">
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
      <h4 class="mb-2 font-bold">讨论区</h4>
      <DiscussionThread
        :replies="detail.replies"
        @endorse="onEndorse"
        @reply="onReply"
      />
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import DiscussionThread from './DiscussionThread.vue'
import { updateSuggestionStatus, createReply, toggleEndorse, screenshotImageUrl } from '@/api/suggestion'

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

const categoryLabel = computed(() => ({ layout: '布局美化', feature: '功能优化', bug: 'Bug反馈', other: '其他' }[props.detail?.category] || ''))
const statusLabel = computed(() => ({ received: '已收到', pending_fix: '等待修改', fixing: '修改中', wont_fix: '不予修改', done: '修改成功' }[props.detail?.status] || ''))
const statusType = computed(() => ({ received: 'info', pending_fix: 'warning', fixing: 'primary', wont_fix: 'danger', done: 'success' }[props.detail?.status] || 'info'))

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

async function onReply(content) {
  try {
    await createReply(props.detail.id, { content })
    ElMessage.success('评论成功')
    emit('refresh')
  } catch (e) { ElMessage.error('评论失败') }
}
</script>
