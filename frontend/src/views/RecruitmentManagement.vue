<template>
  <div class="h-full recruitment-page">
    <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">招新报名管理</h2>
        <p class="mt-1 text-sm text-slate-500">共 {{ tableData.length }} 人报名</p>
      </div>
      <div class="flex items-center gap-2" v-if="userStore.isAdmin">
        <el-upload
          :show-file-list="false"
          accept=".xlsx"
          :http-request="handleImportUpload"
        >
          <el-button type="primary" plain :loading="importing">导入一/二面安排（xlsx）</el-button>
        </el-upload>
        <el-button type="success" @click="handleExport" :loading="exporting">
          下载面试模板
        </el-button>
      </div>
    </div>

    <div class="mb-3 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-xs text-blue-700" v-if="userStore.isAdmin">
      导入模板用于批量写入一面/二面时间地点；当前系统阶段请在下方“招新渠道与阶段控制”里设置。
    </div>

    <div class="mb-4 rounded-xl border border-slate-100 bg-white p-4" v-if="userStore.isAdmin">
      <div class="mb-3 text-sm font-semibold text-slate-700">招新渠道与阶段控制</div>
      <div class="grid grid-cols-1 gap-3 md:grid-cols-5">
        <el-input v-model="configForm.title" placeholder="招新活动名称" />
        <el-date-picker v-model="configForm.start_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="开放报名时间" />
        <el-date-picker v-model="configForm.end_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="关闭报名时间" />
        <el-select v-model="configForm.current_stage" placeholder="当前阶段">
          <el-option v-for="item in stageOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <div class="flex items-center gap-2">
          <el-switch v-model="configForm.is_active" active-text="开放" inactive-text="关闭" />
          <el-button type="primary" :loading="savingConfig" @click="saveRecruitmentConfig">保存</el-button>
        </div>
      </div>
    </div>

    <div class="mb-4 grid grid-cols-1 gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4 md:grid-cols-3">
      <el-input v-model="filters.keyword" placeholder="姓名/学号/手机号" clearable @keyup.enter="fetchList" />
      <el-select v-model="filters.department" placeholder="按部门筛选" clearable>
        <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <div class="flex gap-2">
        <el-button type="primary" @click="fetchList">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>

    <el-table :data="tableData" border stripe height="calc(100% - 170px)" v-loading="loading">
      <el-table-column prop="name" label="姓名" min-width="100" />
      <el-table-column prop="student_id" label="学号" min-width="120" />
      <el-table-column prop="phone" label="手机号" min-width="130" />
      <el-table-column prop="current_stage_desc" label="当前阶段" min-width="130">
        <template #default="{ row }">
          <el-tag :type="stageTagType(row.current_stage)">{{ row.current_stage_desc || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="first_choice" label="第一志愿" min-width="140" />
      <el-table-column prop="second_choice" label="第二志愿" min-width="140" />
      <el-table-column label="面试安排" min-width="280">
        <template #default="{ row }">
          <div class="text-xs leading-6 text-slate-600 whitespace-pre-wrap">{{ formatInterviewPlan(row) }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="college" label="学院" min-width="150" />
      <el-table-column prop="major" label="专业班级" min-width="150" />
      <el-table-column label="自我介绍" min-width="220">
        <template #default="{ row }">
          <el-tooltip effect="dark" :content="row.intro || '-'" placement="top" :show-after="300">
            <span class="inline-block max-w-[200px] truncate text-slate-600">{{ row.intro || '-' }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="180" fixed="right" v-if="userStore.isAdmin">
        <template #default="{ row }">
          <div class="flex gap-2">
            <el-button link type="primary" @click="openEdit(row)">修改</el-button>
            <el-button link type="danger" @click="removeRow(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" title="修改报名信息" width="860px" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" :rules="rules" label-position="top" size="large">
        <div class="grid grid-cols-1 gap-x-4 gap-y-1 md:grid-cols-2">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="editForm.name" />
          </el-form-item>
          <el-form-item label="学号">
            <el-input v-model="editForm.student_id" disabled />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="editForm.phone" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="editForm.email" />
          </el-form-item>
          <el-form-item label="学院" prop="college">
            <el-input v-model="editForm.college" />
          </el-form-item>
          <el-form-item label="专业班级" prop="major">
            <el-input v-model="editForm.major" />
          </el-form-item>
          <el-form-item label="第一志愿" prop="first_choice">
            <el-input v-model="editForm.first_choice" />
          </el-form-item>
          <el-form-item label="第二志愿" prop="second_choice">
            <el-input v-model="editForm.second_choice" />
          </el-form-item>
          <el-form-item label="服从调剂" prop="adjust">
            <el-select v-model="editForm.adjust" class="w-full">
              <el-option label="是" value="是" />
              <el-option label="否" value="否" />
            </el-select>
          </el-form-item>
        </div>

        <div class="grid grid-cols-1 gap-x-4 gap-y-1 md:grid-cols-2">
          <el-form-item label="一面-第一志愿时间">
            <el-input v-model="editForm.first_choice_interview_time" placeholder="如：2026-04-03 19:00" />
          </el-form-item>
          <el-form-item label="一面-第一志愿地点">
            <el-input v-model="editForm.first_choice_interview_location" placeholder="如：主楼A201" />
          </el-form-item>
          <el-form-item label="一面-第二志愿时间">
            <el-input v-model="editForm.second_choice_interview_time" placeholder="如：2026-04-04 19:00" />
          </el-form-item>
          <el-form-item label="一面-第二志愿地点">
            <el-input v-model="editForm.second_choice_interview_location" placeholder="如：主楼A202" />
          </el-form-item>
          <el-form-item label="二面部门">
            <el-select v-model="editForm.second_round_department" class="w-full" clearable placeholder="请选择二面部门">
              <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="二面时间">
            <el-input v-model="editForm.second_round_interview_time" placeholder="如：2026-04-10 19:00" />
          </el-form-item>
          <el-form-item label="二面地点">
            <el-input v-model="editForm.second_round_interview_location" placeholder="如：主楼B301" />
          </el-form-item>
          <el-form-item label="通知备注">
            <el-input v-model="editForm.review_notes" placeholder="给同学的通知信息" />
          </el-form-item>
        </div>

        <el-form-item label="自我介绍" prop="intro">
          <el-input v-model="editForm.intro" type="textarea" :rows="4" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import {
  adminDeleteApplication,
  adminUpdateApplication,
  exportApplications,
  getInternalApplications,
  importInterviewArrangements,
  getAdminSignupConfigs,
  updateAdminSignupConfig
} from '@/api/recruitment'

const userStore = useUserStore()

const loading = ref(false)
const exporting = ref(false)
const importing = ref(false)
const savingConfig = ref(false)
const tableData = ref([])
const recruitmentConfigId = ref(null)

const stageOptions = [
  { label: '报名阶段', value: 'registration' },
  { label: '第一轮面试', value: 'first_round' },
  { label: '第二轮面试', value: 'second_round' },
  { label: '已结束', value: 'ended' }
]

const configForm = reactive({
  title: '',
  start_time: '',
  end_time: '',
  current_stage: 'registration',
  is_active: false
})

const editVisible = ref(false)
const saving = ref(false)
const editingId = ref(null)
const editFormRef = ref(null)

const departmentOptions = ['科创部', '新媒体运营部', '外联部', '宣传部', '组织部']

const filters = reactive({
  keyword: '',
  department: ''
})

const editForm = reactive({
  name: '',
  student_id: '',
  phone: '',
  email: '',
  college: '',
  major: '',
  first_choice: '',
  second_choice: '',
  adjust: '',
  intro: '',
  first_choice_interview_time: '',
  first_choice_interview_location: '',
  second_choice_interview_time: '',
  second_choice_interview_location: '',
  second_round_department: '',
  second_round_interview_time: '',
  second_round_interview_location: '',
  review_notes: ''
})

const rules = reactive({
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  college: [{ required: true, message: '请输入学院', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业班级', trigger: 'blur' }],
  first_choice: [{ required: true, message: '请输入第一志愿', trigger: 'blur' }],
  adjust: [{ required: true, message: '请选择是否服从调剂', trigger: 'change' }],
  intro: [{ required: true, message: '请填写自我介绍', trigger: 'blur' }]
})

const fetchRecruitmentConfig = async () => {
  try {
    const res = await getAdminSignupConfigs({ category: 'recruitment' })
    const list = Array.isArray(res.data) ? res.data : []
    if (!list.length) return
    const cfg = list[0]
    recruitmentConfigId.value = cfg.id
    configForm.title = cfg.title || ''
    configForm.start_time = (cfg.start_time || '').slice(0, 19)
    configForm.end_time = (cfg.end_time || '').slice(0, 19)
    configForm.current_stage = cfg.current_stage || 'registration'
    configForm.is_active = !!cfg.is_active
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '获取招新配置失败')
  }
}

const saveRecruitmentConfig = async () => {
  if (!recruitmentConfigId.value) return
  savingConfig.value = true
  try {
    await updateAdminSignupConfig(recruitmentConfigId.value, {
      title: configForm.title,
      start_time: configForm.start_time,
      end_time: configForm.end_time,
      current_stage: configForm.current_stage,
      is_active: configForm.is_active
    })
    ElMessage.success('招新配置已保存')
    await fetchList()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '保存招新配置失败')
  } finally {
    savingConfig.value = false
  }
}

const fetchList = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.department) params.department = filters.department

    const res = await getInternalApplications(params)
    tableData.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '获取报名列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.department = ''
  fetchList()
}

const openEdit = (row) => {
  if (!userStore.isAdmin) return

  const data = row.form_data || {}
  editingId.value = row.id

  editForm.name = row.name || data['姓名'] || ''
  editForm.student_id = row.student_id || ''
  editForm.phone = row.phone || data['手机号'] || ''
  editForm.email = data['邮箱'] || ''
  editForm.college = data['学院'] || ''
  editForm.major = data['专业班级'] || ''
  editForm.first_choice = data['第一志愿'] || ''
  editForm.second_choice = data['第二志愿'] === '无' ? '' : (data['第二志愿'] || '')
  editForm.adjust = data['服从调剂'] || ''
  editForm.intro = data['自我介绍'] || ''
  editForm.first_choice_interview_time = row.first_choice_interview_time || ''
  editForm.first_choice_interview_location = row.first_choice_interview_location || ''
  editForm.second_choice_interview_time = row.second_choice_interview_time || ''
  editForm.second_choice_interview_location = row.second_choice_interview_location || ''
  editForm.second_round_department = row.second_round_department || ''
  editForm.second_round_interview_time = row.second_round_interview_time || ''
  editForm.second_round_interview_location = row.second_round_interview_location || ''
  editForm.review_notes = row.review_notes || ''

  editVisible.value = true
}

const submitEdit = async () => {
  if (!userStore.isAdmin || !editFormRef.value || !editingId.value) return
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    await adminUpdateApplication(editingId.value, {
      name: editForm.name,
      phone: editForm.phone,
      review_notes: editForm.review_notes,
      first_choice_interview_time: editForm.first_choice_interview_time || null,
      first_choice_interview_location: editForm.first_choice_interview_location || null,
      second_choice_interview_time: editForm.second_choice_interview_time || null,
      second_choice_interview_location: editForm.second_choice_interview_location || null,
      second_round_department: editForm.second_round_department || null,
      second_round_interview_time: editForm.second_round_interview_time || null,
      second_round_interview_location: editForm.second_round_interview_location || null,
      form_data: {
        姓名: editForm.name,
        手机号: editForm.phone,
        邮箱: editForm.email,
        学院: editForm.college,
        专业班级: editForm.major,
        第一志愿: editForm.first_choice,
        第二志愿: editForm.second_choice || '无',
        服从调剂: editForm.adjust,
        自我介绍: editForm.intro
      }
    })
    ElMessage.success('修改成功')
    editVisible.value = false
    fetchList()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '修改失败')
  } finally {
    saving.value = false
  }
}

const removeRow = async (row) => {
  if (!userStore.isAdmin) return

  try {
    await ElMessageBox.confirm(`确认删除 ${row.name} 的报名记录吗？`, '删除确认', {
      type: 'warning'
    })

    await adminDeleteApplication(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (error) {
    if (error === 'cancel') return
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '删除失败')
  }
}

const handleExport = async () => {
  if (!userStore.isAdmin) return

  exporting.value = true
  try {
    const params = {}
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.department) params.department = filters.department

    const blobData = await exportApplications(params)
    const blob = new Blob([blobData], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '招新面试模板.xlsx'
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

const handleImportUpload = async (uploadRequest) => {
  if (!userStore.isAdmin) return
  const file = uploadRequest?.file
  if (!file) {
    ElMessage.error('未选择文件')
    return
  }

  importing.value = true
  try {
    const res = await importInterviewArrangements(file)
    if (typeof uploadRequest?.onSuccess === 'function') {
      uploadRequest.onSuccess(res)
    }
    ElMessage.success(res.msg || '导入成功')
    await fetchList()
  } catch (error) {
    if (typeof uploadRequest?.onError === 'function') {
      uploadRequest.onError(error)
    }
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

const stageTagType = (stage) => {
  if (stage === 'registration') return 'info'
  if (stage === 'second_round') return 'warning'
  if (stage === 'ended') return 'danger'
  return 'info'
}

const formatInterviewPlan = (row) => {
  if (row.current_stage === 'registration') {
    return '当前处于报名阶段'
  }

  if (row.current_stage === 'second_round') {
    const dept = row.second_round_department || '-'
    const time = row.second_round_interview_time || '待安排'
    const location = row.second_round_interview_location || '待安排'
    return `二面（${dept}）\n时间：${time}\n地点：${location}`
  }

  if (row.current_stage === 'ended') {
    return '招新流程已结束'
  }

  const firstTime = row.first_choice_interview_time || '待安排'
  const firstLocation = row.first_choice_interview_location || '待安排'
  const secondTime = row.second_choice_interview_time || '待安排'
  const secondLocation = row.second_choice_interview_location || '待安排'
  return `一面-第一志愿\n时间：${firstTime}\n地点：${firstLocation}\n\n一面-第二志愿\n时间：${secondTime}\n地点：${secondLocation}`
}

onMounted(() => {
  fetchRecruitmentConfig()
  fetchList()
})
</script>

<style scoped>
.recruitment-page :deep(.el-table th.el-table__cell) {
  background: #f8fafc;
  color: #334155;
}
</style>
