<template>
  <div class="recruitment-admin-page flex h-full flex-col gap-6">
    <section class="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] p-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.22)] sm:p-6 lg:p-7">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div class="min-w-0">
          <span class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">
            RECRUITMENT ADMIN
          </span>
          <h2 class="mt-3 text-2xl font-bold leading-[1.25] text-slate-800 sm:text-3xl">招新管理</h2>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base">
            管理招新报名活动名称、报名开始时间和报名结束时间。保存后会同步影响公开招新报名页面。
          </p>
        </div>

        <div
          class="status-card rounded-2xl border px-5 py-4"
          :class="form.is_active ? 'border-emerald-200 bg-emerald-50/75' : 'border-slate-200 bg-slate-50'"
        >
          <div class="text-xs font-semibold uppercase text-slate-400">报名入口</div>
          <div class="mt-2 text-lg font-bold" :class="form.is_active ? 'text-emerald-700' : 'text-slate-700'">
            {{ form.is_active ? '开放中' : '已关闭' }}
          </div>
        </div>
      </div>
    </section>

    <section class="grid min-h-0 flex-1 grid-cols-1 items-start gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
      <div class="rounded-[24px] border border-slate-200/90 bg-white p-5 shadow-[0_14px_36px_-30px_rgba(15,23,42,0.2)] sm:p-6 lg:p-7" v-loading="loading">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="admin-form">
          <el-form-item label="活动名称" prop="title">
            <el-input v-model="form.title" placeholder="请输入招新活动名称" />
          </el-form-item>

          <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <el-form-item label="报名开始时间" prop="start_time">
              <el-date-picker
                v-model="form.start_time"
                type="datetime"
                value-format="YYYY-MM-DDTHH:mm:ss"
                placeholder="选择报名开始时间"
                class="w-full"
              />
            </el-form-item>

            <el-form-item label="报名结束时间" prop="end_time">
              <el-date-picker
                v-model="form.end_time"
                type="datetime"
                value-format="YYYY-MM-DDTHH:mm:ss"
                placeholder="选择报名结束时间"
                class="w-full"
              />
            </el-form-item>
          </div>

          <el-form-item label="报名入口">
            <div class="switch-panel rounded-[20px] border border-slate-200 bg-slate-50 px-4 py-4 sm:px-5">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div class="min-w-0">
                  <div class="text-sm font-semibold text-slate-700">
                    {{ form.is_active ? '当前允许访问公开报名入口' : '当前公开报名入口已关闭' }}
                  </div>
                  <p class="mt-1 text-xs leading-5 text-slate-500">
                    开放时可访问并提交报名；关闭时公开报名表不会展示。
                  </p>
                </div>
                <el-switch v-model="form.is_active" active-text="开放" inactive-text="关闭" />
              </div>
            </div>
          </el-form-item>

          <div class="mt-5 flex flex-col gap-3 rounded-[20px] border border-dashed border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
            <div class="min-w-0">
              <div class="text-sm font-semibold text-slate-700">保存招新活动设置</div>
              <p class="mt-1 text-xs leading-5 text-slate-500">请确认活动名称和报名时间无误后保存。</p>
            </div>
            <el-button type="primary" class="!w-full sm:!w-auto" :loading="saving" @click="submitForm">
              保存设置
            </el-button>
          </div>
        </el-form>
      </div>

      <aside class="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.18)] sm:p-6">
        <div class="text-sm font-semibold text-slate-700">当前配置</div>
        <div class="mt-5 space-y-5">
          <div>
            <div class="text-xs font-semibold uppercase text-slate-400">活动名称</div>
            <div class="mt-1 break-words text-base font-semibold text-slate-800">{{ form.title || '未设置' }}</div>
          </div>
          <div>
            <div class="text-xs font-semibold uppercase text-slate-400">报名时间</div>
            <div class="mt-1 break-words text-sm leading-6 text-slate-600">{{ dateRangeText }}</div>
          </div>
          <div>
            <div class="text-xs font-semibold uppercase text-slate-400">入口状态</div>
            <div class="mt-1 text-base font-semibold" :class="form.is_active ? 'text-emerald-700' : 'text-slate-700'">
              {{ form.is_active ? '开放中' : '已关闭' }}
            </div>
          </div>
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

const loading = ref(false)
const saving = ref(false)
const formRef = ref(null)
const configId = ref(null)

const form = reactive({
  title: '',
  start_time: '',
  end_time: '',
  is_active: false
})

const rules = reactive({
  title: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
  start_time: [{ required: true, message: '请选择报名开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择报名结束时间', trigger: 'change' }]
})

const dateRangeText = computed(() => {
  if (!form.start_time || !form.end_time) {
    return '请先设置报名开始和结束时间'
  }

  return `${dayjs(form.start_time).format('YYYY-MM-DD HH:mm')} - ${dayjs(form.end_time).format('YYYY-MM-DD HH:mm')}`
})

const loadRecruitmentConfig = async () => {
  loading.value = true
  try {
    const res = await getAdminSignupConfigs({ category: 'recruitment' })
    const list = Array.isArray(res.data) ? res.data : []
    if (!list.length) {
      ElMessage.warning('未找到招新活动配置')
      return
    }

    const cfg = list[0]
    configId.value = cfg.id
    form.title = cfg.title || ''
    form.start_time = (cfg.start_time || '').slice(0, 19)
    form.end_time = (cfg.end_time || '').slice(0, 19)
    form.is_active = !!cfg.is_active
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '加载招新配置失败')
  } finally {
    loading.value = false
  }
}

const submitForm = async () => {
  if (!formRef.value || !configId.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  if (dayjs(form.start_time).isAfter(dayjs(form.end_time))) {
    ElMessage.error('报名结束时间必须晚于报名开始时间')
    return
  }

  saving.value = true
  try {
    await updateAdminSignupConfig(configId.value, {
      title: form.title,
      start_time: form.start_time,
      end_time: form.end_time,
      is_active: form.is_active
    })
    ElMessage.success('招新活动设置已保存')
    await loadRecruitmentConfig()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadRecruitmentConfig()
})
</script>

<style scoped>
.recruitment-admin-page {
  min-height: 100%;
}

.status-card,
.switch-panel {
  min-width: 0;
}

.status-card {
  min-height: 86px;
  width: min(100%, 260px);
}

.admin-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

@media (max-width: 1023px) {
  .status-card {
    width: 100%;
  }
}
</style>
