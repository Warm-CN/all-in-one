<template>
  <div class="space-y-3">
    <div v-for="reply in replies" :key="reply.id" class="rounded-lg bg-slate-50 p-3">
      <div class="mb-1 flex items-center justify-between">
        <span class="text-xs font-semibold text-slate-600">用户{{ reply.author_id }}</span>
        <span class="text-xs text-slate-400">{{ reply.created_at }}</span>
      </div>
      <p class="mb-2 text-sm text-slate-700">{{ reply.content }}</p>
      <el-button link size="small" :type="reply.endorsed ? 'primary' : 'default'" @click="$emit('endorse', reply.id)">
        复议 ({{ reply.endorse_count }})
      </el-button>
    </div>
    <div v-if="replies.length === 0" class="py-4 text-center text-sm text-slate-400">暂无讨论</div>
    <div class="flex gap-2">
      <el-input v-model="content" placeholder="发表评论..." />
      <el-button type="primary" @click="submit">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const props = defineProps({ replies: Array })
const emit = defineEmits(['endorse', 'reply'])
const content = ref('')
function submit() {
  if (!content.value.trim()) return
  emit('reply', content.value)
  content.value = ''
}
</script>
