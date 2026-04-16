<template>
  <div class="flex h-full min-h-0 flex-col gap-5 pb-2 sm:gap-6 sm:pb-3">
    <section class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] px-5 pb-5 pt-6 shadow-[0_14px_34px_-28px_rgba(15,23,42,0.22)] sm:px-6 sm:pb-6 sm:pt-7 lg:px-7 lg:pb-7 lg:pt-8">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div class="min-w-0">
          <span class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-[11px] font-semibold tracking-[0.18em] text-blue-600">CONTEST ADMIN</span>
          <h2 class="mt-3 max-w-full pt-1 text-[1.95rem] font-black tracking-tight text-slate-900 sm:text-[2.2rem]">竞赛后台管理</h2>
          <p class="mt-2 text-sm leading-6 text-slate-500">统一处理通道、选题、队伍删除确认和验收安排。</p>
          <p v-if="activeEventName || eventNameForm.name" class="mt-1 text-xs font-semibold text-blue-600">当前比赛：{{ eventNameForm.name || activeEventName }}</p>
        </div>

        <div class="flex flex-col gap-2 sm:flex-row lg:justify-end">
          <el-button type="primary" class="!h-11 !rounded-2xl !px-5" @click="openBulkInspectionDialog">批量验收维护</el-button>
          <el-button class="!h-11 !rounded-2xl !px-5" @click="goBack">返回后台管理</el-button>
          <el-button type="success" :loading="exporting" class="!h-11 !rounded-2xl !px-5" @click="handleExport">导出队伍 Excel</el-button>
        </div>
      </div>

      <el-alert
        v-if="noActiveEvent"
        class="mt-4"
        type="warning"
        :closable="false"
        title="没在比赛中"
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

      <div v-if="activeEventId" class="mt-4 rounded-2xl border border-slate-200/80 bg-white/90 p-4">
        <div class="mb-2 text-sm font-semibold text-slate-700">修改比赛名称</div>
        <div class="flex flex-col gap-3 sm:flex-row">
          <el-input v-model="eventNameForm.name" placeholder="请输入新的比赛名称" clearable class="sm:flex-1" />
          <el-button type="primary" class="!h-11 !rounded-2xl !px-6" :loading="savingEventName" @click="saveEventName">保存比赛名称</el-button>
        </div>
      </div>
    </section>

    <section v-if="!noActiveEvent" class="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,#f8fbff_0%,#f8fafc_100%)] px-5 pb-7 pt-5 shadow-[0_12px_34px_-28px_rgba(15,23,42,0.2)] sm:px-6 sm:pb-8 sm:pt-6">
      <h3 class="text-lg font-semibold text-slate-800">通道总控</h3>
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

    <section v-if="!noActiveEvent" class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.18)] sm:p-6">
      <div class="mt-1 grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_280px_auto]">
        <el-input v-model="filters.keyword" placeholder="队伍名 / 队长姓名 / 学号" clearable @keyup.enter="fetchList" />
        <el-select v-model="filters.topic_id" placeholder="按题目筛选" clearable class="w-full">
          <el-option v-for="item in topics" :key="item.id" :label="formatTopicName(item.title)" :value="item.id" />
        </el-select>
        <div class="flex flex-col gap-2 sm:flex-row xl:justify-end">
          <el-button type="primary" class="!h-11 !rounded-2xl !px-6" @click="fetchList">查询</el-button>
          <el-button class="!h-11 !rounded-2xl !px-6" @click="resetFilters">重置</el-button>
          <el-button type="primary" plain class="!h-11 !rounded-2xl !px-6" @click="openBulkInspectionDialog">批量验收维护</el-button>
        </div>
      </div>
    </section>

    <section v-if="!noActiveEvent" class="flex min-h-0 flex-1 flex-col overflow-hidden rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] shadow-[0_16px_38px_-32px_rgba(15,23,42,0.2)]">
      <div class="flex flex-col gap-3 border-b border-slate-200/80 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <h3 class="text-lg font-semibold text-slate-800">队伍列表</h3>
        <div class="text-xs font-medium text-slate-400">支持修改选题、验收安排与删除确认</div>
      </div>
      <div class="flex h-full min-h-0 flex-col p-4 sm:p-5">
        <div class="min-h-0 flex-1 overflow-hidden rounded-[24px] border border-slate-200/80 bg-white">
          <el-table class="contest-team-table" :data="displayTableData" border stripe height="100%" v-loading="loading" style="width: 100%" scrollbar-always-on>
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
            <el-table-column label="操作" width="240" fixed="right">
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
            <el-option v-for="item in topics" :key="item.id" :label="formatTopicName(item.title)" :value="item.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="topicVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingTopic" @click="submitTopic">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="bulkInspectionVisible" title="批量验收维护" width="980px" destroy-on-close>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <el-form-item label="先选择选题">
            <el-select v-model="bulkForm.topic_id" placeholder="请选择选题" class="w-full" @change="onBulkTopicChange">
              <el-option v-for="item in topics" :key="item.id" :label="formatTopicName(item.title)" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="从第几号">
            <el-input-number v-model="bulkForm.start_no" :min="1" :max="bulkMaxSerial || 1" class="w-full" />
          </el-form-item>
          <el-form-item label="到第几号">
            <el-input-number v-model="bulkForm.end_no" :min="1" :max="bulkMaxSerial || 1" class="w-full" />
          </el-form-item>
        </div>

        <div class="mt-2 text-xs text-slate-500">
          该选题下共 {{ bulkMaxSerial }} 支队伍，序号为临时重排（按队伍ID升序从 1 开始）。
          当前命中 {{ bulkTargetTeams.length }} 支。
        </div>
      </div>

      <el-form :model="bulkForm" label-position="top" size="large" class="mt-4">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <el-form-item label="第一次验收时间"><el-date-picker v-model="bulkForm.first_inspection_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
          <el-form-item label="第一次验收地点"><el-input v-model="bulkForm.first_inspection_location" /></el-form-item>
          <el-form-item label="第一次验收负责人"><el-input v-model="bulkForm.first_inspector" /></el-form-item>
          <el-form-item label="第一次验收备注"><el-input v-model="bulkForm.first_notes" /></el-form-item>
          <el-form-item label="第二次验收时间"><el-date-picker v-model="bulkForm.second_inspection_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
          <el-form-item label="第二次验收地点"><el-input v-model="bulkForm.second_inspection_location" /></el-form-item>
          <el-form-item label="第二次验收负责人"><el-input v-model="bulkForm.second_inspector" /></el-form-item>
          <el-form-item label="第二次验收备注"><el-input v-model="bulkForm.second_notes" /></el-form-item>
        </div>
      </el-form>

      <div class="mt-2 overflow-auto rounded-xl border border-slate-200">
        <el-table :data="bulkTargetTeams" size="small" style="width: 100%; min-width: 680px;">
          <el-table-column prop="serial_no" label="临时序号" width="100" />
          <el-table-column prop="team_name" label="队伍名称" min-width="180" />
          <el-table-column prop="captain_name" label="队长" width="120" />
          <el-table-column prop="captain_student_id" label="学号" width="160" />
          <el-table-column label="选题" min-width="180">
            <template #default="{ row }">
              {{ formatTopicName(row.topic_title) || '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="bulkInspectionVisible = false">取消</el-button>
          <el-button type="primary" :loading="batchSavingInspection" @click="submitBatchInspection">批量下发验收安排</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { getCurrentCompetitionEvent, updateCompetitionEventName } from '@/api/competition'
import {
  batchUpdateTeamTopic,
  batchUpdateTeamInspection,
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
const savingTopic = ref(false)
const savingInspection = ref(false)
const batchSavingInspection = ref(false)
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
const bulkInspectionVisible = ref(false)
const bulkTeamsSource = ref([])
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

const bulkForm = reactive({
  topic_id: null,
  start_no: 1,
  end_no: 1,
  first_inspection_time: null,
  first_inspection_location: '',
  first_inspector: '',
  first_notes: '',
  second_inspection_time: null,
  second_inspection_location: '',
  second_inspector: '',
  second_notes: ''
})

const bulkTopicTeams = computed(() => {
  if (!bulkForm.topic_id) return []
  const sorted = bulkTeamsSource.value
    .filter((item) => item.topic_id === bulkForm.topic_id)
    .slice()
    .sort((a, b) => a.id - b.id)

  return sorted.map((item, index) => ({
    ...item,
    serial_no: index + 1
  }))
})

const bulkMaxSerial = computed(() => bulkTopicTeams.value.length)

const bulkTargetTeams = computed(() => {
  if (!bulkTopicTeams.value.length) return []
  const start = Math.max(1, Number(bulkForm.start_no || 1))
  const end = Math.max(start, Number(bulkForm.end_no || start))
  return bulkTopicTeams.value.filter((item) => item.serial_no >= start && item.serial_no <= end)
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

const goBack = () => {
  router.push('/admin/management')
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

const loadAllTeamsForBulk = async () => {
  if (!activeModuleKey.value) {
    bulkTeamsSource.value = []
    return
  }

  const res = await getTeams({ module_key: activeModuleKey.value })
  bulkTeamsSource.value = Array.isArray(res.data) ? res.data : []
}

const onBulkTopicChange = () => {
  bulkForm.start_no = 1
  bulkForm.end_no = Math.max(1, bulkMaxSerial.value)
}

const openBulkInspectionDialog = async () => {
  if (!activeModuleKey.value) {
    ElMessage.warning('当前没有比赛上下文，无法进行批量维护')
    return
  }

  try {
    await loadAllTeamsForBulk()
    bulkForm.topic_id = null
    bulkForm.start_no = 1
    bulkForm.end_no = 1
    bulkForm.first_inspection_time = null
    bulkForm.first_inspection_location = ''
    bulkForm.first_inspector = ''
    bulkForm.first_notes = ''
    bulkForm.second_inspection_time = null
    bulkForm.second_inspection_location = ''
    bulkForm.second_inspector = ''
    bulkForm.second_notes = ''
    bulkInspectionVisible.value = true
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '加载批量维护数据失败')
  }
}

const saveConfig = async () => {
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
  if (!activeEventId.value) {
    ElMessage.warning('未找到比赛ID，请从后台管理比赛历史入口进入')
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

  savingTopic.value = true
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
    savingTopic.value = false
  }
}

const submitInspection = async () => {
  if (!editingTeamId.value) return
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

const submitBatchInspection = async () => {
  if (!bulkForm.topic_id) {
    ElMessage.warning('请先选择选题')
    return
  }

  if (!bulkTargetTeams.value.length) {
    ElMessage.warning('当前起止序号未命中任何队伍')
    return
  }

  const payload = {
    team_ids: bulkTargetTeams.value.map((item) => item.id),
    first_inspection_time: bulkForm.first_inspection_time,
    first_inspection_location: bulkForm.first_inspection_location || null,
    first_inspector: bulkForm.first_inspector || null,
    first_notes: bulkForm.first_notes || null,
    second_inspection_time: bulkForm.second_inspection_time,
    second_inspection_location: bulkForm.second_inspection_location || null,
    second_inspector: bulkForm.second_inspector || null,
    second_notes: bulkForm.second_notes || null,
    check_duplicate: true
  }

  const hasUpdate = [
    payload.first_inspection_time,
    payload.first_inspection_location,
    payload.first_inspector,
    payload.first_notes,
    payload.second_inspection_time,
    payload.second_inspection_location,
    payload.second_inspector,
    payload.second_notes,
  ].some((value) => value !== null && value !== undefined && value !== '')

  if (!hasUpdate) {
    ElMessage.warning('请至少填写一项验收信息')
    return
  }

  const confirmText = `将对选题下序号 ${bulkForm.start_no}-${bulkForm.end_no} 的 ${bulkTargetTeams.value.length} 支队伍下发验收安排，确认继续吗？`
  const confirmed = await ElMessageBox.confirm(confirmText, '批量验收维护确认', {
    confirmButtonText: '确认下发',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => true).catch(() => false)

  if (!confirmed) return

  batchSavingInspection.value = true
  try {
    const res = await batchUpdateTeamInspection(payload)
    const skipped = res.data?.skipped_duplicate_team_ids || []
    if (skipped.length) {
      ElMessage.warning(`已更新 ${res.data?.updated || 0} 支，跳过重复安排 ${skipped.length} 支`)
    } else {
      ElMessage.success(res.msg || '批量验收维护成功')
    }
    await fetchList()
    bulkInspectionVisible.value = false
  } catch (error) {
    const skipped = error.response?.data?.data?.skipped_duplicate_team_ids
    if (Array.isArray(skipped) && skipped.length) {
      ElMessage.warning(`检测到重复安排，已拦截本次提交（重复 ${skipped.length} 支）`)
    } else {
      ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '批量维护失败')
    }
  } finally {
    batchSavingInspection.value = false
  }
}

const handleConfirmDelete = async (row) => {
  if (!row?.id) return
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
  try {
    const res = await getCurrentCompetitionEvent()
    const currentEvent = res.data

    // 无论是否携带历史比赛参数，只要当前没有进行中的比赛，就进入“没在比赛中”状态
    if (!currentEvent?.module_key) {
      noActiveEvent.value = true
      tableData.value = []
      topics.value = []
      Object.assign(signupStatus, { signup_open: false, signup_close_at: null })
      Object.assign(topicStatus, { topic_open: false, topic_close_at: null })
      Object.assign(updateStatus, { info_update_open: false, info_update_close_at: null })
      return
    }

    if (activeModuleKey.value) {
      noActiveEvent.value = false
      return
    }

    noActiveEvent.value = false
    await router.replace({
      path: route.path,
      query: {
        ...route.query,
        module_key: currentEvent.module_key,
        event_id: String(currentEvent.id),
        event_name: currentEvent.display_title || currentEvent.name,
        cup_type: currentEvent.cup_type
      }
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
    await ensureCurrentEventContext()
    if (noActiveEvent.value) return
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

<style scoped>
.contest-team-table :deep(.el-scrollbar__bar.is-horizontal) {
  opacity: 1;
}

.contest-team-table :deep(.el-table__fixed-right) {
  box-shadow: -8px 0 16px -12px rgba(15, 23, 42, 0.32);
}
</style>
