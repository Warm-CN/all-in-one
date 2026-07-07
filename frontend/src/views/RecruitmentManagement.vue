<template>
  <div class="recruitment-page flex h-full min-h-0 flex-col gap-5 pb-2 sm:gap-6 sm:pb-3">
    <section class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] px-5 pb-5 pt-6 shadow-[0_14px_34px_-28px_rgba(15,23,42,0.22)] sm:px-6 sm:pb-6 sm:pt-7 lg:px-7 lg:pb-7 lg:pt-8">
      <div class="flex flex-col gap-5 2xl:flex-row 2xl:items-start 2xl:justify-between">
        <div class="min-w-0">
          <span class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-[11px] font-semibold tracking-[0.18em] text-blue-600">
            RECRUITMENT
          </span>
          <h2 class="recruitment-hero-title mt-3 max-w-full pt-1 text-[1.95rem] font-black tracking-tight text-slate-900 sm:text-[2.2rem]">
            招新报名
          </h2>
        </div>

        <div v-if="userStore.isAdmin" class="flex flex-col gap-2 sm:flex-row 2xl:justify-end">
          <el-upload
            :show-file-list="false"
            accept=".xlsx"
            :http-request="handleImportUpload"
            class="w-full sm:w-auto"
          >
            <el-button type="primary" plain :loading="importing" class="!h-11 !w-full !rounded-2xl !px-5 sm:!w-auto">
              导入一/二面安排（xlsx）
            </el-button>
          </el-upload>
          <el-button type="success" @click="handleExport" :loading="exporting" class="!h-11 !w-full !rounded-2xl !px-5 sm:!w-auto">
            下载报名信息
          </el-button>
        </div>
      </div>

      <div class="mt-5 grid grid-cols-1 gap-3 md:grid-cols-2">
        <div class="stat-card rounded-[20px] border border-slate-200/80 bg-white/92 px-4 py-3.5 shadow-[0_10px_24px_-26px_rgba(15,23,42,0.24)]">
          <div class="stat-card__label text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">报名人数</div>
          <div class="stat-card__value mt-1.5 text-[1.45rem] font-black text-slate-900">{{ tableData.length }}</div>
        </div>
        <div
          class="stat-card rounded-[20px] border px-4 py-3.5 shadow-[0_10px_24px_-26px_rgba(15,23,42,0.24)]"
          :class="configForm.is_active ? 'border-emerald-200 bg-emerald-50/80' : 'border-amber-200 bg-amber-50/80'"
        >
          <div class="stat-card__label text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">当前状态</div>
          <div class="stat-card__value mt-1.5 text-[15px] font-semibold" :class="configForm.is_active ? 'text-emerald-700' : 'text-slate-700'">
            {{ configForm.is_active ? '报名开放中' : '报名已关闭' }}
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.18)] sm:p-6">
      <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <h3 class="section-title text-lg font-semibold text-slate-800">筛选</h3>
        <div class="inline-flex w-fit items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">
          当前已载入 {{ tableData.length }} 条记录
        </div>
      </div>

      <div class="mt-5 grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.15fr)_320px_auto]">
        <el-input v-model="filters.keyword" placeholder="姓名 / 学号 / 手机号" clearable @keyup.enter="fetchList" />
        <el-select v-model="filters.department" placeholder="按部门筛选" clearable class="w-full">
          <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <div class="flex flex-col gap-2 sm:flex-row xl:justify-end">
          <el-button type="primary" @click="fetchList" class="!h-11 !w-full !rounded-2xl !px-6 sm:!w-auto">查询</el-button>
          <el-button @click="resetFilters" class="!h-11 !w-full !rounded-2xl !px-6 sm:!w-auto">重置</el-button>
        </div>
      </div>
    </section>

    <section class="flex min-h-0 flex-1 flex-col overflow-hidden rounded-[28px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] shadow-[0_16px_38px_-32px_rgba(15,23,42,0.2)]">
      <div class="flex flex-col gap-3 border-b border-slate-200/80 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <h3 class="section-title text-lg font-semibold text-slate-800">报名列表</h3>
        <div class="text-xs font-medium text-slate-400">列表内容按当前筛选条件实时刷新</div>
      </div>

      <div class="flex h-full min-h-0 flex-col p-4 sm:p-5">
        <div class="min-h-0 flex-1 overflow-auto rounded-[24px] border border-slate-200/80 bg-white">
          <el-table :data="tableData" border stripe height="100%" v-loading="loading" style="min-width: 1460px">
            <el-table-column prop="name" label="姓名" min-width="100" />
            <el-table-column prop="student_id" label="学号" min-width="120" />
            <el-table-column prop="phone" label="手机号" min-width="130" />
            <el-table-column prop="first_choice" label="第一志愿" min-width="140" />
            <el-table-column prop="second_choice" label="第二志愿" min-width="140" />
            <el-table-column label="面试安排" min-width="280">
              <template #default="{ row }">
                <div class="whitespace-pre-wrap text-xs leading-6 text-slate-600">{{ formatInterviewPlan(row) }}</div>
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
                <div class="flex flex-wrap gap-2">
                  <el-button link type="primary" @click="openEdit(row)">修改</el-button>
                  <el-button link type="danger" @click="removeRow(row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </section>

    <el-dialog v-model="editVisible" title="修改报名信息" width="min(860px, calc(100vw - 24px))" destroy-on-close>
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
          <el-form-item label="一面时间">
            <el-input v-model="editForm.first_choice_interview_time" placeholder="如：2026-04-03 19:00" />
          </el-form-item>
          <el-form-item label="一面地点">
            <el-input v-model="editForm.first_choice_interview_location" placeholder="如：主楼A201" />
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
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="editVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="submitEdit">保存</el-button>
        </div>
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
  getAdminSignupConfigs
} from '@/api/recruitment'

const userStore = useUserStore()

const loading = ref(false)
const exporting = ref(false)
const importing = ref(false)
const tableData = ref([])

const configForm = reactive({
  title: '',
  start_time: '',
  end_time: '',
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
    configForm.title = cfg.title || ''
    configForm.start_time = (cfg.start_time || '').slice(0, 19)
    configForm.end_time = (cfg.end_time || '').slice(0, 19)
    configForm.is_active = !!cfg.is_active
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '获取招新配置失败')
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
    link.download = '招新报名信息.xlsx'
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

const formatInterviewPlan = (row) => {
  const firstTime = row.first_choice_interview_time || '待安排'
  const firstLocation = row.first_choice_interview_location || '待安排'
  const secondDept = row.second_round_department || '-'
  const secondTime = row.second_round_interview_time || '待安排'
  const secondLocation = row.second_round_interview_location || '待安排'
  return `一面\n时间：${firstTime}\n地点：${firstLocation}\n\n二面（${secondDept}）\n时间：${secondTime}\n地点：${secondLocation}`
}

onMounted(() => {
  fetchRecruitmentConfig()
  fetchList()
})
</script>

<style scoped>
.recruitment-hero-title {
  line-height: 1.22;
  padding-bottom: 2px;
  overflow: visible;
}

.section-title {
  line-height: 1.25;
  padding-top: 2px;
  padding-bottom: 2px;
}

.stat-card {
  min-height: 82px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}

.stat-card__label {
  line-height: 1.3;
}

.stat-card__value {
  line-height: 1.28;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.recruitment-page :deep(.el-upload) {
  width: 100%;
}

.recruitment-page :deep(.el-table th.el-table__cell) {
  background: #f8fafc;
  color: #334155;
}

.recruitment-page :deep(.el-table) {
  --el-table-border-color: #e2e8f0;
  --el-table-header-bg-color: #f8fafc;
  --el-table-row-hover-bg-color: #f8fbff;
}

.recruitment-page :deep(.el-table td.el-table__cell) {
  vertical-align: top;
}

.recruitment-page :deep(.el-table .cell) {
  line-height: 1.6;
}

.recruitment-page :deep(.el-tag) {
  border-radius: 999px;
  padding-inline: 10px;
}

.recruitment-page :deep(.el-dialog) {
  max-width: calc(100vw - 24px);
  border-radius: 26px;
  overflow: hidden;
}

.recruitment-page :deep(.el-dialog__body) {
  padding-top: 12px;
}

@media (max-width: 640px) {
  .recruitment-hero-title {
    line-height: 1.2;
  }

  .stat-card {
    min-height: 78px;
  }
}
</style>
