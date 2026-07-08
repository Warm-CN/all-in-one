<template>
  <el-dialog v-model="visible" title="选择反馈页面" width="420px" :close-on-click-modal="false">
    <p class="mb-4 text-sm text-slate-500">选择要反馈的页面,将跳转到该页面后,点击需要反馈的页面元素并描述问题</p>
    <el-select v-model="selectedPage" placeholder="请选择页面" class="w-full mb-2" filterable>
      <el-option v-for="p in pages" :key="p.url" :label="p.label" :value="p.url" />
    </el-select>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="!selectedPage" @click="onStart">前往页面</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'

const props = defineProps({ visible: Boolean })
const emit = defineEmits(['update:visible', 'start-screenshot'])
const userStore = useUserStore()

const visible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v)
})
const selectedPage = ref('')

const allPages = [
  { label: '首页概览', url: '/home', adminOnly: false },
  { label: '会议室预约', url: '/rooms', adminOnly: false },
  { label: '招新面试', url: '/recruitment', adminOnly: false },
  { label: '竞赛队伍', url: '/teams-center', adminOnly: false },
  { label: '通讯录', url: '/contacts', adminOnly: false },
  { label: '账号设置', url: '/settings', adminOnly: false },
  { label: '成员管理', url: '/users', adminOnly: true },
  { label: '日程管理', url: '/admin/schedule', adminOnly: true },
  { label: '会议室管理', url: '/admin/rooms', adminOnly: true },
  { label: '招新管理', url: '/admin/management', adminOnly: true },
  { label: '赛事管理', url: '/admin/events', adminOnly: true },
]

const pages = computed(() => {
  if (userStore.userRole === 'admin') return allPages
  return allPages.filter(p => !p.adminOnly)
})

function onStart() {
  emit('start-screenshot', selectedPage.value)
  visible.value = false
}
</script>
