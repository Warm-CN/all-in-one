<template>
  <div class="flex h-full min-h-0 flex-col gap-5 pb-2 sm:gap-6 sm:pb-3">
    <section class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] px-5 pb-5 pt-6 shadow-[0_14px_34px_-28px_rgba(15,23,42,0.22)] sm:px-6 sm:pb-6 sm:pt-7 lg:px-7 lg:pb-7 lg:pt-8">
      <div class="flex flex-col gap-5 2xl:flex-row 2xl:items-start 2xl:justify-between">
        <div class="min-w-0">
          <span class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-[11px] font-semibold tracking-[0.18em] text-blue-600">TEAM CENTER</span>
          <h2 class="mt-3 max-w-full pt-1 text-[1.95rem] font-black tracking-tight text-slate-900 sm:text-[2.2rem]">队伍管理中心</h2>
          <p class="mt-2 text-sm leading-6 text-slate-500">仅提供队伍查询与导出功能，管理员维护能力已迁移至后台管理页面。</p>
        </div>

        <div class="flex flex-col gap-2 sm:flex-row 2xl:justify-end">
          <el-button type="success" :loading="exporting" class="!h-11 !rounded-2xl !px-5" @click="handleExport">导出队伍 Excel</el-button>
        </div>
      </div>

      <el-alert
        v-if="noActiveEvent"
        class="mt-4"
        type="warning"
        :closable="false"
        title="没有正在进行的比赛，请先在赛事中心将某个比赛设为“正在比赛”后再进入队伍管理。"
      />

      <div class="mt-5 grid grid-cols-1 gap-3 md:grid-cols-4">
        <div class="rounded-[20px] border border-slate-200/80 bg-white/92 px-4 py-3.5">
          <div class="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">队伍总数</div>
          <div class="mt-1.5 text-[1.45rem] font-black text-slate-900">{{ tableData.length }}</div>
        </div>
        <div class="rounded-[20px] border border-slate-200/80 bg-white/92 px-4 py-3.5">
          <div class="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">报名通道</div>
          <div class="mt-1.5 text-[15px] font-semibold" :class="signupStatus.signup_open ? 'text-emerald-700' : 'text-slate-700'">{{ signupStatus.signup_open ? '开启' : '关闭' }}</div>
        </div>
        <div class="rounded-[20px] border border-slate-200/80 bg-white/92 px-4 py-3.5">
          <div class="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">选题通道</div>
          <div class="mt-1.5 text-[15px] font-semibold" :class="topicStatus.topic_open ? 'text-emerald-700' : 'text-slate-700'">{{ topicStatus.topic_open ? '开启' : '关闭' }}</div>
        </div>
        <div class="rounded-[20px] border border-slate-200/80 bg-white/92 px-4 py-3.5">
          <div class="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">信息修改通道</div>
          <div class="mt-1.5 text-[15px] font-semibold" :class="updateStatus.info_update_open ? 'text-emerald-700' : 'text-slate-700'">{{ updateStatus.info_update_open ? '开启' : '关闭' }}</div>
        </div>
      </div>

    </section>

    <section class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.18)] sm:p-6">
      <div class="mt-1 grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_280px_auto]">
        <el-input v-model="filters.keyword" placeholder="队伍名 / 队长姓名 / 学号" clearable @keyup.enter="fetchList" />
        <el-select v-model="filters.topic_id" placeholder="按题目筛选" clearable class="w-full">
          <el-option v-for="item in topics" :key="item.id" :label="formatTopicName(item.title)" :value="item.id" />
        </el-select>
        <div class="flex flex-col gap-2 sm:flex-row xl:justify-end">
          <el-button type="primary" class="!h-11 !rounded-2xl !px-6" @click="fetchList">查询</el-button>
          <el-button class="!h-11 !rounded-2xl !px-6" @click="resetFilters">重置</el-button>
        </div>
      </div>
    </section>

    <section class="flex min-h-0 flex-1 flex-col overflow-hidden rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] shadow-[0_16px_38px_-32px_rgba(15,23,42,0.2)]">
      <div class="flex flex-col gap-3 border-b border-slate-200/80 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <h3 class="text-lg font-semibold text-slate-800">队伍列表</h3>
        <div class="text-xs font-medium text-slate-400">支持按关键词和题目筛选</div>
      </div>
      <div class="flex h-full min-h-0 flex-col p-4 sm:p-5">
        <div class="min-h-0 flex-1 overflow-hidden rounded-[24px] border border-slate-200/80 bg-white">
          <el-table class="team-query-table" :data="displayTableData" border stripe height="100%" v-loading="loading" style="width: 100%" scrollbar-always-on>
            <el-table-column prop="signup_serial_no" label="序号" width="90" />
            <el-table-column prop="team_name" label="队伍名称" width="180" />
            <el-table-column label="队长信息" width="280">
              <template #default="{ row }">
                <div>{{ row.captain_name }} / {{ row.captain_student_id }}</div>
                <div class="text-xs text-slate-500">{{ row.captain_phone }}</div>
                <div class="text-xs text-slate-500">{{ row.captain_college || '-' }} / {{ row.captain_major_class || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column label="队员1" width="280">
              <template #default="{ row }">
                <div v-if="row.members?.[0]">{{ row.members[0].name }} / {{ row.members[0].student_id }}</div>
                <div v-if="row.members?.[0]" class="text-xs text-slate-500">{{ row.members[0].phone }}</div>
                <div v-if="row.members?.[0]" class="text-xs text-slate-500">{{ row.members[0].college || '-' }} / {{ row.members[0].major_class || '-' }}</div>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="队员2" width="280">
              <template #default="{ row }">
                <div v-if="row.members?.[1]">{{ row.members[1].name }} / {{ row.members[1].student_id }}</div>
                <div v-if="row.members?.[1]" class="text-xs text-slate-500">{{ row.members[1].phone }}</div>
                <div v-if="row.members?.[1]" class="text-xs text-slate-500">{{ row.members[1].college || '-' }} / {{ row.members[1].major_class || '-' }}</div>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="选题" width="220">
              <template #default="{ row }">
                {{ formatTopicName(row.topic_title) || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="删除状态" width="260">
              <template #default="{ row }">
                <div v-if="row.delete_requested" class="space-y-1">
                  <el-tag type="warning" size="small">待管理员确认删除</el-tag>
                  <div class="text-xs text-slate-500">申请时间：{{ row.delete_requested_at || '-' }}</div>
                  <div class="text-xs text-slate-500">理由：{{ row.delete_reason || '-' }}</div>
                </div>
                <el-tag v-else type="success" size="small">正常</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="一验" width="280">
              <template #default="{ row }">
                <div class="whitespace-pre-wrap text-xs leading-6 text-slate-600">
                  时间：{{ row.inspection?.first_inspection_time || '待安排' }}
                  {{ '\n' }}地点：{{ row.inspection?.first_inspection_location || '待安排' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="二验" width="280">
              <template #default="{ row }">
                <div class="whitespace-pre-wrap text-xs leading-6 text-slate-600">
                  时间：{{ row.inspection?.second_inspection_time || '待安排' }}
                  {{ '\n' }}地点：{{ row.inspection?.second_inspection_location || '待安排' }}
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { getCurrentCompetitionEvent } from '@/api/competition'
import {
  exportTeams,
  getSignupStatus,
  getTeams,
  getTeamUpdateStatus,
  getTopicStatus,
  getTopics
} from '@/api/team'

const route = useRoute()
const router = useRouter()
const activeModuleKey = computed(() => (route.query.module_key || '').toString())

const loading = ref(false)
const exporting = ref(false)
const noActiveEvent = ref(false)

const tableData = ref([])
const topics = ref([])

const signupStatus = reactive({ signup_open: false, signup_close_at: null })
const topicStatus = reactive({ topic_open: false, topic_close_at: null })
const updateStatus = reactive({ info_update_open: false, info_update_close_at: null })

const filters = reactive({
  keyword: '',
  topic_id: null
})

const displayTableData = computed(() => {
  const sorted = tableData.value
    .slice()
    .sort((a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime())

  return sorted.map((item, index) => ({
    ...item,
    signup_serial_no: index + 1,
  }))
})

const formatTopicName = (value) => {
  const raw = (value || '').toString().trim()
  if (!raw) return ''
  return raw.replace(/^(wireless|telecom|wireless_cup|telecom_cup)[-_\s]*/i, '')
}

const loadBaseData = async () => {
  if (!activeModuleKey.value) {
    topics.value = []
    Object.assign(signupStatus, { signup_open: false, signup_close_at: null })
    Object.assign(topicStatus, { topic_open: false, topic_close_at: null })
    Object.assign(updateStatus, { info_update_open: false, info_update_close_at: null })
    return
  }

  try {
    const [signupRes, topicRes, updateRes, topicsRes] = await Promise.all([
      getSignupStatus({ module_key: activeModuleKey.value }),
      getTopicStatus({ module_key: activeModuleKey.value }),
      getTeamUpdateStatus({ module_key: activeModuleKey.value }),
      getTopics({ only_active: false, module_key: activeModuleKey.value })
    ])

    Object.assign(signupStatus, signupRes.data || {})
    Object.assign(topicStatus, topicRes.data || {})
    Object.assign(updateStatus, updateRes.data || {})
    topics.value = Array.isArray(topicsRes.data) ? topicsRes.data : []

  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '初始化失败')
  }
}

const fetchList = async () => {
  if (!activeModuleKey.value) {
    tableData.value = []
    return
  }

  loading.value = true
  try {
    const params = {}
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.topic_id) params.topic_id = filters.topic_id
    params.module_key = activeModuleKey.value
    const res = await getTeams(params)
    tableData.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '获取队伍列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.topic_id = null
  fetchList()
}

const handleExport = async () => {
  if (!activeModuleKey.value) {
    ElMessage.warning('当前没有进行中的比赛，无法导出')
    return
  }
  exporting.value = true
  try {
    const params = {}
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.topic_id) params.topic_id = filters.topic_id
    params.module_key = activeModuleKey.value
    const blobData = await exportTeams(params)
    const blob = new Blob([blobData], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '队伍数据导出.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '导出失败')
  } finally {
    exporting.value = false
  }
}

const ensureCurrentEventContext = async () => {
  if (activeModuleKey.value) {
    noActiveEvent.value = false
    return
  }

  try {
    const res = await getCurrentCompetitionEvent()
    const event = res.data
    if (!event?.module_key) {
      noActiveEvent.value = true
      tableData.value = []
      topics.value = []
      Object.assign(signupStatus, { signup_open: false, signup_close_at: null })
      Object.assign(topicStatus, { topic_open: false, topic_close_at: null })
      Object.assign(updateStatus, { info_update_open: false, info_update_close_at: null })
      return
    }

    noActiveEvent.value = false
    await router.replace({
      path: route.path,
      query: {
        ...route.query,
        module_key: event.module_key,
        event_id: String(event.id),
        event_name: event.display_title || event.name,
        cup_type: event.cup_type,
      },
    })
  } catch (error) {
    noActiveEvent.value = true
    tableData.value = []
    topics.value = []
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '获取当前进行中比赛失败')
  }
}

onMounted(async () => {
  await ensureCurrentEventContext()
  if (noActiveEvent.value) return
  await loadBaseData()
  await fetchList()
})

watch(
  () => route.query.module_key,
  async () => {
    if (!route.query.module_key) {
      await ensureCurrentEventContext()
      if (noActiveEvent.value) return
    }
    await loadBaseData()
    await fetchList()
  }
)
</script>

<style scoped>
.team-query-table :deep(.el-scrollbar__bar.is-horizontal) {
  opacity: 1;
}
</style>
