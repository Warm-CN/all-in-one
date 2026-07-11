<template>
  <div class="space-y-3">
    <div v-for="reply in replies" :key="reply.id" class="rounded-lg bg-slate-50 p-3">
      <div class="mb-1 flex items-center justify-between">
        <span class="text-xs font-semibold text-slate-600">
          {{ reply.is_anonymous ? '匿名用户' : (reply.author_name || '用户' + reply.author_id) }}
        </span>
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">{{ reply.created_at }}</span>
          <el-button v-if="isAdmin" link size="small" type="danger" @click="onDeleteReply(reply.id)">删除</el-button>
        </div>
      </div>
      <p class="mb-2 text-sm text-slate-700">{{ reply.content }}</p>
      <el-button link size="small" :type="reply.endorsed ? 'primary' : 'default'" @click="$emit('endorse', reply.id)">
        复议 ({{ reply.endorse_count }})
      </el-button>
    </div>
    <div v-if="replies.length === 0" class="py-4 text-center text-sm text-slate-400">暂无讨论</div>
    <div class="space-y-2">
      <div class="flex items-center gap-3">
        <span class="text-xs text-slate-500">署名:</span>
        <el-radio-group v-model="isAnonymous" size="small">
          <el-radio-button :value="false">实名</el-radio-button>
          <el-radio-button :value="true">匿名</el-radio-button>
        </el-radio-group>
      </div>
      <div class="flex gap-2">
        <el-input v-model="content" placeholder="发表评论..." @keyup.enter="submit" />
        <el-button type="primary" @click="submit">发送</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const props = defineProps({ replies: Array, isAdmin: Boolean })
const emit = defineEmits(['endorse', 'reply', 'delete-reply'])
const content = ref('')
const isAnonymous = ref(false)

function submit() {
  if (!content.value.trim()) return
  emit('reply', { content: content.value, is_anonymous: isAnonymous.value })
  content.value = ''
}

function onDeleteReply(replyId) {
  ElMessageBox.confirm('确定删除这条评论吗？', '提示', { type: 'warning' })
    .then(() => emit('delete-reply', replyId))
    .catch(() => {})
}
</script>
