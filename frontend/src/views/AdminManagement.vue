<template>
  <div class="admin-management-page flex h-full flex-col gap-6">
    <section class="flex flex-col gap-5 pt-2 2xl:flex-row 2xl:items-start 2xl:justify-between">
      <div class="max-w-3xl">
        <span class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold tracking-[0.18em] text-blue-600">
          ACTIVITY CONTROL
        </span>
        <h2 class="mt-3 text-2xl font-bold leading-[1.2] text-slate-800 sm:text-3xl">后台管理</h2>
        <p class="mt-2 text-sm leading-6 text-slate-500 sm:text-base">
          统一维护招新、无线杯、电信杯三类活动的开放时间、当前阶段与报名状态，移动端和桌面端都能更清晰地查看与编辑。
        </p>
      </div>

      <div class="grid w-full grid-cols-1 gap-3 sm:grid-cols-3 2xl:w-[390px] 2xl:flex-none">
        <div class="rounded-2xl border border-slate-200 bg-white px-4 py-4 shadow-sm">
          <div class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">当前活动</div>
          <div class="mt-2 text-lg font-semibold text-slate-800">{{ selectedCategoryMeta.label }}</div>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white px-4 py-4 shadow-sm">
          <div class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">当前阶段</div>
          <div class="mt-2 text-lg font-semibold text-slate-800">{{ currentStageLabel }}</div>
        </div>
        <div
          class="rounded-2xl border px-4 py-4 shadow-sm"
          :class="form.is_active ? 'border-emerald-200 bg-emerald-50/70' : 'border-slate-200 bg-slate-50'"
        >
          <div class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">报名状态</div>
          <div class="mt-2 text-lg font-semibold" :class="form.is_active ? 'text-emerald-600' : 'text-slate-700'">
            {{ form.is_active ? '开放中' : '已关闭' }}
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,#f8fbff_0%,#f8fafc_100%)] p-5 shadow-[0_12px_34px_-28px_rgba(15,23,42,0.2)] sm:p-6">
      <div class="mb-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 class="text-sm font-semibold text-slate-700">活动分类切换</h3>
          <p class="text-xs leading-5 text-slate-500">小屏自动纵向堆叠，大屏保持分组切换，方便快速维护不同活动配置。</p>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
        <el-button
          v-for="item in categoryOptions"
          :key="item.value"
          :type="selectedCategory === item.value ? 'primary' : 'default'"
          class="category-button !ml-0 !h-auto !justify-start !rounded-[18px] !px-5 !py-4"
          @click="selectCategory(item.value)"
        >
          <div class="flex min-w-0 flex-col items-start text-left">
            <span class="text-sm font-semibold">{{ item.label }}</span>
            <span class="mt-1 text-xs opacity-70">
              {{ item.value === selectedCategory ? '当前正在编辑该活动配置' : '点击切换到该活动配置' }}
            </span>
          </div>
        </el-button>
      </div>
    </section>

    <section class="grid min-h-0 flex-1 grid-cols-1 items-start gap-6 2xl:grid-cols-[minmax(0,1.55fr)_300px]">
      <div class="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-6 shadow-[0_14px_36px_-28px_rgba(15,23,42,0.26)] sm:p-7" v-loading="loading">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="space-y-2">
          <div class="grid grid-cols-1 gap-5 xl:grid-cols-2">
            <el-form-item label="活动名称" prop="title" class="lg:col-span-2">
              <el-input v-model="form.title" placeholder="请输入活动名称" />
            </el-form-item>

            <el-form-item label="开放报名时间" prop="start_time">
              <el-date-picker
                v-model="form.start_time"
                type="datetime"
                class="w-full"
                value-format="YYYY-MM-DDTHH:mm:ss"
                placeholder="选择开放时间"
              />
            </el-form-item>

            <el-form-item label="截止报名时间" prop="end_time">
              <el-date-picker
                v-model="form.end_time"
                type="datetime"
                class="w-full"
                value-format="YYYY-MM-DDTHH:mm:ss"
                placeholder="选择截止时间"
              />
            </el-form-item>

            <el-form-item label="当前系统阶段" prop="current_stage">
              <el-select v-model="form.current_stage" class="w-full" placeholder="请选择当前阶段">
                <el-option label="报名阶段" value="registration" />
                <el-option label="第一轮面试" value="first_round" />
                <el-option label="第二轮面试" value="second_round" />
                <el-option label="已结束" value="ended" />
              </el-select>
            </el-form-item>

            <el-form-item label="报名开关">
              <div class="rounded-[20px] border border-slate-200 bg-slate-50 px-5 py-5">
                <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div class="text-sm font-semibold text-slate-700">
                      {{ form.is_active ? '当前允许提交报名' : '当前已关闭报名入口' }}
                    </div>
                    <div class="mt-1 text-xs leading-5 text-slate-500">
                      切换开关后，前台将根据状态展示或关闭对应活动的报名入口。
                    </div>
                  </div>
                  <el-switch v-model="form.is_active" active-text="开放" inactive-text="关闭" />
                </div>
              </div>
            </el-form-item>
          </div>

          <el-form-item label="活动描述">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="5"
              resize="none"
              placeholder="补充活动介绍、报名说明或当前阶段提示信息"
            />
          </el-form-item>

          <div class="flex flex-col gap-3 rounded-[20px] border border-dashed border-slate-200 bg-slate-50 p-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div class="text-sm font-semibold text-slate-700">保存当前配置</div>
              <p class="mt-1 text-xs leading-5 text-slate-500">
                修改会立即作用于当前活动分类，请在保存前确认时间与阶段设置无误。
              </p>
            </div>
            <el-button type="primary" class="!w-full sm:!w-auto" :loading="saving" @click="submitForm">
              保存配置
            </el-button>
          </div>
        </el-form>
      </div>

      <aside class="flex flex-col gap-5">
        <div class="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-6 shadow-[0_14px_36px_-28px_rgba(15,23,42,0.22)]">
          <div class="text-sm font-semibold text-slate-700">当前配置概览</div>
          <div class="mt-4 space-y-4">
            <div>
              <div class="text-xs uppercase tracking-[0.18em] text-slate-400">活动类型</div>
              <div class="mt-1 text-base font-semibold text-slate-800">{{ selectedCategoryMeta.label }}</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.18em] text-slate-400">阶段进度</div>
              <div class="mt-1 text-base font-semibold text-slate-800">{{ currentStageLabel }}</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.18em] text-slate-400">时间范围</div>
              <div class="mt-1 text-sm leading-6 text-slate-600">{{ dateRangeText }}</div>
            </div>
          </div>
        </div>

        <div class="rounded-[24px] border border-blue-100/90 bg-[linear-gradient(180deg,#eef6ff_0%,#eaf2ff_100%)] p-6 shadow-[0_14px_34px_-28px_rgba(59,130,246,0.28)]">
          <div class="text-sm font-semibold text-blue-700">使用建议</div>
          <ul class="mt-3 space-y-2 text-sm leading-6 text-blue-700/90">
            <li>报名阶段建议保持入口开启，并及时维护开放与截止时间。</li>
            <li>进入面试阶段后，可在前台提示中同步说明安排与通知方式。</li>
            <li>电脑端适合集中编辑，手机端适合快速查看和轻量修改。</li>
          </ul>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { getAdminSignupConfigs, updateAdminSignupConfig } from '@/api/recruitment'

const categoryOptions = [
  { label: '招新', value: 'recruitment' },
  { label: '无线杯', value: 'wireless_cup' },
  { label: '电信杯', value: 'telecom_cup' }
]

const stageLabelMap = {
  registration: '报名阶段',
  first_round: '第一轮面试',
  second_round: '第二轮面试',
  ended: '已结束'
}

const selectedCategory = ref('recruitment')
const loading = ref(false)
const saving = ref(false)
const formRef = ref(null)
const configId = ref(null)

const form = reactive({
  title: '',
  start_time: '',
  end_time: '',
  current_stage: 'registration',
  is_active: false,
  description: ''
})

const rules = reactive({
  title: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
  start_time: [{ required: true, message: '请选择开放时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择截止时间', trigger: 'change' }],
  current_stage: [{ required: true, message: '请选择系统阶段', trigger: 'change' }]
})

const selectedCategoryMeta = computed(() => {
  return categoryOptions.find((item) => item.value === selectedCategory.value) || categoryOptions[0]
})

const currentStageLabel = computed(() => {
  return stageLabelMap[form.current_stage] || '未设置'
})

const dateRangeText = computed(() => {
  if (!form.start_time || !form.end_time) {
    return '请先设置开放与截止时间'
  }

  return `${dayjs(form.start_time).format('YYYY-MM-DD HH:mm')} - ${dayjs(form.end_time).format('YYYY-MM-DD HH:mm')}`
})

const loadCategoryConfig = async () => {
  loading.value = true
  try {
    const res = await getAdminSignupConfigs({ category: selectedCategory.value })
    const list = Array.isArray(res.data) ? res.data : []
    if (!list.length) {
      ElMessage.warning('未找到该活动配置')
      return
    }

    const cfg = list[0]
    configId.value = cfg.id
    form.title = cfg.title || ''
    form.start_time = (cfg.start_time || '').slice(0, 19)
    form.end_time = (cfg.end_time || '').slice(0, 19)
    form.current_stage = cfg.current_stage || 'registration'
    form.is_active = !!cfg.is_active
    form.description = cfg.description || ''
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '加载配置失败')
  } finally {
    loading.value = false
  }
}

const selectCategory = (category) => {
  selectedCategory.value = category
  loadCategoryConfig()
}

const submitForm = async () => {
  if (!formRef.value || !configId.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  if (dayjs(form.start_time).isAfter(dayjs(form.end_time))) {
    ElMessage.error('截止时间必须晚于开放时间')
    return
  }

  saving.value = true
  try {
    await updateAdminSignupConfig(configId.value, {
      title: form.title,
      start_time: form.start_time,
      end_time: form.end_time,
      current_stage: form.current_stage,
      is_active: form.is_active,
      description: form.description || null
    })
    ElMessage.success('保存成功')
    await loadCategoryConfig()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadCategoryConfig()
})
</script>

<style scoped>
.admin-management-page {
  min-height: 100%;
}

.category-button :deep(.el-button__text) {
  width: 100%;
}

.category-button {
  box-shadow: 0 10px 24px -22px rgba(15, 23, 42, 0.24);
}

@media (max-width: 1279px) {
  .admin-management-page > section:last-child {
    height: auto;
  }
}
</style>
