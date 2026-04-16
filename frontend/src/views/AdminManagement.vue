<template>
  <div class="admin-management-page flex h-full min-h-0 flex-col gap-6">
    <section class="flex flex-col gap-5 pt-2 2xl:flex-row 2xl:items-start 2xl:justify-between">
      <div class="max-w-3xl">
        <span class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold tracking-[0.18em] text-blue-600">
          ACTIVITY CONTROL
        </span>
        <h2 class="mt-3 text-2xl font-bold leading-[1.2] text-slate-800 sm:text-3xl">后台管理</h2>
        <p class="mt-2 text-sm leading-6 text-slate-500 sm:text-base">
          统一管理无线杯、电信杯比赛历史；可设置当前“正在比赛”，并进入竞赛后台管理。
        </p>
      </div>

      <div class="grid w-full grid-cols-1 gap-3 sm:grid-cols-3 2xl:w-[390px] 2xl:flex-none">
        <div class="rounded-2xl border border-slate-200 bg-white px-4 py-4 shadow-sm">
          <div class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">当前活动</div>
          <div class="mt-2 text-lg font-semibold text-slate-800">{{ selectedCategoryMeta.label }}</div>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white px-4 py-4 shadow-sm">
          <div class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">历史比赛数</div>
          <div class="mt-2 text-lg font-semibold text-slate-800">{{ competitionEvents.length }}</div>
        </div>
        <div
          class="rounded-2xl border px-4 py-4 shadow-sm"
          :class="activeEvent ? 'border-emerald-200 bg-emerald-50/70' : 'border-slate-200 bg-slate-50'"
        >
          <div class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">当前状态</div>
          <div class="mt-2 text-lg font-semibold" :class="activeEvent ? 'text-emerald-600' : 'text-slate-700'">
            {{ activeEvent ? '存在进行中比赛' : '暂无进行中比赛' }}
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,#f8fbff_0%,#f8fafc_100%)] p-5 shadow-[0_12px_34px_-28px_rgba(15,23,42,0.2)] sm:p-6">
      <div class="mb-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 class="text-sm font-semibold text-slate-700">活动分类切换</h3>
          <p class="text-xs leading-5 text-slate-500">选择无线杯或电信杯查看历史赛事并进入竞赛后台管理。</p>
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
              {{ item.value === selectedCategory ? '当前正在查看' : '点击切换' }}
            </span>
          </div>
        </el-button>
      </div>
    </section>

    <section
      class="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.18)] sm:p-6"
      v-loading="eventsLoading"
    >
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-800">比赛历史（{{ selectedCategoryMeta.label }}）</h3>
        <el-button class="!rounded-xl" @click="fetchCompetitionEvents">刷新</el-button>
      </div>

      <el-alert
        v-if="!isCompetitionCategory"
        type="info"
        :closable="false"
        title="招新不在此页面维护比赛历史，请切换到无线杯或电信杯。"
      />

      <div v-else-if="!competitionEvents.length && !eventsLoading" class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
        暂无比赛历史，请先在赛事中心创建比赛。
      </div>

      <div v-else class="history-scroll max-h-[62vh] overflow-y-auto pr-1">
        <div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
          <article v-for="item in competitionEvents" :key="item.id" class="rounded-2xl border border-slate-200/80 bg-white/95 p-4 shadow-[0_10px_24px_-24px_rgba(15,23,42,0.4)]">
            <div class="flex items-start justify-between gap-3">
              <div>
                <h4 class="text-base font-semibold text-slate-900">{{ item.name }}</h4>
                <p class="mt-1 text-xs text-slate-500">报名页标题：{{ item.display_title }}</p>
                <p class="mt-1 text-xs text-slate-500">模块标识：{{ item.module_key }}</p>
              </div>
              <el-tag :type="item.is_current ? 'success' : 'info'">{{ item.is_current ? '正在比赛' : '已结束' }}</el-tag>
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

            <div class="mt-4 flex flex-wrap gap-2">
              <el-button type="primary" class="!rounded-xl" @click="goContestAdmin(item)">竞赛后台管理</el-button>
              <el-button class="!rounded-xl" :loading="activatingId === item.id" @click="toggleActive(item)">
                {{ item.is_current ? '设为已结束' : '设为正在比赛' }}
              </el-button>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getCompetitionEvents, updateCompetitionActiveState } from '@/api/competition'

const router = useRouter()

const categoryOptions = [
  { label: '招新', value: 'recruitment' },
  { label: '无线杯', value: 'wireless_cup' },
  { label: '电信杯', value: 'telecom_cup' }
]

const selectedCategory = ref('wireless_cup')
const eventsLoading = ref(false)
const activatingId = ref(null)
const competitionEvents = ref([])

const selectedCategoryMeta = computed(() => {
  return categoryOptions.find((item) => item.value === selectedCategory.value) || categoryOptions[0]
})

const isCompetitionCategory = computed(() => {
  return selectedCategory.value === 'wireless_cup' || selectedCategory.value === 'telecom_cup'
})

const competitionCupType = computed(() => {
  if (selectedCategory.value === 'wireless_cup') return 'wireless'
  if (selectedCategory.value === 'telecom_cup') return 'telecom'
  return ''
})

const activeEvent = computed(() => competitionEvents.value.find((item) => item.is_current) || null)

const fetchCompetitionEvents = async () => {
  if (!isCompetitionCategory.value || !competitionCupType.value) {
    competitionEvents.value = []
    return
  }

  eventsLoading.value = true
  try {
    const res = await getCompetitionEvents(competitionCupType.value)
    competitionEvents.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '获取比赛历史失败')
  } finally {
    eventsLoading.value = false
  }
}

const toggleActive = async (event) => {
  activatingId.value = event.id
  try {
    await updateCompetitionActiveState(event.id, !event.is_current)
    ElMessage.success('比赛状态已更新')
    await fetchCompetitionEvents()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '状态更新失败')
  } finally {
    activatingId.value = null
  }
}

const goContestAdmin = async (event) => {
  await router.push({
    path: '/admin/contest',
    query: {
      module_key: event.module_key,
      event_id: event.id,
      event_name: event.display_title || event.name,
      cup_type: event.cup_type
    }
  })
}

const selectCategory = async (category) => {
  selectedCategory.value = category
  await fetchCompetitionEvents()
}

onMounted(async () => {
  await fetchCompetitionEvents()
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

.history-scroll {
  scrollbar-gutter: stable;
}
</style>
