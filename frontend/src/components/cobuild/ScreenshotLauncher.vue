<template>
  <el-dialog v-model="visible" title="选择截图页面" width="400px">
    <p class="mb-3 text-sm text-slate-500">选择要反馈的页面,点击后将在新标签页打开并进入截图模式</p>
    <el-select v-model="selectedPage" placeholder="请选择页面" class="w-full mb-4">
      <el-option v-for="p in pages" :key="p.url" :label="p.label" :value="p.url" />
    </el-select>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="!selectedPage" @click="onStart">前往截图</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ visible: Boolean })
const emit = defineEmits(['update:visible', 'start-screenshot'])

const visible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v)
})
const selectedPage = ref('')

const pages = [
  { label: '首页概览', url: '/home' },
  { label: '会议室预约', url: '/rooms' },
  { label: '招新面试', url: '/recruitment' },
  { label: '竞赛队伍', url: '/teams-center' },
  { label: '通讯录', url: '/contacts' },
  { label: '账号设置', url: '/settings' },
  { label: '成员管理', url: '/users' },
  { label: '日程管理', url: '/admin/schedule' },
  { label: '会议室管理', url: '/admin/rooms' },
  { label: '招新管理', url: '/admin/management' },
  { label: '赛事管理', url: '/admin/events' },
]

function onStart() {
  emit('start-screenshot', selectedPage.value)
  visible.value = false
}
</script>
