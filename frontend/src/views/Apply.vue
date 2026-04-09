<template>
  <div class="apply-page min-h-screen w-full px-4 py-6 sm:px-6 lg:px-8">
    <div class="mx-auto my-auto w-full max-w-5xl">
      <div class="mb-8 text-center sm:mb-10">
        <img src="@/assets/images/logo.png" alt="Logo" class="mx-auto h-20 w-auto object-contain sm:h-24" />
        <h1 class="mt-4 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl md:text-5xl">协会招新报名通道</h1>
        <p class="mt-3 text-lg leading-relaxed text-slate-600">报名、查询、查看面试安排都在这里完成</p>
      </div>

      <section class="glass-card mx-auto w-full max-w-3xl overflow-hidden rounded-3xl border border-white/50">
        <div class="bg-white/70 p-3 sm:p-4">
          <div class="native-segment mx-auto flex max-w-xl rounded-2xl border border-slate-200/80 bg-slate-50 p-1">
          <button
            class="flex-1 rounded-xl py-3 text-center text-lg font-semibold transition"
            :class="activeTab === 'apply' ? 'segment-active' : 'text-slate-500 hover:text-slate-800'"
            @click="activeTab = 'apply'"
          >
            我要报名
          </button>
          <button
            class="flex-1 rounded-xl py-3 text-center text-lg font-semibold transition"
            :class="activeTab === 'query' ? 'segment-active' : 'text-slate-500 hover:text-slate-800'"
            @click="activeTab = 'query'"
          >
            进度查询
          </button>
          </div>
        </div>

        <div class="p-5 sm:p-9">
          <div v-show="activeTab === 'apply'">
            <div v-if="loadingConfigs" class="py-16 text-center text-slate-500">
              <el-icon class="is-loading text-3xl"><Loading /></el-icon>
              <p class="mt-3">正在加载可报名活动...</p>
            </div>

            <div v-else-if="!activeConfig" class="rounded-2xl border border-dashed border-slate-300 bg-white/60 p-8 text-center">
              <h3 class="text-xl font-semibold text-slate-800">当前暂无开放的招新活动</h3>
              <p class="mt-2 text-slate-500">如果你已提交过报名，仍然可以通过进度查询查看审核与面试信息。</p>
              <div class="mt-5 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                <el-button type="primary" size="large" @click="activeTab = 'query'">去进度查询</el-button>
                <el-button plain size="large" @click="enablePreviewMode">预览报名页效果</el-button>
              </div>
            </div>

            <el-form v-else ref="formRef" :model="form" :rules="rules" label-position="top" size="large" class="native-form">
              <div class="mb-5 rounded-xl border border-sky-100 bg-sky-50 p-4 text-sm text-sky-900">
                当前活动：<span class="font-bold">{{ activeConfig.title }}</span>
                <div class="mt-1 text-xs text-sky-700">报名截止：{{ formatDate(activeConfig.end_time) }}</div>
                <div v-if="previewMode" class="mt-2 text-xs font-semibold text-amber-700">
                  当前为前端预览模式，仅用于展示页面效果，不会提交真实报名数据。
                </div>
              </div>

              <div class="grid grid-cols-1 gap-x-4 gap-y-1 md:grid-cols-2">
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="form.name" placeholder="请输入真实姓名" />
                </el-form-item>
                <el-form-item label="学号" prop="student_id">
                  <el-input v-model="form.student_id" placeholder="请输入学号" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="form.phone" placeholder="请输入手机号" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="form.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="学院" prop="college">
                  <el-input v-model="form.college" placeholder="请输入所在学院" />
                </el-form-item>
                <el-form-item label="专业班级" prop="major">
                  <el-input v-model="form.major" placeholder="如：信息工程1班" />
                </el-form-item>
              </div>

              <el-divider content-position="left">志愿选择</el-divider>
              <div class="grid grid-cols-1 gap-x-4 gap-y-1 md:grid-cols-2">
                <el-form-item label="第一志愿" prop="first_choice">
                  <el-select v-model="form.first_choice" placeholder="请选择第一志愿" class="w-full">
                    <el-option v-for="dept in departmentOptions" :key="dept" :label="dept" :value="dept" />
                  </el-select>
                </el-form-item>
                <el-form-item label="第二志愿" prop="second_choice">
                  <el-select v-model="form.second_choice" placeholder="请选择第二志愿（可选）" clearable class="w-full">
                    <el-option
                      v-for="dept in departmentOptions"
                      :key="dept"
                      :label="dept"
                      :value="dept"
                      :disabled="dept === form.first_choice"
                    />
                  </el-select>
                </el-form-item>
              </div>

              <el-form-item label="是否服从调剂" prop="adjust">
                <el-radio-group v-model="form.adjust">
                  <el-radio label="是">是，服从调剂</el-radio>
                  <el-radio label="否">否，仅考虑以上志愿</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="自我介绍" prop="intro">
                <el-input
                  v-model="form.intro"
                  type="textarea"
                  :rows="4"
                  maxlength="500"
                  show-word-limit
                  placeholder="请简单介绍你的经历、兴趣与擅长方向"
                />
              </el-form-item>

              <el-button type="primary" class="h-12 w-full rounded-xl text-base font-semibold" :loading="submitting" @click="submitForm">
                提交报名
              </el-button>
            </el-form>
          </div>

          <div v-show="activeTab === 'query'">
            <div class="mb-6 rounded-xl border border-cyan-100 bg-cyan-50 p-4 text-sm text-cyan-900">
              输入报名时的学号和手机号，即可查看筛选进度、面试时间和地点。
            </div>

            <el-form ref="queryFormRef" :model="queryForm" :rules="queryRules" label-position="top" size="large" class="native-form">
              <div class="grid grid-cols-1 gap-2 md:grid-cols-2 md:gap-4">
                <el-form-item label="学号" prop="student_id">
                  <el-input v-model="queryForm.student_id" placeholder="请输入学号" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="queryForm.phone" placeholder="请输入手机号" />
                </el-form-item>
              </div>
              <el-button type="primary" class="mt-1 h-12 w-full rounded-xl text-base font-semibold" :loading="querying" @click="handleQuery">
                查询我的报名进度
              </el-button>
            </el-form>

            <div v-if="queryResults.length > 0" class="mt-7 space-y-4 border-t border-slate-100 pt-6">
              <div v-for="item in queryResults" :key="item.id" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <div class="mb-2 flex items-start justify-between gap-3">
                  <div>
                    <h3 class="text-lg font-bold text-slate-900">{{ item.activity_title }}</h3>
                    <p class="text-xs text-slate-500">提交时间：{{ formatDate(item.submitted_at) }}</p>
                  </div>
                  <el-tag :type="statusTagType(item.current_stage)" effect="dark">{{ item.status_desc }}</el-tag>
                </div>

                <div v-if="item.current_stage === 'first_round'" class="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
                  <div class="rounded-lg bg-slate-50 p-3">
                    <div class="font-semibold text-slate-700">一面-第一志愿</div>
                    <div class="mt-1 text-slate-900">时间：{{ item.first_choice_interview_time ? formatDate(item.first_choice_interview_time) : '待通知' }}</div>
                    <div class="mt-1 text-slate-900">地点：{{ item.first_choice_interview_location || '待通知' }}</div>
                  </div>
                  <div class="rounded-lg bg-slate-50 p-3">
                    <div class="font-semibold text-slate-700">一面-第二志愿</div>
                    <div class="mt-1 text-slate-900">时间：{{ item.second_choice_interview_time ? formatDate(item.second_choice_interview_time) : '待通知' }}</div>
                    <div class="mt-1 text-slate-900">地点：{{ item.second_choice_interview_location || '待通知' }}</div>
                  </div>
                </div>

                <div v-else-if="item.current_stage === 'second_round'" class="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
                  <div class="rounded-lg bg-slate-50 p-3">
                    <div class="font-semibold text-slate-700">二面志愿</div>
                    <div class="mt-1 text-slate-900">{{ item.second_round_department || '待通知' }}</div>
                  </div>
                  <div class="rounded-lg bg-slate-50 p-3">
                    <div class="font-semibold text-slate-700">二面安排</div>
                    <div class="mt-1 text-slate-900">时间：{{ item.second_round_interview_time ? formatDate(item.second_round_interview_time) : '待通知' }}</div>
                    <div class="mt-1 text-slate-900">地点：{{ item.second_round_interview_location || '待通知' }}</div>
                  </div>
                </div>

                <div v-else class="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
                  当前结果：<span class="font-semibold text-slate-900">{{ item.status_desc }}</span>
                </div>

                <div class="mt-3 rounded-lg border border-slate-100 bg-slate-50 p-3 text-sm text-slate-700">
                  <div class="font-semibold text-slate-800">通知信息</div>
                  <div class="mt-1 whitespace-pre-wrap">{{ item.notes }}</div>
                </div>

                <div class="mt-4 flex justify-end" v-if="canEdit(item.status)">
                  <el-button type="primary" plain @click="openEditDialog(item)">修改报名信息</el-button>
                </div>
              </div>
            </div>

            <div v-else-if="hasQueried" class="mt-7 rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-500">
              未找到报名记录，请检查学号和手机号是否与报名时一致。
            </div>
          </div>
        </div>
      </section>
    </div>

    <el-dialog v-model="editVisible" title="修改报名信息" width="680px" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" :rules="rules" label-position="top" size="large">
        <div class="grid grid-cols-1 gap-x-4 gap-y-1 md:grid-cols-2">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="editForm.name" />
          </el-form-item>
          <el-form-item label="学号" prop="student_id">
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
            <el-select v-model="editForm.first_choice" class="w-full">
              <el-option v-for="dept in departmentOptions" :key="dept" :label="dept" :value="dept" />
            </el-select>
          </el-form-item>
          <el-form-item label="第二志愿" prop="second_choice">
            <el-select v-model="editForm.second_choice" clearable class="w-full">
              <el-option
                v-for="dept in departmentOptions"
                :key="dept"
                :label="dept"
                :value="dept"
                :disabled="dept === editForm.first_choice"
              />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="是否服从调剂" prop="adjust">
          <el-radio-group v-model="editForm.adjust">
            <el-radio label="是">是，服从调剂</el-radio>
            <el-radio label="否">否，仅考虑以上志愿</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="自我介绍" prop="intro">
          <el-input v-model="editForm.intro" type="textarea" :rows="4" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingEdit" @click="submitEdit">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { getActiveConfigs, queryStatus, submitApply, updateApply } from '@/api/recruitment'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()

const activeTab = ref('apply')
const loadingConfigs = ref(true)
const submitting = ref(false)
const querying = ref(false)
const hasQueried = ref(false)
const activeConfig = ref(null)
const previewMode = ref(false)
const queryResults = ref([])

const formRef = ref(null)
const queryFormRef = ref(null)
const editFormRef = ref(null)

const editVisible = ref(false)
const savingEdit = ref(false)
const editingId = ref(null)

const departmentOptions = ['科创部', '新媒体运营部','外联部',  '宣传部', '组织部']

const form = reactive({
  name: '',
  student_id: '',
  phone: '',
  email: '',
  college: '',
  major: '',
  first_choice: '',
  second_choice: '',
  adjust: '',
  intro: ''
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
  intro: ''
})

const queryForm = reactive({
  student_id: '',
  phone: ''
})

const rules = reactive({
  name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  student_id: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { pattern: /^[0-9A-Za-z]+$/, message: '学号格式不正确', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  college: [{ required: true, message: '请输入学院', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业班级', trigger: 'blur' }],
  first_choice: [{ required: true, message: '请选择第一志愿', trigger: 'change' }],
  adjust: [{ required: true, message: '请选择是否服从调剂', trigger: 'change' }]
})

const queryRules = reactive({
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }]
})

onMounted(async () => {
  if (route.query.tab === 'query') {
    activeTab.value = 'query'
  }

  try {
    const res = await getActiveConfigs({ category: 'recruitment' })
    if (Array.isArray(res.data) && res.data.length > 0) {
      activeConfig.value = res.data[0]
    } else if (import.meta.env.DEV) {
      enablePreviewMode()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '获取招新活动失败')
    if (import.meta.env.DEV) {
      enablePreviewMode()
    }
  } finally {
    loadingConfigs.value = false
  }
})

const enablePreviewMode = () => {
  previewMode.value = true
  activeConfig.value = {
    id: null,
    title: '2026 春季招新（预览）',
    end_time: dayjs().add(15, 'day').toISOString()
  }
}

const submitForm = async () => {
  if (!formRef.value || !activeConfig.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  if (previewMode.value) {
    ElMessage.success('前端预览模式下不提交后端，你可以继续体验页面布局与交互。')
    activeTab.value = 'query'
    return
  }

  submitting.value = true
  try {
    await submitApply({
      signup_config_id: activeConfig.value.id,
      student_id: form.student_id,
      form_data: toFormData(form)
    })

    ElMessage.success('报名成功，请保存好学号和手机号用于查询')
    router.push({ path: '/apply/success', query: { tab: 'query' } })
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '报名失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}

const handleQuery = async () => {
  if (!queryFormRef.value) return
  const valid = await queryFormRef.value.validate().catch(() => false)
  if (!valid) return

  querying.value = true
  hasQueried.value = false
  queryResults.value = []

  try {
    const res = await queryStatus(queryForm)
    queryResults.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    if (error?.response?.status !== 404) {
      ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '查询失败')
    }
  } finally {
    hasQueried.value = true
    querying.value = false
  }
}

const openEditDialog = (record) => {
  const data = record.form_data || {}
  editingId.value = record.id

  editForm.name = data['姓名'] || ''
  editForm.student_id = queryForm.student_id || ''
  editForm.phone = data['手机号'] || queryForm.phone || ''
  editForm.email = data['邮箱'] || ''
  editForm.college = data['学院'] || ''
  editForm.major = data['专业班级'] || ''
  editForm.first_choice = data['第一志愿'] || ''
  editForm.second_choice = data['第二志愿'] === '无' ? '' : (data['第二志愿'] || '')
  editForm.adjust = data['服从调剂'] || ''
  editForm.intro = data['自我介绍'] || ''

  editVisible.value = true
}

const submitEdit = async () => {
  if (!editFormRef.value || !editingId.value) return
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return

  savingEdit.value = true
  try {
    await updateApply(editingId.value, { form_data: toFormData(editForm) })
    ElMessage.success('报名信息已更新')
    editVisible.value = false
    await handleQuery()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '修改失败')
  } finally {
    savingEdit.value = false
  }
}

const toFormData = (source) => ({
  姓名: source.name,
  手机号: source.phone,
  邮箱: source.email,
  学院: source.college,
  专业班级: source.major,
  第一志愿: source.first_choice,
  第二志愿: source.second_choice || '无',
  服从调剂: source.adjust,
  自我介绍: source.intro
})

const canEdit = (status) => status === 'submitted'

const statusTagType = (status) => {
  if (status === 'accepted') return 'success'
  if (status === 'rejected') return 'danger'
  if (status === 'second_round') return 'warning'
  return 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}
</script>

<style scoped>
.apply-page {
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 10% 20%, #dff5ff 0%, transparent 40%),
    radial-gradient(circle at 90% 10%, #e7fff4 0%, transparent 35%),
    linear-gradient(180deg, #f6f8fb 0%, #f3f6fb 100%);
}

.glass-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92) 0%, rgba(255, 255, 255, 0.88) 100%);
  box-shadow: 0 18px 60px rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(8px);
}

.segment-active {
  background: linear-gradient(180deg, #ffffff 0%, #f0f7ff 100%);
  color: #0369a1;
  box-shadow: 0 6px 14px rgba(2, 132, 199, 0.15), 0 0 0 1px rgba(2, 132, 199, 0.15) inset;
}

:deep(.native-form .el-form-item) {
  margin-bottom: 18px;
}

@media (max-width: 640px) {
  .glass-card {
    border-radius: 24px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.16);
  }
}
</style>
