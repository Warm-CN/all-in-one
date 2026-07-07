<template>
  <div class="flex h-full min-h-0 flex-col gap-5 pb-2 sm:gap-6 sm:pb-3">
    <section class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] px-5 pb-5 pt-6 shadow-[0_14px_34px_-28px_rgba(15,23,42,0.22)] sm:px-6 sm:pb-6 sm:pt-7 lg:px-7 lg:pb-7 lg:pt-8">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div class="min-w-0">
          <span class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-[11px] font-semibold tracking-[0.18em] text-blue-600">{{ badgeText }}</span>
          <h2 class="mt-3 max-w-full pt-1 text-[1.95rem] font-black tracking-tight text-slate-900 sm:text-[2.2rem]">{{ cupTitle }}赛事中心</h2>
          <p class="mt-2 text-sm leading-6 text-slate-500">点击历史可跳转到竞赛队伍管理页面按对应比赛操控，支持创建比赛、配置报名页展示标题与选题。</p>
        </div>
        <div v-if="userStore.isAdmin" class="flex flex-col gap-2 lg:justify-end">
          <el-button type="primary" class="!h-11 !rounded-2xl !px-5" @click="openCreateDialog">新建比赛</el-button>
          <el-button class="!h-11 !rounded-2xl !px-5" @click="goTeamPortal">进入报名网页</el-button>
        </div>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.18)] sm:p-6">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-800">比赛历史</h3>
        <el-button class="!rounded-xl" @click="fetchEvents" :loading="loading">刷新</el-button>
      </div>

      <div v-if="!events.length && !loading" class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
        暂无比赛，{{ userStore.isAdmin ? '点击右上角“新建比赛”开始创建' : '请等待管理员创建比赛' }}。
      </div>

      <div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <article v-for="item in events" :key="item.id" class="rounded-2xl border border-slate-200/80 bg-white/95 p-4 shadow-[0_10px_24px_-24px_rgba(15,23,42,0.4)] overflow-hidden">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <h4 class="text-base font-semibold text-slate-900 truncate">{{ item.name }}</h4>
              <p class="mt-1 text-xs text-slate-500 truncate">报名页标题：{{ item.display_title }}</p>
              <p class="mt-1 text-xs text-slate-500 truncate">模块标识：{{ item.module_key }}</p>
            </div>
            <el-tag :type="item.is_current ? 'success' : 'info'" class="shrink-0">{{ item.is_current ? '正在比赛' : '已结束' }}</el-tag>
          </div>

          <div class="mt-4 grid grid-cols-3 gap-2 text-center text-xs">
            <div class="rounded-xl bg-slate-50 px-2 py-2">
              <div class="font-semibold text-slate-700">队伍数</div>
              <div class="mt-1 text-sm font-bold text-slate-900">{{ item.team_count }}</div>
            </div>
            <div class="rounded-xl bg-slate-50 px-2 py-2">
              <div class="font-semibold text-slate-700">报名人数</div>
              <div class="mt-1 text-sm font-bold text-slate-900">{{ item.total_people }}</div>
            </div>
            <div class="rounded-xl bg-slate-50 px-2 py-2">
              <div class="font-semibold text-slate-700">选题数</div>
              <div class="mt-1 text-sm font-bold text-slate-900">{{ item.topic_count }}（不限）</div>
            </div>
          </div>

          <div class="mt-3 text-xs leading-6 text-slate-500 break-all">
            比赛周期：{{ formatRange(item.cycle_start_at, item.cycle_end_at) }}<br />
            报名时间：{{ formatRange(item.signup_start_at, item.signup_end_at) }}<br />
            选题时间：{{ formatRange(item.topic_open_at, item.topic_end_at) }}
          </div>

          <div v-if="!item.is_current" class="mt-3 rounded-xl border border-slate-200/80 bg-slate-50/80 p-3">
            <div class="text-xs font-semibold text-slate-700">已结束比赛统计（按选题）</div>
            <div v-if="item.topics?.length" class="mt-2 space-y-2">
              <div v-for="topic in item.topics" :key="topic.id" class="flex items-center justify-between gap-3 rounded-lg bg-white px-3 py-2 text-xs">
                <span class="min-w-0 truncate text-slate-700">{{ topic.title }}</span>
                <span class="text-slate-500">队伍 {{ topic.selected_team_count || 0 }} / 人数 {{ topic.selected_total_people || 0 }}</span>
              </div>
            </div>
            <div v-else class="mt-2 text-xs text-slate-500">该比赛暂无选题</div>
          </div>

          <div class="mt-4 flex flex-wrap gap-2">
            <el-button type="primary" class="!rounded-xl" @click="goTeamsCenter(item)">竞赛队伍管理</el-button>
            <el-button v-if="userStore.isAdmin" class="!rounded-xl" @click="openTopicDialog(item)">修改选题</el-button>
          </div>
          <div class="mt-2">
            <el-button v-if="userStore.isAdmin" link type="success" :loading="activatingId === item.id" @click="toggleActive(item)">
              {{ item.is_current ? '设为不进行' : '设为正在比赛' }}
            </el-button>
          </div>
        </article>
      </div>
    </section>

    <el-dialog v-model="createDialogVisible" title="新建比赛" width="760px" destroy-on-close>
      <el-form :model="createForm" label-position="top" size="large">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <el-form-item label="比赛名称"><el-input v-model="createForm.name" placeholder="如：2025年无线杯" /></el-form-item>
          <el-form-item label="比赛周期开始时间"><el-date-picker v-model="createForm.cycle_start_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
          <el-form-item label="比赛周期结束时间"><el-date-picker v-model="createForm.cycle_end_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
          <el-form-item label="报名开始日期"><el-date-picker v-model="createForm.signup_start_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
          <el-form-item label="报名截止日期"><el-date-picker v-model="createForm.signup_end_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
          <el-form-item label="选题开放日期"><el-date-picker v-model="createForm.topic_open_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
          <el-form-item label="选题截止日期"><el-date-picker v-model="createForm.topic_end_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" class="w-full" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="creating" @click="submitCreate">创建比赛</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="portalDialogVisible" title="新建报名网页设置" width="560px" destroy-on-close>
      <el-form :model="portalForm" label-position="top" size="large">
        <el-form-item label="报名网页显示比赛名称">
          <el-input v-model="portalForm.portal_title" placeholder="如：2025年无线杯" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="portalDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingPortal" @click="submitPortalConfig">保存并继续</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="topicDialogVisible" title="修改选题" width="860px" destroy-on-close>
      <div class="mb-4 rounded-xl border border-slate-200 bg-slate-50 p-3">
        <div class="mb-2 text-sm font-semibold text-slate-700">已添加选题</div>
        <div v-if="!topicDialogTopics.length" class="text-xs text-slate-500">当前比赛暂无选题，可在下方新增。</div>
        <div v-else class="space-y-2">
          <div
            v-for="topic in topicDialogTopics"
            :key="topic.id"
            class="flex items-center justify-between rounded-lg border px-3 py-2 cursor-pointer"
            :class="selectedTopicId === topic.id ? 'border-blue-300 bg-blue-50' : 'border-slate-200 bg-white'"
            @click="selectTopicForEdit(topic)"
          >
            <span class="min-w-0 truncate text-sm text-slate-700">{{ topic.title }}</span>
            <el-button link type="primary" @click.stop="downloadTopicDocument(topic)">下载选题文件</el-button>
          </div>
        </div>
      </div>

      <el-form :model="topicForm" label-position="top" size="large">
        <div class="mb-2 flex items-center justify-end">
          <el-button link type="primary" @click="startCreateTopic">新增选题</el-button>
        </div>
        <el-form-item label="选题名称"><el-input v-model="topicForm.title" placeholder="请输入选题名称" /></el-form-item>
        <el-form-item label="题目简介（选填）"><el-input v-model="topicForm.description" type="textarea" :rows="3" placeholder="请输入题目简介" /></el-form-item>
        <el-form-item label="题目文档（可选：pdf/doc/docx）">
          <el-upload class="w-full" drag action="#" :auto-upload="false" :limit="1" :on-change="onFileChange" :on-remove="onFileRemove" :file-list="uploadList">
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="closeTopicDialog">取消</el-button>
          <el-button type="primary" :loading="creatingTopic" @click="submitTopic">{{ selectedTopicId ? '保存修改' : '添加选题' }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import {
  createCompetitionEvent,
  createCompetitionTopic,
  getCompetitionEventDetail,
  getCompetitionEvents,
  updateCompetitionActiveState,
  updateCompetitionPortalTitle,
  updateCompetitionTopic,
} from '@/api/competition'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const creating = ref(false)
const creatingTopic = ref(false)
const savingPortal = ref(false)
const activatingId = ref(null)

const createDialogVisible = ref(false)
const topicDialogVisible = ref(false)
const portalDialogVisible = ref(false)

const events = ref([])
const selectedEventId = ref(null)
const justCreatedEventId = ref(null)
const selectedTopicId = ref(null)
const topicDialogTopics = ref([])

const selectedFile = ref(null)
const uploadList = ref([])

const createForm = reactive({
  name: '',
  signup_start_at: null,
  signup_end_at: null,
  topic_open_at: null,
  topic_end_at: null,
  cycle_start_at: null,
  cycle_end_at: null,
})

const portalForm = reactive({
  portal_title: '',
})

const topicForm = reactive({
  title: '',
  description: '',
})

const cupType = computed(() => route.meta.cupType || 'wireless')
const cupTitle = computed(() => (cupType.value === 'wireless' ? '无线杯' : '电信杯'))
const badgeText = computed(() => (cupType.value === 'wireless' ? 'WIRELESS CUP' : 'TELECOM CUP'))

const formatRange = (start, end) => {
  const left = start ? new Date(start).toLocaleString() : '未设置'
  const right = end ? new Date(end).toLocaleString() : '未设置'
  return `${left} ~ ${right}`
}

const fetchEvents = async () => {
  loading.value = true
  try {
    const res = await getCompetitionEvents(cupType.value)
    events.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '获取比赛历史失败')
  } finally {
    loading.value = false
  }
}

const goTeamsCenter = async (event) => {
  await router.push({
    path: '/teams-center',
    query: {
      module_key: event.module_key,
      event_id: event.id,
      event_name: event.display_title || event.name,
      cup_type: event.cup_type
    }
  })
}

const goTeamPortal = () => {
  window.open('/team-portal', '_blank')
}

const openCreateDialog = () => {
  createForm.name = ''
  createForm.signup_start_at = null
  createForm.signup_end_at = null
  createForm.topic_open_at = null
  createForm.topic_end_at = null
  createForm.cycle_start_at = null
  createForm.cycle_end_at = null
  createDialogVisible.value = true
}

const submitCreate = async () => {
  if (!createForm.name.trim()) {
    ElMessage.warning('请输入比赛名称')
    return
  }

  creating.value = true
  try {
    const res = await createCompetitionEvent({
      cup_type: cupType.value,
      name: createForm.name.trim(),
      signup_start_at: createForm.signup_start_at,
      signup_end_at: createForm.signup_end_at,
      topic_open_at: createForm.topic_open_at,
      topic_end_at: createForm.topic_end_at,
      cycle_start_at: createForm.cycle_start_at,
      cycle_end_at: createForm.cycle_end_at,
    })
    ElMessage.success(res.msg || '创建成功')
    createDialogVisible.value = false
    justCreatedEventId.value = res.data?.event_id || null
    portalForm.portal_title = createForm.name.trim()
    portalDialogVisible.value = true
    await fetchEvents()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '创建比赛失败')
  } finally {
    creating.value = false
  }
}

const submitPortalConfig = async () => {
  if (!justCreatedEventId.value) {
    portalDialogVisible.value = false
    return
  }
  if (!portalForm.portal_title.trim()) {
    ElMessage.warning('请输入报名网页显示比赛名称')
    return
  }

  savingPortal.value = true
  try {
    await updateCompetitionPortalTitle(justCreatedEventId.value, portalForm.portal_title.trim())
    ElMessage.success('报名网页显示名称已保存')
    portalDialogVisible.value = false
    await fetchEvents()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '保存失败')
  } finally {
    savingPortal.value = false
  }
}

const toggleActive = async (event) => {
  activatingId.value = event.id
  try {
    await updateCompetitionActiveState(event.id, !event.is_current)
    ElMessage.success('比赛状态已更新')
    await fetchEvents()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '状态更新失败')
  } finally {
    activatingId.value = null
  }
}

const openTopicDialog = (event) => {
  selectedEventId.value = event.id
  topicDialogTopics.value = Array.isArray(event.topics) ? event.topics : []
  startCreateTopic()
  topicDialogVisible.value = true
}

const selectTopicForEdit = (topic) => {
  selectedTopicId.value = topic.id
  topicForm.title = topic.title || ''
  topicForm.description = topic.description || ''
  selectedFile.value = null
  uploadList.value = []
}

const downloadTopicDocument = (topic) => {
  if (!topic?.document_url) {
    ElMessage.warning('该选题暂无可下载文件')
    return
  }
  window.open(topic.document_url, '_blank')
}

const startCreateTopic = () => {
  selectedTopicId.value = null
  topicForm.title = ''
  topicForm.description = ''
  selectedFile.value = null
  uploadList.value = []
}

const onFileChange = (file) => {
  selectedFile.value = file.raw
  uploadList.value = [file]
}

const onFileRemove = () => {
  selectedFile.value = null
  uploadList.value = []
}

const closeTopicDialog = () => {
  topicDialogVisible.value = false
  startCreateTopic()
  topicDialogTopics.value = []
}

const refreshTopicDialogEvent = async () => {
  if (!selectedEventId.value) return
  const detailRes = await getCompetitionEventDetail(selectedEventId.value)
  const detail = detailRes.data || {}
  topicDialogTopics.value = Array.isArray(detail.topics) ? detail.topics : []
}

const submitTopic = async () => {
  if (!selectedEventId.value) {
    ElMessage.warning('请先选择比赛')
    return
  }
  if (!topicForm.title.trim()) {
    ElMessage.warning('请输入选题名称')
    return
  }

  creatingTopic.value = true
  try {
    if (selectedTopicId.value) {
      await updateCompetitionTopic(selectedEventId.value, selectedTopicId.value, {
        title: topicForm.title.trim(),
        description: topicForm.description.trim(),
        document: selectedFile.value,
      })
      ElMessage.success('选题修改成功')
    } else {
      await createCompetitionTopic(selectedEventId.value, {
        title: topicForm.title.trim(),
        description: topicForm.description.trim(),
        document: selectedFile.value,
      })
      ElMessage.success('选题添加成功')
    }

    await refreshTopicDialogEvent()
    startCreateTopic()
    await fetchEvents()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '选题保存失败')
  } finally {
    creatingTopic.value = false
  }
}

onMounted(fetchEvents)

watch(
  () => route.meta.cupType,
  async () => {
    await fetchEvents()
  }
)
</script>
