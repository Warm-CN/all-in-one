<template>
  <div class="h-full">
    <div class="mb-5">
      <h2 class="text-2xl font-bold text-slate-800">后台管理</h2>
      <p class="mt-1 text-sm text-slate-500">固定管理招新、无线杯、电信杯三个活动。</p>
    </div>

    <div class="mb-4 flex flex-wrap gap-2 rounded-xl border border-slate-100 bg-slate-50 p-3">
      <el-button
        v-for="item in categoryOptions"
        :key="item.value"
        :type="selectedCategory === item.value ? 'primary' : 'default'"
        @click="selectCategory(item.value)"
      >
        {{ item.label }}
      </el-button>
    </div>

    <div class="rounded-xl border border-slate-100 bg-white p-5" v-loading="loading">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="活动名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入活动名称" />
        </el-form-item>

        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <el-form-item label="开放报名时间" prop="start_time">
            <el-date-picker v-model="form.start_time" type="datetime" class="w-full" value-format="YYYY-MM-DDTHH:mm:ss" />
          </el-form-item>
          <el-form-item label="截止报名时间" prop="end_time">
            <el-date-picker v-model="form.end_time" type="datetime" class="w-full" value-format="YYYY-MM-DDTHH:mm:ss" />
          </el-form-item>
        </div>

        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <el-form-item label="当前系统阶段" prop="current_stage">
            <el-select v-model="form.current_stage" class="w-full">
              <el-option label="报名阶段" value="registration" />
              <el-option label="第一轮面试" value="first_round" />
              <el-option label="第二轮面试" value="second_round" />
              <el-option label="已结束" value="ended" />
            </el-select>
          </el-form-item>
          <el-form-item label="报名开关">
            <el-switch v-model="form.is_active" active-text="开放" inactive-text="关闭" />
          </el-form-item>
        </div>

        <el-form-item label="活动描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>

        <div class="flex justify-end">
          <el-button type="primary" :loading="saving" @click="submitForm">保存配置</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { getAdminSignupConfigs, updateAdminSignupConfig } from '@/api/recruitment'

const categoryOptions = [
  { label: '招新', value: 'recruitment' },
  { label: '无线杯', value: 'wireless_cup' },
  { label: '电信杯', value: 'telecom_cup' }
]

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
