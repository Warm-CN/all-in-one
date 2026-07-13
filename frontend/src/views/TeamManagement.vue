<template>
  <div class="team-management-page flex h-full min-h-0 flex-col gap-5 pb-2 sm:gap-6 sm:pb-3">
    <section class="rounded-2xl border border-slate-200 bg-white px-4 py-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.22)] sm:px-6 sm:py-6">
      <div class="flex min-w-0 flex-col gap-4 2xl:flex-row 2xl:items-start 2xl:justify-between">
        <div class="min-w-0">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600 shadow-sm">
              <el-icon :size="16"><Trophy /></el-icon>
            </div>
            <div>
              <span class="inline-flex max-w-full items-center rounded-full bg-blue-50 px-3 py-1 text-[11px] font-semibold tracking-[0.16em] text-blue-600">
                COMPETITION TEAMS
              </span>
              <h2 class="mt-3 text-[1.85rem] font-black tracking-tight text-slate-900 sm:text-[2.2rem]">竞赛队伍</h2>
            </div>
          </div>
          <p class="mt-2 text-sm leading-6 text-slate-500">选择比赛后查看报名队伍信息，并按当前筛选条件导出报名数据或导入验收信息。</p>
        </div>
      </div>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-[0_12px_28px_-30px_rgba(15,23,42,0.18)] sm:p-5">
      <div class="flex min-w-0 flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div class="min-w-0 xl:max-w-xl">
          <h3 class="text-lg font-bold text-slate-900">选择比赛</h3>
          <p class="mt-1 text-sm text-slate-500">选择后，下方整页展示对应比赛的报名队伍信息。</p>
        </div>
      </div>

      <div v-if="eventsLoading" class="mt-5 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <el-skeleton v-for="item in 4" :key="item" animated>
          <template #template>
            <div class="rounded-xl border border-slate-100 p-4">
              <el-skeleton-item variant="h3" class="!w-3/5" />
              <el-skeleton-item variant="text" class="!mt-3 !w-full" />
              <el-skeleton-item variant="text" class="!mt-2 !w-4/5" />
            </div>
          </template>
        </el-skeleton>
      </div>

      <div v-else-if="!events.length" class="mt-5 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
        暂无比赛
      </div>

      <div v-else class="mt-5 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <button
          v-for="item in events"
          :key="item.id"
          type="button"
          class="competition-card rounded-xl border p-4 text-left"
          :class="selectedEventId === item.id ? 'border-blue-300 bg-blue-50/70' : 'border-slate-200 bg-white hover:border-blue-200 hover:bg-blue-50/30'"
          @click="selectEvent(item)"
        >
          <span class="flex flex-wrap items-center gap-2">
            <el-tag :type="cupTagType(item.cup_type)" effect="plain">{{ cupLabel(item.cup_type) }}</el-tag>
            <el-tag :type="item.is_current ? 'success' : 'info'" effect="light">
              {{ item.is_current ? '进行中' : '未进行' }}
            </el-tag>
          </span>
          <span class="mt-3 block text-base font-bold leading-snug text-slate-900 break-words">{{ item.name }}</span>
          <span class="mt-3 grid grid-cols-3 gap-2 text-center">
            <span class="rounded-lg bg-slate-50 px-2 py-2">
              <span class="block text-[11px] font-semibold text-slate-500">队伍</span>
              <span class="mt-1 block text-sm font-black text-slate-900">{{ item.team_count || 0 }}</span>
            </span>
            <span class="rounded-lg bg-slate-50 px-2 py-2">
              <span class="block text-[11px] font-semibold text-slate-500">人数</span>
              <span class="mt-1 block text-sm font-black text-slate-900">{{ item.total_people || 0 }}</span>
            </span>
            <span class="rounded-lg bg-slate-50 px-2 py-2">
              <span class="block text-[11px] font-semibold text-slate-500">选题</span>
              <span class="mt-1 block text-sm font-black text-slate-900">{{ item.topic_count || 0 }}</span>
            </span>
          </span>
        </button>
      </div>
    </section>

    <section v-if="selectedEvent" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-[0_12px_28px_-30px_rgba(15,23,42,0.18)] sm:p-5">
      <div class="flex min-w-0 flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <el-tag :type="cupTagType(selectedEvent.cup_type)" effect="plain">{{ cupLabel(selectedEvent.cup_type) }}</el-tag>
            <el-tag :type="selectedEvent.is_current ? 'success' : 'info'" effect="light">
              {{ selectedEvent.is_current ? '进行中' : '未进行' }}
            </el-tag>
          </div>
          <h3 class="mt-3 text-2xl font-black leading-snug text-slate-900 break-words">{{ selectedEvent.name }}</h3>
        </div>

        <div class="grid w-full grid-cols-1 gap-2 sm:grid-cols-2 lg:w-auto lg:min-w-[360px]">
          <div v-if="userStore.isAdmin" class="flex items-center gap-1">
            <el-popover placement="bottom" :width="300" trigger="hover">
              <template #reference>
                <el-icon class="cursor-help text-slate-300 hover:text-slate-500"><QuestionFilled /></el-icon>
              </template>
              <div class="text-xs leading-5 text-slate-600">
                <p class="font-bold text-slate-700">导出/导入格式说明</p>
                <p class="mt-1 font-semibold text-slate-600">导出</p>
                <p>包含全部队伍信息 + 验收安排 + 填写示例</p>
                <p class="mt-1 font-semibold text-slate-600">导入（.xlsx）</p>
                <p>• 队伍ID / 队长学号 / 队伍名称（任选其一匹配）</p>
                <p>• 一验时间、一验地点、一验备注</p>
                <p>• 二验时间、二验地点、二验备注</p>
                <p class="mt-1 text-slate-400">留空字段不会覆盖已有值</p>
                <el-button link type="primary" size="small" class="mt-2" @click="handleDownloadTemplate">下载导入模板</el-button>
              </div>
            </el-popover>
            <el-upload
              :show-file-list="false"
              accept=".xlsx"
              :http-request="handleInspectionImport"
              class="w-full"
              :disabled="importing"
            >
              <el-button type="primary" plain :icon="Upload" :loading="importing" class="w-full">
                导入验收信息
              </el-button>
            </el-upload>
          </div>
          <div class="flex items-center gap-1">
            <el-button type="success" :icon="Download" :loading="exporting" @click="handleExport" class="w-full">
              导出报名信息
            </el-button>
          </div>
        </div>
      </div>

      <div class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
          <div class="text-xs font-semibold text-slate-500">报名队伍</div>
          <div class="mt-1 text-xl font-black text-slate-900">{{ tableData.length }}</div>
        </div>
        <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
          <div class="text-xs font-semibold text-slate-500">报名人数</div>
          <div class="mt-1 text-xl font-black text-slate-900">{{ selectedEvent.total_people || 0 }}</div>
        </div>
        <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
          <div class="text-xs font-semibold text-slate-500">选题数量</div>
          <div class="mt-1 text-xl font-black text-slate-900">{{ topics.length }}</div>
        </div>
        <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
          <div class="text-xs font-semibold text-slate-500">报名时间</div>
          <div class="mt-1 text-xs font-bold leading-5 text-slate-900">{{ formatRange(selectedEvent.signup_start_at, selectedEvent.signup_end_at) }}</div>
        </div>
      </div>
    </section>

    <el-alert
      v-else
      type="info"
      :closable="false"
      title="请先选择一个比赛"
    />

    <section v-if="selectedEvent" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-[0_12px_28px_-30px_rgba(15,23,42,0.18)] sm:p-5">
      <div class="mb-4 flex min-w-0 flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
        <div class="min-w-0">
          <h3 class="text-lg font-bold text-slate-900">筛选报名队伍</h3>
          <p class="mt-1 text-sm text-slate-500">当前筛选会同步作用于 Excel 导出。</p>
        </div>
      </div>
      <div class="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.2fr)_280px_220px_auto]">
        <el-input v-model="filters.keyword" placeholder="队伍名 / 队长姓名 / 学号" clearable @keyup.enter="fetchList" />
        <el-select v-model="filters.topic_id" placeholder="按题目筛选" clearable class="w-full">
          <el-option v-for="item in topics" :key="item.id" :label="topicLabel(item)" :value="item.id" />
        </el-select>
        <el-select v-model="filters.delete_status" placeholder="删除申请状态" clearable class="w-full">
          <el-option label="正常队伍" value="normal" />
          <el-option label="待确认删除" value="pending" />
        </el-select>
        <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:flex xl:justify-end">
          <el-button type="primary" :icon="Search" @click="fetchList">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </div>
      </div>
    </section>

    <section class="flex min-h-[560px] flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_16px_38px_-32px_rgba(15,23,42,0.2)]">
      <div class="flex flex-col gap-3 border-b border-slate-200 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5">
        <h3 class="text-lg font-bold text-slate-900">报名队伍信息</h3>
        <div class="text-xs font-medium text-slate-400">{{ selectedEvent ? `已载入 ${tableData.length} 支队伍` : '未选择比赛' }}</div>
      </div>
      <div v-if="!selectedEvent" class="flex min-h-[360px] items-center justify-center px-4 py-10 text-center text-sm text-slate-500">
        选择比赛后显示该比赛的报名队伍
      </div>
      <div v-else class="flex h-full min-h-0 flex-col p-4 sm:p-5">
        <div class="min-h-0 flex-1 overflow-auto rounded-xl border border-slate-200 bg-white">
          <el-table :data="tableData" border stripe height="100%" v-loading="loading" style="min-width: 1850px">
            <el-table-column prop="team_name" label="队伍名称" min-width="160" />
            <el-table-column prop="topic_title" label="选题" min-width="200">
              <template #default="{ row }">
                <span v-if="row.topic_title" class="text-slate-700">{{ row.topic_title }}</span>
                <span v-else class="text-slate-400">未选题</span>
              </template>
            </el-table-column>
            <el-table-column label="队长信息" min-width="230">
              <template #default="{ row }">
                <div class="font-semibold text-slate-800">{{ row.captain_name }} / {{ row.captain_student_id }}</div>
                <div class="text-xs text-slate-500">{{ row.captain_phone }}</div>
                <div class="text-xs text-slate-500">{{ row.captain_college || '-' }} / {{ row.captain_major_class || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column label="队员1" min-width="220">
              <template #default="{ row }">
                <div v-if="row.members?.[0]">{{ row.members[0].name }} / {{ row.members[0].student_id }}</div>
                <div v-if="row.members?.[0]" class="text-xs text-slate-500">{{ row.members[0].phone }}</div>
                <div v-if="row.members?.[0]" class="text-xs text-slate-500">{{ row.members[0].college || '-' }} / {{ row.members[0].major_class || '-' }}</div>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="队员2" min-width="220">
              <template #default="{ row }">
                <div v-if="row.members?.[1]">{{ row.members[1].name }} / {{ row.members[1].student_id }}</div>
                <div v-if="row.members?.[1]" class="text-xs text-slate-500">{{ row.members[1].phone }}</div>
                <div v-if="row.members?.[1]" class="text-xs text-slate-500">{{ row.members[1].college || '-' }} / {{ row.members[1].major_class || '-' }}</div>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" min-width="190">
              <template #default="{ row }">
                <div v-if="row.delete_requested" class="space-y-1">
                  <el-tag type="warning" size="small">待确认删除</el-tag>
                  <div class="text-xs text-slate-500">申请时间：{{ formatDate(row.delete_requested_at, '-') }}</div>
                </div>
                <el-tag v-else type="success" size="small">正常</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="一验安排" min-width="250">
              <template #default="{ row }">
                <div class="whitespace-pre-wrap text-xs leading-6 text-slate-600">
                  时间：{{ formatDate(row.inspection?.first_inspection_time, '待安排') }}
                  {{ '\n' }}地点：{{ row.inspection?.first_inspection_location || '待安排' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="二验安排" min-width="250">
              <template #default="{ row }">
                <div class="whitespace-pre-wrap text-xs leading-6 text-slate-600">
                  时间：{{ formatDate(row.inspection?.second_inspection_time, '待安排') }}
                  {{ '\n' }}地点：{{ row.inspection?.second_inspection_location || '待安排' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="报名时间" min-width="160">
              <template #default="{ row }">{{ formatDate(row.created_at, '-') }}</template>
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
import { useUserStore } from '@/store/user'
import { Download, Search, Trophy, Upload, QuestionFilled } from '@element-plus/icons-vue'
import { getCompetitionEvents } from '@/api/competition'
import {
  exportTeams,
  getSignupStatus,
  getTeams,
  getTopics,
  importTeamInspections,
  downloadInspectionTemplate,
} from '@/api/team'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const eventsLoading = ref(false)
const loading = ref(false)
const exporting = ref(false)
const importing = ref(false)

const events = ref([])
const selectedEventId = ref(null)
const tableData = ref([])
const topics = ref([])

const selectedEvent = computed(() => events.value.find((item) => item.id === selectedEventId.value) || null)
const activeModuleKey = computed(() => selectedEvent.value?.module_key || '')

const signupStatus = reactive({ signup_open: false, signup_close_at: null })

const filters = reactive({
  keyword: '',
  topic_id: null,
  delete_status: ''
})

const dateTimeFormatter = new Intl.DateTimeFormat('zh-CN', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail
  return error?.response?.data?.msg || (typeof detail === 'string' ? detail : '') || error?.message || fallback
}

const cupLabel = (type) => (type === 'telecom' ? '电信杯' : '无线杯')
const cupTagType = (type) => (type === 'telecom' ? 'warning' : 'primary')
const topicLabel = (item) => `${item.code || item.id} - ${item.title}`

const formatDate = (value, fallback = '未设置') => {
  if (!value) return fallback
  const date = new Date(value)
  if (!Number.isFinite(date.getTime())) return String(value)
  return dateTimeFormatter.format(date)
}

const formatRange = (start, end) => `${formatDate(start)} 至 ${formatDate(end)}`

const toSortableTime = (value) => {
  const time = new Date(value || 0).getTime()
  return Number.isFinite(time) ? time : 0
}

const sortEvents = (items) => {
  return [...items].sort((left, right) => {
    if (!!right.is_current !== !!left.is_current) return right.is_current ? 1 : -1
    return toSortableTime(right.created_at) - toSortableTime(left.created_at)
  })
}

const buildListParams = () => {
  const params = {
    module_key: activeModuleKey.value
  }
  if (filters.keyword) params.keyword = filters.keyword
  if (filters.topic_id) params.topic_id = filters.topic_id
  if (filters.delete_status === 'pending') params.delete_requested = true
  if (filters.delete_status === 'normal') params.delete_requested = false
  return params
}

const resetContextData = () => {
  tableData.value = []
  topics.value = []
  Object.assign(signupStatus, { signup_open: false, signup_close_at: null })
}

const fetchEvents = async () => {
  eventsLoading.value = true
  try {
    const [wirelessRes, telecomRes] = await Promise.all([
      getCompetitionEvents('wireless'),
      getCompetitionEvents('telecom')
    ])
    const wirelessEvents = Array.isArray(wirelessRes.data) ? wirelessRes.data : []
    const telecomEvents = Array.isArray(telecomRes.data) ? telecomRes.data : []
    events.value = sortEvents([...wirelessEvents, ...telecomEvents])

    const routeEventId = Number(route.query.event_id)
    const preferred = events.value.find((item) => item.id === routeEventId)
      || events.value.find((item) => item.is_current)
      || events.value[0]
      || null

    if (preferred) {
      await selectEvent(preferred, { resetTopicFilter: false })
    } else {
      selectedEventId.value = null
      resetContextData()
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '获取比赛列表失败'))
  } finally {
    eventsLoading.value = false
  }
}

const selectEvent = async (event, options = {}) => {
  if (!event?.id) return
  const { resetTopicFilter = true, syncRoute = true } = options

  selectedEventId.value = event.id
  if (resetTopicFilter) filters.topic_id = null

  if (syncRoute) {
    await router.replace({
      path: '/teams-center',
      query: {
        event_id: String(event.id),
        module_key: event.module_key,
        event_name: event.display_title || event.portal_title || event.name,
        cup_type: event.cup_type,
      }
    })
  }

  await loadBaseData()
  await fetchList()
}

const loadBaseData = async () => {
  if (!activeModuleKey.value) {
    resetContextData()
    return
  }

  try {
    const [signupRes, topicsRes] = await Promise.all([
      getSignupStatus({ module_key: activeModuleKey.value }),
      getTopics({ only_active: false, module_key: activeModuleKey.value })
    ])

    Object.assign(signupStatus, signupRes.data || {})
    topics.value = Array.isArray(topicsRes.data) ? topicsRes.data : []
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '初始化比赛信息失败'))
  }
}

const fetchList = async () => {
  if (!activeModuleKey.value) {
    tableData.value = []
    return
  }

  loading.value = true
  try {
    const res = await getTeams(buildListParams())
    tableData.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '获取队伍列表失败'))
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.topic_id = null
  filters.delete_status = ''
  fetchList()
}

const handleExport = async () => {
  if (!selectedEvent.value || !activeModuleKey.value) {
    ElMessage.warning('请先选择比赛')
    return
  }
  exporting.value = true
  try {
    const blobData = await exportTeams(buildListParams())
    const blob = new Blob([blobData], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const safeName = (selectedEvent.value.name || '竞赛队伍').replace(/[\\/:*?"<>|]/g, '_')
    link.href = url
    link.download = `${safeName}_报名信息.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '导出失败'))
  } finally {
    exporting.value = false
  }
}

const handleDownloadTemplate = async () => {
  try {
    const blobData = await downloadInspectionTemplate()
    const blob = new Blob([blobData], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '验收信息导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '下载失败'))
  }
}

const handleInspectionImport = async (uploadRequest) => {
  if (!userStore.isAdmin || !selectedEvent.value || !activeModuleKey.value) return
  const file = uploadRequest?.file
  if (!file) {
    ElMessage.warning('请选择 xlsx 文件')
    return
  }

  importing.value = true
  try {
    const res = await importTeamInspections(file, activeModuleKey.value)
    if (typeof uploadRequest?.onSuccess === 'function') uploadRequest.onSuccess(res)
    ElMessage.success(res.msg || '导入成功')
    await fetchList()
  } catch (error) {
    if (typeof uploadRequest?.onError === 'function') uploadRequest.onError(error)
    ElMessage.error(getErrorMessage(error, '导入失败'))
  } finally {
    importing.value = false
  }
}

onMounted(fetchEvents)

watch(
  () => route.query.event_id,
  async (value) => {
    if (!events.value.length) return
    const eventId = Number(value)
    if (!eventId || eventId === selectedEventId.value) return
    const event = events.value.find((item) => item.id === eventId)
    if (event) await selectEvent(event, { resetTopicFilter: true, syncRoute: false })
  }
)
</script>

<style scoped>
.team-management-page {
  min-height: 100%;
  overflow-x: hidden;
}

.competition-card {
  min-width: 0;
  transition: border-color 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease;
}

.competition-card:hover {
  box-shadow: 0 12px 26px -28px rgba(15, 23, 42, 0.45);
}

.competition-card:focus-visible {
  outline: 2px solid #93c5fd;
  outline-offset: 2px;
}

.team-management-page :deep(.el-upload) {
  width: 100%;
}

.team-management-page :deep(.el-form-item) {
  min-width: 0;
}
</style>
