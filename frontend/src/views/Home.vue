<template>
  <div class="h-full flex flex-col gap-6">
    <!-- 顶部欢迎区 -->
    <div class="flex items-center justify-between shrink-0 animate-fade-in-down">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 tracking-tight">
          欢迎回来，{{ userStore.userName || '同学' }}！👋
        </h1>
        <p class="text-gray-500 mt-2 text-sm flex items-center gap-2">
          今天有 <span class="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full text-xs font-bold">5</span> 个新动态，
          <span class="bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full text-xs font-bold">2</span> 场宣讲会即将开始。
        </p>
      </div>
      <div class="flex items-center gap-3">
         <div class="text-right hidden sm:block">
            <p class="text-sm font-semibold text-gray-700">{{ currentDate }}</p>
            <p class="text-xs text-gray-400">{{ currentWeekday }}</p>
         </div>
      </div>
    </div>

    <!-- 核心内容区 -->
    <div class="flex-1 min-h-0 flex gap-4 pr-1">
      
      <!-- 左侧：现代化日历 (58%) -->
      <div class="w-[58%] bg-white rounded-3xl p-6 shadow-sm flex flex-col relative group animate-fade-in-left border border-gray-100/60 overflow-hidden">
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
               <div :class="['w-full h-full flex flex-col justify-start items-center transition-all duration-300 rounded-xl py-1 border border-transparent hover:border-indigo-100 hover:bg-slate-50 relative group/cell', 
                  isSameDay(data.day, calendarValue) ? '!bg-indigo-50/40' : '']">
                  <!-- 日期数字 -->
                  <div class="flex justify-center items-center h-8 w-full mb-0.5">
                     <span :class="['text-[14px] font-bold font-mono w-7 h-7 flex items-center justify-center rounded-lg transition-all duration-300', 
                        isToday(data.day) ? 'bg-indigo-600 text-white shadow-md shadow-indigo-300' : 'text-gray-600']">
                       {{ data.day.split('-')[2] }}
                     </span>
                  </div>
                  
                  <!-- 日程标记点 -->
                  <div class="w-full px-1 flex flex-col gap-0.5 items-center">
                     <template v-for="(event, index) in getEvents(data.day)" :key="index">
                        <el-tooltip :content="event.title" placement="top" :hide-after="0">
                           <div v-if="event.type === 'tag'" 
                                :class="['w-full py-[2px] rounded-[3px] text-[9px] truncate text-center font-bold leading-none opacity-90 shadow-[0_1px_1px_rgba(0,0,0,0.03)] border border-transparent/50 scale-95 origin-center', event.colorClass]">
                              {{ event.title }}
                           </div>
                           <div v-else 
                                class="w-1.5 h-1.5 rounded-full ring-2 ring-white mt-0.5" :class="event.dotColor"></div>
                        </el-tooltip>
                     </template>
                  </div>
               </div>
            </template>
         </el-calendar>
      </div>

      <!-- 右侧：状态与贡献者 (42%) -->
      <div class="w-[42%] flex flex-col gap-4 animate-fade-in-right">
         
         <!-- 会议室状态卡片 -->
         <div class="bg-white rounded-[24px] p-7 shadow-sm flex-1 flex flex-col min-h-0 relative overflow-hidden group border border-gray-100/60">
            <!-- 装饰背景 -->
            <div class="absolute -right-8 -top-8 w-40 h-40 bg-gradient-to-br from-indigo-50/50 to-purple-50/50 rounded-full blur-3xl opacity-60 pointer-events-none"></div>

            <!-- 当前状态大卡片 -->
            <div class="relative z-10 mb-6 bg-white/40 backdrop-blur-sm rounded-2xl border border-gray-100 p-5">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-bold text-gray-500 uppercase tracking-wider pl-1">Current Status</span>
                    <span class="relative flex h-2.5 w-2.5">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                    </span>
                </div>
                <div class="flex items-end gap-3">
                    <h2 class="text-3xl font-black text-gray-800 tracking-tight">空闲中</h2>
                    <span class="text-sm font-medium text-gray-400 mb-1.5 bg-gray-100 px-2 py-0.5 rounded-md">第一会议室 A101</span>
                </div>
                <div class="mt-4 flex gap-3">
                    <el-button type="primary" class="!rounded-xl !px-6 !h-9 !font-bold !shadow-md shadow-indigo-100/50">立即预约</el-button>
                    <el-button plain class="!rounded-xl !px-4 !h-9 !bg-white/80 !border-gray-200">详情</el-button>
                </div>
            </div>

            <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2 relative z-10 pl-1 text-sm">
                <span class="w-1 h-4 rounded-full bg-indigo-500 block"></span>
                今日预约日程
            </h3>
            
            <div class="flex-1 overflow-y-auto pr-2 -mr-2 custom-scrollbar relative z-10 pl-1">
               <div v-if="roomSlots.filter(s => s.status === 'booked').length === 0" class="flex flex-col items-center justify-center h-32 text-gray-400">
                  <el-icon :size="32" class="mb-2 opacity-20"><Calendar /></el-icon>
                  <p class="text-xs">今日暂无预约</p>
               </div>
               
               <div v-else class="space-y-3">
                  <div v-for="(slot, idx) in roomSlots.filter(s => s.status === 'booked')" :key="idx" 
                       class="relative flex gap-4 p-4 rounded-2xl bg-gray-50/30 border border-gray-50 hover:bg-white hover:shadow-lg hover:shadow-gray-100/40 hover:border-gray-100 transition-all duration-300">
                     
                     <div class="flex flex-col items-center justify-center min-w-[60px] border-r border-gray-200 pr-4">
                        <span class="text-sm font-bold text-gray-500 font-mono">{{ slot.time.split('-')[0] }}</span>
                        <div class="w-0.5 h-3 bg-gray-200 my-1 rounded-full"></div>
                        <span class="text-sm font-bold text-gray-500 font-mono">{{ slot.time.split('-')[1] }}</span>
                     </div>

                     <div class="flex-1 min-w-0 flex flex-col justify-center">
                        <div class="flex items-center gap-2 mb-2">
                           <el-avatar :size="26" class="!bg-indigo-100 !text-indigo-600 !text-xs ring-2 ring-white shadow-sm shrink-0">
                              {{ slot.user.charAt(0) }}
                           </el-avatar>
                           <span class="font-bold text-gray-700 text-sm truncate">{{ slot.user }}</span>
                           <span class="text-[11px] px-2 py-0.5 bg-gray-100 text-gray-500 rounded font-medium shrink-0">{{ slot.dept }}</span>
                        </div>
                        <div class="text-xs text-gray-400 truncate flex items-center gap-1">
                           <span>需使用投影仪、白板</span>
                        </div>
                     </div>
                  </div>
               </div>
            </div>
         </div>

         <!-- 贡献者墙 (毛玻璃悬浮卡片) -->
         <div class="h-auto shrink-0 bg-white/60 backdrop-blur-xl rounded-[20px] p-5 border border-white/50 shadow-[0_8px_30px_rgba(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgba(99,102,241,0.08)] transition-all duration-500 relative overflow-hidden group/wall">
            <!-- 镜面反光效果 -->
            <div class="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/40 to-white/0 opacity-0 group-hover/wall:opacity-100 transition-opacity duration-700 pointer-events-none transform -skew-x-12 translate-x-[-100%] group-hover/wall:translate-x-[100%] ease-in-out"></div>

            <div class="flex items-center justify-between mb-4">
               <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                 <el-icon><Trophy /></el-icon> 
                 System Contributors
               </h3>
               <span class="text-[10px] text-gray-300 bg-gray-50 px-2 py-0.5 rounded-full">Open Source</span>
            </div>
            
            <div class="flex items-center gap-[-8px]">
               <div class="flex -space-x-2 overflow-hidden py-2 px-1">
                 <el-tooltip v-for="(dev, idx) in developers" :key="dev.id" :content="dev.name" placement="top" effect="light">
                    <a :href="dev.url" target="_blank" 
                       class="inline-block relative transition-transform duration-300 hover:!z-10 hover:-translate-y-1.5 rounded-full ring-2 ring-white">
                      <img :src="dev.avatar" :alt="dev.name" class="h-10 w-10 rounded-full object-cover bg-gray-200" />
                    </a>
                 </el-tooltip>
                 
                 <!-- More Button -->
                 <a href="#" class="flex items-center justify-center h-10 w-10 rounded-full ring-2 ring-white bg-gray-100 text-gray-500 text-xs font-medium hover:bg-gray-200 transition-colors z-0 relative hover:z-10 hover:-translate-y-1">
                    +3
                 </a>
               </div>
            </div>
         </div>
         
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { Monitor, User, Trophy, Calendar, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

const userStore = useUserStore()
const calendarValue = ref(new Date())

// 切换日历日期
const selectDate = (type) => {
  if (type === 'prev-month') {
    calendarValue.value = dayjs(calendarValue.value).subtract(1, 'month').toDate()
  } else if (type === 'today') {
    calendarValue.value = new Date()
  } else if (type === 'next-month') {
    calendarValue.value = dayjs(calendarValue.value).add(1, 'month').toDate()
  }
}

// 辅助方法：判断两个日期是否是同一天
const isSameDay = (d1, d2) => {
  return dayjs(d1).isSame(dayjs(d2), 'day')
}

// 当前日期展示
const currentDate = computed(() => dayjs().format('YYYY年MM月DD日'))
const currentWeekday = computed(() => dayjs().format('dddd'))

// 判断是否是今天
const isToday = (dateStr) => {
    return dayjs(dateStr).isSame(dayjs(), 'day')
}

// 模拟日历事件数据
const eventsMap = {
    [dayjs().format('YYYY-MM-DD')]: [
        { type: 'tag', title: '全员大会', colorClass: 'bg-indigo-100 text-indigo-600', dotColor: 'bg-indigo-500' },
        { type: 'dot', title: '部门会议', dotColor: 'bg-orange-400' }
    ],
    [dayjs().add(2, 'day').format('YYYY-MM-DD')]: [
        { type: 'tag', title: '招新宣讲', colorClass: 'bg-emerald-100 text-emerald-600', dotColor: 'bg-emerald-500' }
    ],
    [dayjs().add(5, 'day').format('YYYY-MM-DD')]: [
        { type: 'dot', title: '物资盘点', dotColor: 'bg-pink-400' },
        { type: 'dot', title: '系统维护', dotColor: 'bg-gray-400' }
    ],
    [dayjs().subtract(3, 'day').format('YYYY-MM-DD')]: [
        { type: 'tag', title: '艺术展览', colorClass: 'bg-purple-100/80 text-purple-600', dotColor: 'bg-purple-500' }
    ]
}

const getEvents = (day) => {
    return eventsMap[day] || []
}

// 模拟【单个】会议室（第一会议室）的时间段数据
const roomSlots = ref([
    { time: '08:00 - 10:00', status: 'free', user: '', dept: '' },
    { time: '10:00 - 12:00', status: 'booked', user: '张三', dept: '技术部' },
    { time: '14:00 - 16:00', status: 'booked', user: '李四', dept: '宣传部' },
    { time: '16:00 - 18:00', status: 'free', user: '', dept: '' },
    { time: '19:00 - 21:00', status: 'booked', user: '王五', dept: '主席团' }
])

// 模拟贡献者数据
const developers = ref([
    { id: 1, name: 'Evan You', avatar: 'https://avatars.githubusercontent.com/u/499550?v=4', url: 'https://github.com/yyx990803' },
    { id: 2, name: 'Anthony Fu', avatar: 'https://avatars.githubusercontent.com/u/11247099?v=4', url: 'https://github.com/antfu' },
    { id: 3, name: 'Sindre Sorhus', avatar: 'https://avatars.githubusercontent.com/u/170270?v=4', url: 'https://github.com/sindresorhus' },
    { id: 4, name: 'Linus Torvalds', avatar: 'https://avatars.githubusercontent.com/u/1024025?v=4', url: 'https://github.com/torvalds' },
    { id: 5, name: 'Guido van Rossum', avatar: 'https://avatars.githubusercontent.com/u/289464?v=4', url: 'https://github.com/gvanrossum' }
])

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
  /* 恢复默认显示，但移除所有 padding/margin 和 边框 */
  display: block; 
  padding: 0 0 16px 0;
  border-bottom: none;
}

:deep(.el-calendar__body) {
  padding: 0; 
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: visible; /* 防止内容被切割 */
}

:deep(.el-calendar-table) {
  height: 100%;
  flex: 1;
  table-layout: fixed; 
}

:deep(.el-calendar-table thead th) {
  padding-bottom: 12px;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  text-align: center;
}

:deep(.el-calendar-table td) {
  border: none;
  text-align: center; /* 确保内容居中 */
  vertical-align: top;
}


:deep(.el-calendar__body) {
  padding: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.el-calendar-table) {
  flex: 1;
  height: 100%;
}

:deep(.el-calendar-table td) {
  border: none !important; 
}

:deep(.el-calendar-table .el-calendar-day) {
  height: 100%; 
  padding: 2px;
  display: flex;
  flex-direction: column;
}

/* 移除默认选中背景，由 slot 内部控制 */
:deep(.el-calendar-table td.is-selected) {
  background-color: transparent;
}
:deep(.el-calendar-table .el-calendar-day:hover) {
  background-color: transparent; 
}

/* 动画定义 */
.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out;
}
.animate-fade-in-left {
  animation: fadeInLeft 0.6s ease-out 0.2s backwards;
}
.animate-fade-in-right {
  animation: fadeInRight 0.6s ease-out 0.3s backwards;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes fadeInRight {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
