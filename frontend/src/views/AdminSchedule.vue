<template>
  <div class="h-full flex gap-4 p-6 bg-gray-50">
    <!-- 左侧：日历 (58%) -->
    <div class="w-[58%] bg-white rounded-3xl p-6 shadow-sm flex flex-col relative border border-gray-100/60">
      <el-calendar v-model="calendarValue" class="custom-calendar h-full flex flex-col">
        <!-- 自定义日历头部 -->
        <template #header="{ date }">
          <div class="flex items-center justify-between w-full mb-2 px-2 shrink-0">
            <div class="flex flex-col">
              <div class="flex items-baseline gap-2">
                <span class="text-3xl font-black text-gray-800 tracking-tight">{{ dayjs(calendarValue).format('MMM') }}</span>
                <span class="text-lg font-bold text-gray-400">{{ dayjs(calendarValue).format('YYYY') }}</span>
              </div>
            </div>
            <!-- 导航按钮组 -->
            <div class="flex items-center bg-gray-50 rounded-full p-1 border border-gray-200/50 shadow-sm">
              <el-button size="small" circle text @click="selectDate('prev-month')" class="!w-8 !h-8 hover:!bg-white hover:!text-indigo-600 transition-colors">
                <el-icon><ArrowLeft /></el-icon>
              </el-button>
              <el-button size="small" text @click="selectDate('today')" class="!px-3 !h-8 !font-bold text-gray-600 hover:!text-indigo-600">Today</el-button>
              <el-button size="small" circle text @click="selectDate('next-month')" class="!w-8 !h-8 hover:!bg-white hover:!text-indigo-600 transition-colors">
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
        </template>

        <template #date-cell="{ data }">
          <div @click="handleDateClick(data.day)" 
               :class="['absolute inset-1.5 flex flex-col justify-start items-center overflow-hidden transition-all duration-300 rounded-xl py-1 border border-transparent hover:border-indigo-200 hover:bg-indigo-50 relative group/cell cursor-pointer', 
               isSameDay(data.day, selectedDate) ? '!bg-indigo-100 !border-indigo-300' : '']">
            <!-- 日期数字 -->
            <div class="flex justify-center items-center h-8 w-full mb-0.5 shrink-0">
              <span :class="['text-[14px] font-bold font-mono w-7 h-7 flex items-center justify-center rounded-lg transition-all duration-300', 
                isToday(data.day) ? 'bg-indigo-600 text-white shadow-md shadow-indigo-300' : (data.type === 'current-month' ? 'text-gray-600' : 'text-gray-300 opacity-50')]">
                {{ data.day.split('-')[2] }}
              </span>
            </div>
            
            <!-- 日程标记点 -->
            <div class="w-full px-1 flex flex-wrap gap-1 justify-center items-center flex-1 min-h-0 overflow-hidden">
              <template v-for="(event, index) in getEvents(data.day)" :key="index">
                <el-tooltip v-if="event.type === 'dot'" :content="event.title" placement="top" :hide-after="0">
                  <div class="w-1.5 h-1.5 rounded-full ring-1 ring-white shrink-0" 
                       :style="{ backgroundColor: event.dotColor }"></div>
                </el-tooltip>
                <span v-else-if="event.type === 'more'" 
                      class="text-[10px] text-gray-400 font-bold shrink-0">+{{ event.count }}</span>
              </template>
            </div>
          </div>
        </template>
      </el-calendar>
    </div>

    <!-- 右侧：日程管理 (42%) -->
    <div class="w-[42%] flex flex-col gap-4">
      <!-- 选中日期显示 -->
      <div class="bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl py-5 px-8 text-white shadow-lg">
        <h2 class="text-2xl font-bold mb-1">{{ dayjs(selectedDate).format('MM月DD日') }}</h2>
        <p class="text-sm opacity-90">{{ dayjs(selectedDate).format('dddd') }}</p>
      </div>

      <!-- 当日日程列表 -->
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex-1 flex flex-col min-h-0">
        <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2 text-sm">
          <span class="w-1 h-4 rounded-full bg-indigo-500 block"></span>
          当日日程 ({{ selectedDateSchedules.length }})
        </h3>

        <div class="flex-1 overflow-y-auto pr-2 -mr-2 custom-scrollbar mb-4">
          <div v-if="selectedDateSchedules.length === 0" class="flex flex-col items-center justify-center h-32 text-gray-400">
            <el-icon :size="40" class="mb-2 opacity-20"><Calendar /></el-icon>
            <p class="text-sm">暂无日程安排</p>
          </div>

          <div v-else class="space-y-3">
            <div v-for="schedule in selectedDateSchedules" :key="schedule.id" 
                 class="flex items-stretch rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors border border-gray-100 overflow-hidden group">
              <!-- 颜色标记 -->
              <div class="w-1.5 shrink-0" :style="{ backgroundColor: schedule.color }"></div>
              
              <!-- 内容区域 -->
              <div class="py-3 pr-3 pl-5 flex-1 min-w-0">
                <!-- 时间 -->
                <div class="flex items-center gap-2 mb-2">
                  <el-icon :size="14" class="text-gray-400"><Clock /></el-icon>
                  <span class="text-xs font-mono font-bold text-gray-600">{{ schedule.start_time }} - {{ schedule.end_time }}</span>
                </div>
              
                <!-- 标题 -->
                <h4 class="font-bold text-gray-800 mb-1 text-sm">{{ schedule.title }}</h4>
              
                <!-- 地点 -->
                <div v-if="schedule.location" class="flex items-center gap-1 text-xs text-gray-500 mb-2">
                  <el-icon :size="12"><Location /></el-icon>
                  <span>{{ schedule.location }}</span>
                </div>

                <!-- 删除按钮 -->
                <div class="flex justify-end">
                  <el-popconfirm
                    title="确定要删除这条日程吗？"
                    confirm-button-text="删除"
                    cancel-button-text="取消"
                    confirm-button-type="danger"
                    @confirm="handleDelete(schedule.id)"
                  >
                    <template #reference>
                      <el-button type="danger" link size="small" class="opacity-0 group-hover:opacity-100 transition-opacity">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </template>
                  </el-popconfirm>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 添加日程表单 -->
        <div class="border-t border-gray-100 pt-4">
          <h4 class="font-bold text-gray-700 mb-3 text-sm">添加新日程</h4>
          <el-form :model="form" label-position="top" size="default">
            <el-form-item label="标题" class="!mb-3">
              <el-input v-model="form.title" placeholder="请输入日程标题" maxlength="200" show-word-limit />
            </el-form-item>

            <div class="grid grid-cols-2 gap-3 !mb-3">
              <el-form-item label="开始时间" class="!mb-0">
                <el-time-select
                  v-model="form.start_time"
                  start="00:00"
                  step="00:30"
                  end="23:30"
                  placeholder="00:00"
                  class="!w-full"
                />
              </el-form-item>

              <el-form-item label="结束时间" class="!mb-0">
                <el-time-select
                  v-model="form.end_time"
                  start="00:00"
                  step="00:30"
                  end="23:30"
                  :min-time="form.start_time"
                  placeholder="23:30"
                  class="!w-full"
                />
              </el-form-item>
            </div>

            <el-form-item label="地点" class="!mb-3">
              <el-input v-model="form.location" placeholder="请输入地点（可选）" maxlength="200" />
            </el-form-item>

            <el-form-item label="颜色标记" class="!mb-3">
              <div class="flex gap-3 mt-1 pl-2">
                 <div v-for="color in predefineColors" :key="color"
                      @click="form.color = color"
                      class="w-6 h-6 rounded-md cursor-pointer transition-transform hover:scale-105 flex items-center justify-center ring-2 ring-offset-1"
                      :class="form.color === color ? 'ring-indigo-500 scale-105' : 'ring-transparent'"
                      :style="{ backgroundColor: color }">
                    <el-icon v-if="form.color === color" class="text-white font-bold text-xs"><Check /></el-icon>
                 </div>
              </div>
            </el-form-item>

            <el-button type="primary" @click="handleSubmit" :loading="submitting" class="w-full !rounded-lg !h-10">
              <el-icon class="mr-1"><Plus /></el-icon>
              添加日程
            </el-button>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar, ArrowLeft, ArrowRight, Clock, Location, Delete, Plus, Check } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { getSchedules, createSchedule, deleteSchedule } from '@/api/schedule'

dayjs.locale('zh-cn')

const calendarValue = ref(new Date())
const selectedDate = ref(dayjs().format('YYYY-MM-DD'))
const schedulesMap = ref({})
const selectedDateSchedules = ref([])
const submitting = ref(false)

// 表单数据
const form = ref({
  title: '',
  start_time: '',
  end_time: '',
  location: '',
  color: '#3B82F6'
})

// 预设颜色（6个）
const predefineColors = [
  '#3B82F6', // 蓝色
  '#10B981', // 绿色
  '#F59E0B', // 橙色
  '#EF4444', // 红色
  '#8B5CF6', // 紫色
  '#EC4899'  // 粉色
]

// 切换日历日期
const selectDate = (type) => {
  if (type === 'prev-month') {
    calendarValue.value = dayjs(calendarValue.value).subtract(1, 'month').toDate()
  } else if (type === 'today') {
    calendarValue.value = new Date()
    selectedDate.value = dayjs().format('YYYY-MM-DD')
  } else if (type === 'next-month') {
    calendarValue.value = dayjs(calendarValue.value).add(1, 'month').toDate()
  }
}

// 判断是否是同一天
const isSameDay = (d1, d2) => {
  return dayjs(d1).isSame(dayjs(d2), 'day')
}

// 判断是否是今天
const isToday = (dateStr) => {
  return dayjs(dateStr).isSame(dayjs(), 'day')
}

// 获取指定日期的日程（显示为圆点）
const getEvents = (day) => {
  const schedules = schedulesMap.value[day] || []
  const maxDots = 3
  const events = schedules.slice(0, maxDots).map(schedule => ({
    type: 'dot',
    title: `${schedule.start_time}-${schedule.end_time} ${schedule.title}`,
    dotColor: schedule.color || '#3B82F6'
  }))
  
  if (schedules.length > maxDots) {
    events.push({
      type: 'more',
      count: schedules.length - maxDots
    })
  }
  
  return events
}

// 加载指定月份的日程
const loadMonthSchedules = async (targetDate) => {
  try {
    const startDate = dayjs(targetDate).startOf('month').format('YYYY-MM-DD')
    const endDate = dayjs(targetDate).endOf('month').format('YYYY-MM-DD')
    
    const res = await getSchedules({ start_date: startDate, end_date: endDate })
    if (res.code === 200) {
      const newMap = {}
      res.data.forEach(schedule => {
        const dateKey = schedule.schedule_date
        if (!newMap[dateKey]) {
          newMap[dateKey] = []
        }
        newMap[dateKey].push(schedule)
      })
      schedulesMap.value = newMap
      
      // 更新选中日期的日程列表
      updateSelectedDateSchedules()
    }
  } catch (e) {
    console.error('加载日程失败:', e)
  }
}

// 更新选中日期的日程列表
const updateSelectedDateSchedules = () => {
  selectedDateSchedules.value = (schedulesMap.value[selectedDate.value] || []).sort((a, b) => {
    return a.start_time.localeCompare(b.start_time)
  })
}

// 监听日历月份变化
watch(calendarValue, (newVal) => {
  loadMonthSchedules(newVal)
})

// 监听选中日期变化
watch(selectedDate, () => {
  updateSelectedDateSchedules()
})

// 处理日期点击
const handleDateClick = (day) => {
  selectedDate.value = day
}

// 提交表单
const handleSubmit = async () => {
  // 表单验证
  if (!form.value.title) {
    ElMessage.warning('请输入日程标题')
    return
  }
  if (!form.value.start_time || !form.value.end_time) {
    ElMessage.warning('请选择开始和结束时间')
    return
  }
  if (form.value.start_time >= form.value.end_time) {
    ElMessage.warning('结束时间必须晚于开始时间')
    return
  }

  submitting.value = true
  try {
    const res = await createSchedule({
      title: form.value.title,
      schedule_date: selectedDate.value,
      start_time: form.value.start_time,
      end_time: form.value.end_time,
      location: form.value.location || null,
      color: form.value.color
    })

    if (res.code === 200) {
      // 检查是否有时间冲突警告
      if (res.data.warning) {
        ElMessage.warning(res.data.warning)
      } else {
        ElMessage.success('日程添加成功')
      }

      // 重置表单
      form.value = {
        title: '',
        start_time: '',
        end_time: '',
        location: '',
        color: '#3B82F6'
      }

      // 重新加载当月日程
      await loadMonthSchedules(calendarValue.value)
    }
  } catch (e) {
    ElMessage.error('添加日程失败')
    console.error(e)
  } finally {
    submitting.value = false
  }
}

// 删除日程
const handleDelete = async (scheduleId) => {
  try {
    const res = await deleteSchedule(scheduleId)
    if (res.code === 200) {
      ElMessage.success('日程删除成功')
      // 重新加载当月日程
      await loadMonthSchedules(calendarValue.value)
    }
  } catch (e) {
    ElMessage.error('删除日程失败')
    console.error(e)
  }
}

onMounted(async () => {
  await loadMonthSchedules(new Date())
})
</script>

<style scoped>
/* 深度定制 EL-Calendar */
:deep(.el-calendar) {
  --el-calendar-border: none;
  --el-calendar-header-border-bottom: none; 
  background: transparent;
  height: 100%;
}

:deep(.el-calendar__header) {
  display: block; 
  padding: 0 0 16px 0;
  border-bottom: none;
}

:deep(.el-calendar__body) {
  padding: 0; 
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.el-calendar-table) {
  width: 100%;
  height: 100%;
  table-layout: fixed;
  border-collapse: collapse;
}

:deep(.el-calendar-table thead th) {
  padding-bottom: 12px;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  text-align: center;
  border: none;
}

:deep(.el-calendar-table tr) {
  height: 16.666%;
}

:deep(.el-calendar-table tr:first-child td) {
  border-top: none;
}

:deep(.el-calendar-table td) {
  border: none;
  padding: 0;
  vertical-align: top;
  position: relative;
}

:deep(.el-calendar-table .el-calendar-day) {
  height: 100% !important;
  min-height: 0 !important;
  padding: 0;
  position: relative;
  z-index: 1;
}

:deep(.el-calendar-table td.is-selected) {
  background-color: transparent;
}

:deep(.el-calendar-table .el-calendar-day:hover) {
  background-color: transparent; 
}

/* 自定义滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
