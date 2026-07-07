<template>
  <div class="apply-page min-h-screen w-full px-3 py-5 sm:px-6 lg:px-8 lg:py-10">
    <div class="apply-shell mx-auto flex w-full max-w-[1180px] flex-col gap-5 sm:gap-7">
      <header class="portal-hero grid w-full gap-5 rounded-[28px] border border-white/70 px-4 py-5 sm:px-6 sm:py-7 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-center lg:px-8 lg:py-8">
        <div class="min-w-0">
          <div class="flex flex-col items-center gap-3 text-center sm:flex-row sm:text-left">
            <img src="@/assets/images/logo.png" alt="Logo" class="h-16 w-auto shrink-0 object-contain sm:h-20" />
            <div class="min-w-0">
              <div class="inline-flex items-center rounded-full border border-cyan-200 bg-cyan-50 px-3 py-1 text-[11px] font-semibold uppercase text-cyan-700">
                RECRUITMENT PORTAL
              </div>
              <h1 class="mt-3 break-words text-3xl font-black leading-tight text-slate-950 sm:text-4xl lg:text-5xl">社团招新报名中心</h1>
            </div>
          </div>
          <p class="mx-auto mt-4 max-w-3xl text-center text-base leading-7 text-slate-600 sm:mx-0 sm:text-left sm:text-lg">
            报名、查询进度、查看面试安排与修改个人信息都在这里完成。
          </p>
        </div>

        <div class="hero-summary rounded-2xl border border-slate-200/80 bg-white/80 p-4 shadow-[0_16px_38px_-32px_rgba(15,23,42,0.35)]">
          <div class="text-xs font-semibold uppercase text-slate-400">当前状态</div>
          <div class="mt-3 text-lg font-black leading-6 text-slate-900">
            {{ activeConfig ? activeConfig.title : '等待活动开放' }}
          </div>
          <div class="mt-2 text-sm leading-6 text-slate-500">
            {{ activeConfig ? `截止：${formatDate(activeConfig.end_time)}` : '已报名同学可继续查询进度' }}
          </div>
        </div>
      </header>

      <section class="glass-card mx-auto w-full overflow-hidden rounded-[28px] border border-white/70">
        <div class="surface-header border-b border-slate-200/70 bg-white/75 p-3 sm:p-4">
          <div class="native-segment mx-auto grid max-w-xl grid-cols-1 rounded-2xl border border-slate-200/80 bg-slate-50 p-1 sm:grid-cols-2">
          <button
            class="tab-button rounded-xl px-3 py-3 text-center text-base font-semibold transition"
            :class="activeTab === 'apply' ? 'segment-active' : 'text-slate-500 hover:text-slate-800'"
            @click="activeTab = 'apply'"
          >
            我要报名
          </button>
          <button
            class="tab-button rounded-xl px-3 py-3 text-center text-base font-semibold transition"
            :class="activeTab === 'query' ? 'segment-active' : 'text-slate-500 hover:text-slate-800'"
            @click="activeTab = 'query'"
          >
            进度查询
          </button>
          </div>
        </div>

        <div class="p-4 sm:p-6 lg:p-8">
          <div v-show="activeTab === 'apply'">
            <div v-if="loadingConfigs" class="py-16 text-center text-slate-500">
              <el-icon class="is-loading text-3xl"><Loading /></el-icon>
              <p class="mt-3">正在加载可报名活动...</p>
            </div>

            <div v-else-if="!activeConfig" class="empty-panel rounded-2xl border border-dashed border-slate-300 bg-white/75 p-6 text-center sm:p-8">
              <h3 class="text-xl font-semibold text-slate-800">当前暂无开放的招新活动</h3>
              <p class="mt-2 text-slate-500">如果你已提交过报名，仍然可以通过进度查询查看审核与面试信息。</p>
              <div class="mt-5 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                <el-button type="primary" size="large" class="!w-full sm:!w-auto" @click="activeTab = 'query'">去进度查询</el-button>
              </div>
            </div>

            <el-form v-else ref="formRef" :model="form" :rules="rules" label-position="top" size="large" class="native-form">
              <div class="status-strip mb-5 rounded-2xl border border-sky-100 bg-sky-50/90 p-4 text-sm leading-6 text-sky-900 sm:p-5">
                <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div class="min-w-0">
                    <div class="text-xs font-semibold uppercase text-sky-600">正在报名</div>
                    <div class="mt-1 break-words text-base font-bold text-sky-950">{{ activeConfig.title }}</div>
                  </div>
                  <div class="rounded-xl bg-white/85 px-3 py-2 text-xs font-semibold text-sky-700">截止：{{ formatDate(activeConfig.end_time) }}</div>
                </div>
              </div>

              <div class="form-section">
                <div class="section-kicker">基础信息</div>
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
              </div>

              <div class="form-section mt-4">
                <div class="section-kicker">志愿选择</div>
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
                  <el-radio-group v-model="form.adjust" class="mobile-radio-group">
                    <el-radio label="是">是，服从调剂</el-radio>
                    <el-radio label="否">否，仅考虑以上志愿</el-radio>
                  </el-radio-group>
                </el-form-item>
              </div>

              <div class="form-section mt-4">
                <div class="section-kicker">个人介绍</div>
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
              </div>

              <el-button type="primary" class="mt-5 h-12 w-full rounded-xl text-base font-semibold" :loading="submitting" @click="submitForm">
                提交报名
              </el-button>
            </el-form>
          </div>

          <div v-show="activeTab === 'query'" class="mx-auto w-full max-w-[880px]">
            <div class="query-panel rounded-[26px] border border-cyan-100/80 bg-[linear-gradient(180deg,#f3fbff_0%,#fafdff_100%)] p-5 shadow-[0_16px_34px_-32px_rgba(8,145,178,0.42)] sm:p-6">
              <div class="text-center sm:text-left">
                <div class="flex justify-center sm:justify-start">
                  <div class="inline-flex items-center rounded-full bg-white/85 px-3 py-1 text-[11px] font-semibold uppercase text-cyan-700">
                    QUERY CENTER
                  </div>
                </div>
                <h3 class="mt-3 text-2xl font-black text-slate-900">查询进度与修改入口</h3>
                <p class="mx-auto mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                    输入报名时使用的学号和手机号即可查看当前进度、面试安排。查询成功后，若记录仍允许调整，结果卡片里会直接显示“修改报名信息”按钮。
                </p>
              </div>

              <el-form ref="queryFormRef" :model="queryForm" :rules="queryRules" label-position="top" size="large" class="native-form mt-6">
                <div class="form-section rounded-[24px] border border-slate-200/80 bg-white/92 p-4 shadow-[0_10px_30px_-30px_rgba(15,23,42,0.28)] sm:p-5">
                  <div class="grid grid-cols-1 gap-3 md:grid-cols-2 md:gap-4">
                    <el-form-item label="学号" prop="student_id">
                      <el-input v-model="queryForm.student_id" placeholder="请输入学号" />
                    </el-form-item>
                    <el-form-item label="手机号" prop="phone">
                      <el-input v-model="queryForm.phone" placeholder="请输入手机号" />
                    </el-form-item>
                  </div>
                  <div class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div class="text-sm leading-6 text-slate-500">
                      查询后会显示当前状态、面试安排以及是否可修改。
                    </div>
                    <el-button type="primary" class="!h-12 !w-full !rounded-2xl !px-6 text-base font-semibold sm:!w-auto" :loading="querying" @click="handleQuery">
                      查询我的报名进度
                    </el-button>
                  </div>
                </div>
              </el-form>
            </div>

            <div v-if="queryResults.length > 0" class="mt-7 space-y-5">
              <div v-for="item in queryResults" :key="item.id" class="query-result-card rounded-[24px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-4 shadow-[0_16px_40px_-32px_rgba(15,23,42,0.18)] sm:p-6">
                <div class="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_220px] xl:items-start">
                  <div class="min-w-0 text-left">
                    <div class="flex flex-wrap items-center gap-2">
                      <span class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-[11px] font-semibold uppercase text-slate-500">
                        APPLICATION
                      </span>
                      <el-tag :type="statusTagType(item.status)" effect="dark" class="w-fit">{{ item.status_desc }}</el-tag>
                    </div>
                    <h3 class="mt-3 text-xl font-black leading-[1.2] text-slate-900">{{ item.activity_title }}</h3>
                    <p class="mt-2 text-sm text-slate-500">提交时间：{{ formatDate(item.submitted_at) }}</p>
                  </div>

                  <div class="flex w-full flex-col gap-2 xl:items-stretch">
                    <el-button
                      v-if="canEdit(item)"
                      type="primary"
                      class="!h-11 !w-full !rounded-2xl !px-5 font-semibold"
                      @click="openEditDialog(item)"
                    >
                      修改报名信息
                    </el-button>
                    <div class="rounded-2xl border px-4 py-3 text-sm leading-6" :class="canEdit(item) ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-slate-200 bg-slate-50 text-slate-500'">
                      {{ getEditHint(item) }}
                    </div>
                  </div>
                </div>

                <div class="mt-5 grid grid-cols-1 gap-3 lg:grid-cols-3">
                  <div class="rounded-2xl border border-slate-200/70 bg-white/90 px-4 py-4 shadow-[0_10px_26px_-32px_rgba(15,23,42,0.2)]">
                    <div class="text-[11px] font-semibold uppercase text-slate-400">第一志愿</div>
                    <div class="mt-2 text-base font-semibold leading-6 text-slate-800">{{ displayFormValue(item, '第一志愿') }}</div>
                  </div>
                  <div class="rounded-2xl border border-slate-200/70 bg-white/90 px-4 py-4 shadow-[0_10px_26px_-32px_rgba(15,23,42,0.2)]">
                    <div class="text-[11px] font-semibold uppercase text-slate-400">第二志愿</div>
                    <div class="mt-2 text-base font-semibold leading-6 text-slate-800">{{ displayFormValue(item, '第二志愿') }}</div>
                  </div>
                  <div class="rounded-2xl border border-slate-200/70 bg-white/90 px-4 py-4 shadow-[0_10px_26px_-32px_rgba(15,23,42,0.2)]">
                    <div class="text-[11px] font-semibold uppercase text-slate-400">服从调剂</div>
                    <div class="mt-2 text-base font-semibold leading-6 text-slate-800">{{ displayFormValue(item, '服从调剂') }}</div>
                  </div>
                </div>

                <div class="mt-5">
                  <div class="mb-3 text-xs font-semibold uppercase text-slate-400">面试安排</div>
                  <div class="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
                    <div class="rounded-[22px] border border-slate-200/70 bg-slate-50/85 p-4">
                      <div class="text-sm font-semibold text-slate-700">一面</div>
                      <div class="mt-2 leading-7 text-slate-900">时间：{{ item.first_choice_interview_time ? formatDate(item.first_choice_interview_time) : '待通知' }}</div>
                      <div class="leading-7 text-slate-900">地点：{{ item.first_choice_interview_location || '待通知' }}</div>
                    </div>
                    <div class="rounded-[22px] border border-slate-200/70 bg-slate-50/85 p-4">
                      <div class="text-sm font-semibold text-slate-700">二面</div>
                      <div class="mt-2 leading-7 text-slate-900">部门：{{ item.second_round_department || '待通知' }}</div>
                      <div class="mt-2 leading-7 text-slate-900">时间：{{ item.second_round_interview_time ? formatDate(item.second_round_interview_time) : '待通知' }}</div>
                      <div class="leading-7 text-slate-900">地点：{{ item.second_round_interview_location || '待通知' }}</div>
                    </div>
                  </div>
                </div>

                <div class="mt-5">
                  <div class="mb-3 text-xs font-semibold uppercase text-slate-400">通知信息</div>
                  <div class="rounded-[22px] border border-slate-200/70 bg-[linear-gradient(180deg,#f8fafc_0%,#f8fbff_100%)] p-4 text-sm text-slate-700">
                    <div class="whitespace-pre-wrap leading-7">{{ item.notes }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else-if="hasQueried" class="mt-7 rounded-[24px] border border-dashed border-slate-300 bg-white/70 p-8 text-center text-slate-500">
              未找到报名记录，请检查学号和手机号是否与报名时一致。
            </div>
          </div>
        </div>
      </section>
    </div>

    <el-dialog v-model="editVisible" title="修改报名信息" width="min(680px, calc(100vw - 24px))" destroy-on-close>
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
          <el-radio-group v-model="editForm.adjust" class="mobile-radio-group">
            <el-radio label="是">是，服从调剂</el-radio>
            <el-radio label="否">否，仅考虑以上志愿</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="自我介绍" prop="intro">
          <el-input v-model="editForm.intro" type="textarea" :rows="4" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="editVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingEdit" @click="submitEdit">保存修改</el-button>
        </div>
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
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '获取招新活动失败')
  } finally {
    loadingConfigs.value = false
  }
})

const submitForm = async () => {
  if (!formRef.value || !activeConfig.value) return

  if (activeConfig.value.can_submit === false) {
    ElMessage.warning('当前报名入口未开放。')
    return
  }

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

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

const displayFormValue = (item, key) => {
  const value = item?.form_data?.[key]
  if (!value || value === '无') return '未填写'
  return value
}

const canEdit = (item) => item?.status === 'submitted'

const getEditHint = (item) => {
  if (canEdit(item)) {
    return '当前记录仍可在线修改，更新后会立即覆盖你原来的报名信息。'
  }
  return '当前记录已锁定，若确需调整，请联系管理员协助处理。'
}

const statusTagType = (status) => {
  if (status === 'accepted') return 'success'
  if (status === 'rejected') return 'danger'
  if (status === 'second_round') return 'warning'
  return 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const parsed = dayjs(dateStr)
  if (!parsed.isValid()) return String(dateStr)
  return parsed.format('YYYY-MM-DD HH:mm')
}
</script>

<style scoped>
.apply-page {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  background:
    linear-gradient(135deg, #eef7ff 0%, #f8fafc 46%, #edfdf8 100%);
}

.portal-hero {
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(240, 249, 255, 0.9) 58%, rgba(236, 253, 245, 0.86) 100%);
  box-shadow: 0 24px 58px -44px rgba(15, 23, 42, 0.45);
}

.portal-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(14, 165, 233, 0.09), transparent 36%, rgba(16, 185, 129, 0.08));
  pointer-events: none;
}

.portal-hero > * {
  position: relative;
  z-index: 1;
}

.glass-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 250, 252, 0.92) 100%);
  box-shadow: 0 22px 66px -44px rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(8px);
}

.surface-header {
  backdrop-filter: blur(8px);
}

.tab-button {
  min-height: 48px;
  line-height: 1.25;
}

.segment-active {
  background: linear-gradient(180deg, #ffffff 0%, #f0f7ff 100%);
  color: #0369a1;
  box-shadow: 0 6px 14px rgba(2, 132, 199, 0.15), 0 0 0 1px rgba(2, 132, 199, 0.15) inset;
}

.form-section,
.query-panel,
.empty-panel {
  min-width: 0;
}

.form-section {
  border: 1px solid rgba(226, 232, 240, 0.84);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.74);
  padding: 18px;
}

.section-kicker {
  margin-bottom: 14px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.status-strip {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.query-result-card {
  overflow: hidden;
}

:deep(.native-form .el-form-item) {
  margin-bottom: 18px;
}

:deep(.native-form .el-form-item:last-child) {
  margin-bottom: 0;
}

:deep(.el-dialog) {
  max-width: calc(100vw - 24px);
}

@media (max-width: 640px) {
  .apply-page {
    padding-left: 12px;
    padding-right: 12px;
  }

  .portal-hero {
    border-radius: 22px;
  }

  .hero-summary,
  .form-section {
    padding: 14px;
  }

  .glass-card {
    border-radius: 22px;
    box-shadow: 0 18px 42px -32px rgba(15, 23, 42, 0.38);
  }

  .tab-button {
    min-height: 44px;
  }
}
</style>
