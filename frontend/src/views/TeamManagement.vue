<template>
  <div class="flex h-full min-h-0 flex-col gap-5 pb-2 sm:gap-6 sm:pb-3">
    <section class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] px-5 pb-5 pt-6 shadow-[0_14px_34px_-28px_rgba(15,23,42,0.22)] sm:px-6 sm:pb-6 sm:pt-7 lg:px-7 lg:pb-7 lg:pt-8">
      <div class="flex flex-col gap-5 2xl:flex-row 2xl:items-start 2xl:justify-between">
        <div class="min-w-0">
          <span class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-[11px] font-semibold tracking-[0.18em] text-blue-600">TEAM CENTER</span>
          <h2 class="mt-3 max-w-full pt-1 text-[1.95rem] font-black tracking-tight text-slate-900 sm:text-[2.2rem]">队伍管理中心</h2>
          <p class="mt-2 text-sm leading-6 text-slate-500">成员可查询与导出，管理员可维护通道状态与验收安排。</p>
          <p v-if="activeEventName || eventNameForm.name" class="mt-1 text-xs font-semibold text-blue-600">当前操控比赛：{{ eventNameForm.name || activeEventName }}</p>
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

      <div v-if="userStore.isAdmin && activeEventId" class="mt-4 rounded-2xl border border-slate-200/80 bg-white/90 p-4">
        <div class="mb-2 text-sm font-semibold text-slate-700">修改比赛名称</div>
        <div class="flex flex-col gap-3 sm:flex-row">
          <el-input v-model="eventNameForm.name" placeholder="请输入新的比赛名称" clearable class="sm:flex-1" />
          <el-button type="primary" class="!h-11 !rounded-2xl !px-6" :loading="savingEventName" @click="saveEventName">保存比赛名称</el-button>
        </div>
      </div>
    </section>

    <section v-if="userStore.isAdmin" class="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,#f8fbff_0%,#f8fafc_100%)] px-5 pb-7 pt-5 shadow-[0_12px_34px_-28px_rgba(15,23,42,0.2)] sm:px-6 sm:pb-8 sm:pt-6">
      <h3 class="text-lg font-semibold text-slate-800">通道总控（管理员）</h3>
      <div class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <el-switch v-model="configForm.signup_open" active-text="报名开启" inactive-text="报名关闭" />
        <el-switch v-model="configForm.topic_open" active-text="选题开启" inactive-text="选题关闭" />
        <el-switch v-model="configForm.info_update_open" active-text="信息修改开启" inactive-text="信息修改关闭" />
      </div>
      <div class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <el-date-picker v-model="configForm.signup_close_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="报名截止时间" />
        <el-date-picker v-model="configForm.topic_close_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选题截止时间" />
        <el-date-picker v-model="configForm.info_update_close_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="信息修改截止时间" />
      </div>
      <div class="mt-6 flex justify-end border-t border-slate-200/70 pt-4">
        <el-button type="primary" class="!h-11 !rounded-2xl !px-6" :loading="savingConfig" @click="saveConfig">保存通道配置</el-button>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.18)] sm:p-6">
      <div class="mt-1 grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_280px_auto]">
        <el-input v-model="filters.keyword" placeholder="队伍名 / 队长姓名 / 学号" clearable @keyup.enter="fetchList" />
        <el-select v-model="filters.topic_id" placeholder="按题目筛选" clearable class="w-full">
          <el-option v-for="item in topics" :key="item.id" :label="`${item.code} - ${item.title}`" :value="item.id" />
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
        <div class="text-xs font-medium text-slate-400">仅管理员可维护验收安排</div>
      </div>
      <div class="flex h-full min-h-0 flex-col p-4 sm:p-5">
        <div class="min-h-0 flex-1 overflow-auto rounded-[24px] border border-slate-200/80 bg-white">
          <el-table :data="tableData" border stripe height="100%" v-loading="loading" style="min-width: 1700px">
            <el-table-column prop="team_name" label="队伍名称" min-width="160" />
            <el-table-column label="队长信息" min-width="220">
              <template #default="{ row }">
                <div>{{ row.captain_name }} / {{ row.captain_student_id }}</div>
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
            <el-table-column prop="topic_title" label="选题" min-width="180" />
            <el-table-column label="删除状态" min-width="220">
              <template #default="{ row }">
                <div v-if="row.delete_requested" class="space-y-1">
                  <el-tag type="warning" size="small">待管理员确认删除</el-tag>
                  <div class="text-xs text-slate-500">申请时间：{{ row.delete_requested_at || '-' }}</div>
                  <div class="text-xs text-slate-500">理由：{{ row.delete_reason || '-' }}</div>
                </div>
                <el-tag v-else type="success" size="small">正常</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="一验" min-width="260">
              <template #default="{ row }">
                <div class="whitespace-pre-wrap text-xs leading-6 text-slate-600">
                  时间：{{ row.inspection?.first_inspection_time || '待安排' }}
                  {{ '\n' }}地点：{{ row.inspection?.first_inspection_location || '待安排' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="二验" min-width="260">
              <template #default="{ row }">
                <div class="whitespace-pre-wrap text-xs leading-6 text-slate-600">
                  时间：{{ row.inspection?.second_inspection_time || '待安排' }}
                  {{ '\n' }}地点：{{ row.inspection?.second_inspection_location || '待安排' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column v-if="userStore.isAdmin" label="操作" min-width="140" fixed="right">
              <template #default="{ row }">
                <div class="flex flex-wrap gap-2">
                  <el-button link type="primary" @click="openTopicDialog(row)">修改选题</el-button>
                  <el-button link type="primary" @click="openInspectionDialog(row)">维护验收</el-button>
                  <el-popconfirm
                    v-if="row.delete_requested"
                    title="确认彻底删除该队伍？删除后不可恢复"
                    confirm-button-text="确认删除"
                    cancel-button-text="取消"
                    @confirm="handleConfirmDelete(row)"
                  >
                    <template #reference>
                      <el-button link type="danger">确认删除</el-button>
                    </template>
                  </el-popconfirm>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </section>

    <el-dialog v-model="inspectionVisible" title="维护验收安排" width="760px" destroy-on-close>
      <el-form :model="inspectionForm" label-position="top" size="large">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <el-form-item label="第一次验收时间"><el-date-picker v-model="inspectionForm.first_inspection_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
          <el-form-item label="第一次验收地点"><el-input v-model="inspectionForm.first_inspection_location" /></el-form-item>
          <el-form-item label="第一次验收负责人"><el-input v-model="inspectionForm.first_inspector" /></el-form-item>
          <el-form-item label="第一次验收备注"><el-input v-model="inspectionForm.first_notes" /></el-form-item>
          <el-form-item label="第二次验收时间"><el-date-picker v-model="inspectionForm.second_inspection_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
          <el-form-item label="第二次验收地点"><el-input v-model="inspectionForm.second_inspection_location" /></el-form-item>
          <el-form-item label="第二次验收负责人"><el-input v-model="inspectionForm.second_inspector" /></el-form-item>
          <el-form-item label="第二次验收备注"><el-input v-model="inspectionForm.second_notes" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="inspectionVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingInspection" @click="submitInspection">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="topicVisible" title="修改队伍选题" width="560px" destroy-on-close>
      <el-form :model="topicForm" label-position="top" size="large">
        <el-form-item label="新题目">
          <el-select v-model="topicForm.topic_id" placeholder="请选择题目" class="w-full">
            <el-option v-for="item in topics" :key="item.id" :label="`${item.code} - ${item.title}`" :value="item.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="topicVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingInspection" @click="submitTopic">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { getCurrentCompetitionEvent, updateCompetitionEventName } from '@/api/competition'
import {
  batchUpdateTeamTopic,
  confirmDeleteTeam,
  exportTeams,
  getSignupStatus,
  getTeams,
  getTeamUpdateStatus,
  getTopicStatus,
  getTopics,
  updateTeamChannelConfig,
  updateTeamInspection
} from '@/api/team'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const activeModuleKey = computed(() => (route.query.module_key || '').toString())
const activeEventName = computed(() => (route.query.event_name || '').toString())
const activeEventId = computed(() => {
  const raw = Number(route.query.event_id)
  return Number.isInteger(raw) && raw > 0 ? raw : null
})

const loading = ref(false)
const exporting = ref(false)
const savingConfig = ref(false)
const savingInspection = ref(false)
const savingEventName = ref(false)
const noActiveEvent = ref(false)

const tableData = ref([])
const topics = ref([])
const eventNameForm = reactive({
  name: ''
})

const signupStatus = reactive({ signup_open: false, signup_close_at: null })
const topicStatus = reactive({ topic_open: false, topic_close_at: null })
const updateStatus = reactive({ info_update_open: false, info_update_close_at: null })

const configForm = reactive({
  signup_open: false,
  topic_open: false,
  info_update_open: false,
  signup_close_at: null,
  topic_close_at: null,
  info_update_close_at: null
})

const filters = reactive({
  keyword: '',
  topic_id: null
})

const inspectionVisible = ref(false)
const editingTeamId = ref(null)
const topicVisible = ref(false)
const topicForm = reactive({
  team_id: null,
  topic_id: null
})
const inspectionForm = reactive({
  first_inspection_time: null,
  first_inspection_location: '',
  first_inspector: '',
  first_notes: '',
  second_inspection_time: null,
  second_inspection_location: '',
  second_inspector: '',
  second_notes: ''
})

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

    configForm.signup_open = !!signupStatus.signup_open
    configForm.topic_open = !!topicStatus.topic_open
    configForm.info_update_open = !!updateStatus.info_update_open
    configForm.signup_close_at = signupStatus.signup_close_at
    configForm.topic_close_at = topicStatus.topic_close_at
    configForm.info_update_close_at = updateStatus.info_update_close_at
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

const saveConfig = async () => {
  if (!userStore.isAdmin) return
  if (!activeModuleKey.value) {
    ElMessage.warning('当前没有进行中的比赛，无法保存通道配置')
    return
  }
  savingConfig.value = true
  try {
    await updateTeamChannelConfig({
      module_key: activeModuleKey.value,
      signup_open: configForm.signup_open,
      topic_open: configForm.topic_open,
      info_update_open: configForm.info_update_open,
      signup_close_at: configForm.signup_close_at,
      topic_close_at: configForm.topic_close_at,
      info_update_close_at: configForm.info_update_close_at
    })
    ElMessage.success('通道配置已保存')
    await loadBaseData()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '保存失败')
  } finally {
    savingConfig.value = false
  }
}

const saveEventName = async () => {
  if (!userStore.isAdmin) return
  if (!activeEventId.value) {
    ElMessage.warning('未找到比赛ID，请从赛事中心进入本页面后再修改名称')
    return
  }

  const name = (eventNameForm.name || '').trim()
  if (!name) {
    ElMessage.warning('请输入比赛名称')
    return
  }

  savingEventName.value = true
  try {
    await updateCompetitionEventName(activeEventId.value, name)
    ElMessage.success('比赛名称已更新')
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '更新失败')
  } finally {
    savingEventName.value = false
  }
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

const openInspectionDialog = (row) => {
  editingTeamId.value = row.id
  inspectionForm.first_inspection_time = row.inspection?.first_inspection_time || null
  inspectionForm.first_inspection_location = row.inspection?.first_inspection_location || ''
  inspectionForm.first_inspector = row.inspection?.first_inspector || ''
  inspectionForm.first_notes = row.inspection?.first_notes || ''
  inspectionForm.second_inspection_time = row.inspection?.second_inspection_time || null
  inspectionForm.second_inspection_location = row.inspection?.second_inspection_location || ''
  inspectionForm.second_inspector = row.inspection?.second_inspector || ''
  inspectionForm.second_notes = row.inspection?.second_notes || ''
  inspectionVisible.value = true
}

const openTopicDialog = (row) => {
  topicForm.team_id = row.id
  topicForm.topic_id = row.topic_id || null
  topicVisible.value = true
}

const submitTopic = async () => {
  if (!topicForm.team_id || !topicForm.topic_id) {
    ElMessage.warning('请选择要设置的题目')
    return
  }

  savingInspection.value = true
  try {
    await batchUpdateTeamTopic({
      team_ids: [topicForm.team_id],
      topic_id: topicForm.topic_id
    })
    ElMessage.success('选题修改成功')
    topicVisible.value = false
    await fetchList()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '修改失败')
  } finally {
    savingInspection.value = false
  }
}

const submitInspection = async () => {
  if (!editingTeamId.value || !userStore.isAdmin) return
  savingInspection.value = true
  try {
    await updateTeamInspection(editingTeamId.value, { ...inspectionForm })
    ElMessage.success('验收安排已保存')
    inspectionVisible.value = false
    await fetchList()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '保存失败')
  } finally {
    savingInspection.value = false
  }
}

const handleConfirmDelete = async (row) => {
  if (!userStore.isAdmin || !row?.id) return
  savingInspection.value = true
  try {
    await confirmDeleteTeam(row.id)
    ElMessage.success('已彻底删除该队伍')
    await fetchList()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '删除失败')
  } finally {
    savingInspection.value = false
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

watch(
  () => route.query.event_name,
  () => {
    eventNameForm.name = activeEventName.value
  },
  { immediate: true }
)
</script>
