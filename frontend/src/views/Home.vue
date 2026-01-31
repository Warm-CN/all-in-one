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
               <div @click.stop="handleDateClick(data.day, $event)" 
                    :class="['absolute inset-1.5 flex flex-col justify-start items-center overflow-hidden transition-all duration-300 rounded-xl py-1 border border-transparent hover:border-indigo-100 hover:bg-slate-50 relative group/cell cursor-pointer', 
                  isSameDay(data.day, calendarValue) ? '!bg-indigo-50/40' : '']">
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
         
         <!-- 浮动日程卡片 -->
         <transition name="schedule-card">
            <div v-if="showScheduleCard" 
                 class="fixed w-80 bg-white rounded-2xl shadow-2xl border border-gray-100 z-[9999] overflow-hidden"
                 :style="popupStyle"
                 @click.stop>
               <!-- 卡片头部 -->
               <div class="bg-gradient-to-r from-indigo-500 to-purple-500 p-4 text-white">
                  <div class="flex items-center justify-between mb-1">
                     <h3 class="text-lg font-bold">{{ dayjs(selectedDate).format('MM月DD日') }}</h3>
                     <el-button circle size="small" text @click="closeScheduleCard" class="!text-white hover:!bg-white/20">
                        <el-icon><Close /></el-icon>
                     </el-button>
                  </div>
                  <p class="text-xs opacity-90">{{ dayjs(selectedDate).format('dddd') }}</p>
               </div>
               
               <!-- 卡片内容 -->
               <div class="p-4 max-h-96 overflow-y-auto custom-scrollbar">
                  <div v-if="selectedDateSchedules.length === 0" class="flex flex-col items-center justify-center py-8 text-gray-400">
                     <el-icon :size="40" class="mb-2 opacity-20"><Calendar /></el-icon>
                     <p class="text-sm">当日暂无日程</p>
                  </div>
                  
                  <div v-else class="space-y-3">
                     <div v-for="schedule in selectedDateSchedules" :key="schedule.id" 
                          class="p-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors border border-gray-100">
                        <!-- 时间标记 -->
                        <div class="flex items-center gap-2 mb-2">
                           <div class="w-2 h-2 rounded-full" :style="{ backgroundColor: schedule.color }"></div>
                           <span class="text-xs font-mono font-bold text-gray-500">{{ schedule.start_time }} - {{ schedule.end_time }}</span>
                        </div>
                        
                        <!-- 标题 -->
                        <h4 class="font-bold text-gray-800 mb-1 text-sm">{{ schedule.title }}</h4>
                        
                        <!-- 地点 -->
                        <div v-if="schedule.location" class="flex items-center gap-1 text-xs text-gray-500">
                           <el-icon :size="12"><Location /></el-icon>
                           <span>{{ schedule.location }}</span>
                        </div>
                     </div>
                  </div>
               </div>
            </div>
         </transition>
      </div>

      <!-- 右侧：状态与贡献者 (42%) -->
      <div class="w-[42%] flex flex-col gap-4 animate-fade-in-right">
         
         <!-- 会议室状态卡片 -->
         <div class="bg-white rounded-[24px] p-7 shadow-sm flex-1 flex flex-col min-h-0 relative overflow-hidden group border border-gray-100/60">
            <!-- 装饰背景 -->
            <div class="absolute -right-8 -top-8 w-40 h-40 bg-gradient-to-br from-indigo-50/50 to-purple-50/50 rounded-full blur-3xl opacity-60 pointer-events-none"></div>

            <!-- 当前状态大卡片 -->
            <div class="relative z-10 mb-6 bg-white/40 backdrop-blur-sm rounded-2xl border border-gray-100 p-5 overflow-hidden">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-bold text-gray-500 uppercase tracking-wider pl-1">Current Status</span>
                </div>
                <div class="flex items-end gap-3">
                    <h2 class="text-3xl font-black text-gray-800 tracking-tight">空闲中</h2>
                    <span class="text-sm font-medium text-gray-400 mb-1.5 bg-gray-100 px-2 py-0.5 rounded-md">北三会议室</span>
                </div>
                <div class="mt-4 flex gap-3">
                    <el-button type="primary" class="!rounded-xl !px-6 !h-9 !font-bold !shadow-md shadow-indigo-100/50" @click="router.push('/rooms')">立即预约</el-button>
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
                           <span>{{ slot.remarks }}</span>
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
                 <el-tooltip v-for="(dev, idx) in developers.slice(0, 5)" :key="dev.id" :content="dev.name" placement="top" effect="light">
                    <a :href="dev.url" target="_blank" 
                       class="inline-block relative transition-transform duration-300 hover:!z-10 hover:-translate-y-1.5 rounded-full ring-2 ring-white">
                      <img :src="dev.avatar" :alt="dev.name" class="h-10 w-10 rounded-full object-cover bg-gray-200" />
                    </a>
                 </el-tooltip>
                 
                 <!-- More Button -->
                 <div v-if="developers.length > 5" 
                      @click.stop="openContributorsPopup($event)" 
                      class="flex items-center justify-center h-10 w-10 rounded-full ring-2 ring-white bg-indigo-50 text-indigo-600 text-xs font-bold hover:bg-indigo-100 hover:text-indigo-700 transition-all z-0 relative hover:z-10 hover:-translate-y-1 cursor-pointer shadow-sm">
                    +{{ developers.length - 5 }}
                 </div>
               </div>
            </div>
         </div>
         
         <!-- 贡献者悬浮卡片 -->
         <transition name="schedule-card">
            <div v-if="showContributorCard" 
                 class="fixed w-80 bg-white rounded-2xl shadow-2xl border border-gray-100 z-[9999] overflow-hidden"
                 :style="contributorPopupStyle"
                 @click.stop>
               <!-- 卡片头部 -->
               <div class="bg-gradient-to-r from-indigo-500 to-purple-500 p-4 text-white relative z-10">
                  <div class="flex items-center justify-between mb-1">
                     <h3 class="text-lg font-bold">系统贡献者</h3>
                     <el-button circle size="small" text @click="showContributorCard = false" class="!text-white hover:!bg-white/20">
                        <el-icon><Close /></el-icon>
                     </el-button>
                  </div>
                  <p class="text-xs opacity-90">感谢每一位开发者的辛勤付出！</p>
               </div>
               
               <!-- 卡片内容 -->
               <div class="p-5 pt-6 grid grid-cols-4 gap-4 max-h-80 overflow-y-auto custom-scrollbar relative z-0">
                  <a v-for="dev in developers" :key="dev.id" :href="dev.url" target="_blank" 
                     class="flex flex-col items-center gap-2 group p-2 rounded-xl hover:bg-gray-50 transition-colors">
                      <img :src="dev.avatar" :alt="dev.name" class="h-10 w-10 rounded-full object-cover ring-2 ring-gray-100 group-hover:ring-indigo-200 transition-all"/>
                      <span class="text-[10px] text-gray-600 font-medium truncate w-full text-center">{{ dev.name }}</span>
                  </a>
               </div>
            </div>
         </transition>
         
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { Monitor, User, Trophy, Calendar, ArrowLeft, ArrowRight, Close, Location } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { getBookings } from '@/api/booking'
import { getSchedules } from '@/api/schedule'

dayjs.locale('zh-cn')

const router = useRouter()
const userStore = useUserStore()
const calendarValue = ref(new Date())
const roomSlots = ref([])
const schedulesMap = ref({}) // 日程数据映射 { 'YYYY-MM-DD': [...] }
const showScheduleCard = ref(false) // 是否显示日程浮动卡片
const selectedDate = ref(null) // 选中的日期
const selectedDateSchedules = ref([]) // 选中日期的日程列表
const popupStyle = ref({ top: '0px', left: '0px' })
const showContributorCard = ref(false)
const contributorPopupStyle = ref({ top: '0px', left: '0px' })

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

// 判断是否是当月第一天或最后一天
const isMonthBoundary = (dateStr) => {
    const d = dayjs(dateStr)
    return d.date() === 1 || d.date() === d.daysInMonth()
}

// 获取指定日期的日程（显示为圆点）
const getEvents = (day) => {
    const schedules = schedulesMap.value[day] || []
    // 最多显示3个圆点，超出显示+N
    const maxDots = 3
    const events = schedules.slice(0, maxDots).map(schedule => ({
        type: 'dot',
        title: `${schedule.start_time}-${schedule.end_time} ${schedule.title}`,
        dotColor: schedule.color || '#3B82F6'
    }))
    
    // 如果超过3个，添加+N提示
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
            // 将数组转换为按日期分组的对象
            const newMap = {}
            res.data.forEach(schedule => {
                const dateKey = schedule.schedule_date
                if (!newMap[dateKey]) {
                    newMap[dateKey] = []
                }
                newMap[dateKey].push(schedule)
            })
            schedulesMap.value = newMap
        }
    } catch (e) {
        console.error('加载日程失败:', e)
    }
}

// 监听日历月份变化
watch(calendarValue, (newVal) => {
    loadMonthSchedules(newVal)
})

// 处理日期点击事件
const handleDateClick = (day, event) => {
    selectedDate.value = day
    selectedDateSchedules.value = schedulesMap.value[day] || []
    
    // 智能定位：根据鼠标在屏幕的位置决定弹出方向
    const gap = 12 // 鼠标偏移量
    const { clientX, clientY } = event
    const { innerWidth, innerHeight } = window
    
    const style = {}

    // 水平方向：如果在屏幕右侧 (60%之后)，则向左弹出
    if (clientX > innerWidth * 0.6) {
        style.left = 'auto'
        style.right = `${innerWidth - clientX + gap}px`
        // 防止溢出左边界 (320px是卡片宽)
        if (clientX - 320 < 0) {
             style.right = 'auto'
             style.left = '10px'
        }
    } else {
        style.left = `${clientX + gap}px`
        style.right = 'auto'
    }

    // 垂直方向：如果在屏幕下方 (60%之后)，则向上弹出
    if (clientY > innerHeight * 0.6) {
        style.top = 'auto'
        style.bottom = `${innerHeight - clientY + gap}px`
    } else {
        style.top = `${clientY + gap}px`
        style.bottom = 'auto'
    }

    popupStyle.value = style
    showScheduleCard.value = true
}

// 关闭浮动卡片
const closeScheduleCard = () => {
    showScheduleCard.value = false
}

const openContributorsPopup = (event) => {
    const gap = 12
    const { clientX, clientY } = event
    const { innerWidth, innerHeight } = window
    
    const style = {}

    if (clientX > innerWidth * 0.6) {
        style.left = 'auto'
        style.right = `${innerWidth - clientX + gap}px`
        // 防止溢出左边界 (320px是卡片宽)
        if (clientX - 320 < 0) {
             style.right = 'auto'
             style.left = '10px'
        }
    } else {
        style.left = `${clientX + gap}px`
        style.right = 'auto'
    }

    if (clientY > innerHeight * 0.6) {
        style.top = 'auto'
        style.bottom = `${innerHeight - clientY + gap}px`
    } else {
        style.top = `${clientY + gap}px`
        style.bottom = 'auto'
    }

    contributorPopupStyle.value = style
    showContributorCard.value = true
}

// 点击空白关闭
const handleGlobalClick = () => {
   if (showScheduleCard.value) {
      showScheduleCard.value = false
   }
   if (showContributorCard.value) {
      showContributorCard.value = false
   }
}

onMounted(async () => {
   document.addEventListener('click', handleGlobalClick)
   try {
      // 默认获取今天的预约作为概览
      const res = await getBookings(dayjs().format('YYYY-MM-DD'))
      if (res.code === 200) {
         // 适配 API 数据到 Home 组件的格式
         roomSlots.value = res.data.map(item => ({
             time: `${item.start_time} - ${item.end_time}`,
             status: 'booked', // 只要是 API 返回的都是 booked
             user: item.user_name || '未知用户',
             dept: item.user_dept || '未知部门',
             remarks: item.remarks || '无备注'
         }))
      }
   } catch (e) {
      console.error('Fetch home bookings failed', e)
   }
   
   // 加载当月日程
   await loadMonthSchedules(new Date())
})

onUnmounted(() => {
   document.removeEventListener('click', handleGlobalClick)
})

// 模拟贡献者数据
const developers = ref([
    { id: 1, name: 'Evan You', avatar: 'https://avatars.githubusercontent.com/u/499550?v=4', url: 'https://github.com/yyx990803' },
    { id: 2, name: 'Anthony Fu', avatar: 'https://avatars.githubusercontent.com/u/11247099?v=4', url: 'https://github.com/antfu' },
    { id: 3, name: 'Sindre Sorhus', avatar: 'https://avatars.githubusercontent.com/u/170270?v=4', url: 'https://github.com/sindresorhus' },
    { id: 4, name: 'Linus Torvalds', avatar: 'https://avatars.githubusercontent.com/u/1024025?v=4', url: 'https://github.com/torvalds' },
    { id: 5, name: 'Guido van Rossum', avatar: 'https://avatars.githubusercontent.com/u/289464?v=4', url: 'https://github.com/gvanrossum' },
    { id: 6, name: 'Dan Abramov', avatar: 'https://avatars.githubusercontent.com/u/810438?v=4', url: 'https://github.com/gaearon' },
    { id: 7, name: 'Ryan Dahl', avatar: 'https://avatars.githubusercontent.com/u/80?v=4', url: 'https://github.com/ry' },
    { id: 8, name: 'Rich Harris', avatar: 'https://avatars.githubusercontent.com/u/1162160?v=4', url: 'https://github.com/Rich-Harris' }
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
  display: block; 
  padding: 0 0 16px 0;
  border-bottom: none;
}

:deep(.el-calendar__body) {
  padding: 0; 
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止溢出 */
}

:deep(.el-calendar-table) {
  width: 100%;
  height: 100%;
  table-layout: fixed;
  border-collapse: collapse; /* 关键：合并边框模型，更有利于高度计算 */
}

:deep(.el-calendar-table thead th) {
  padding-bottom: 12px;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  text-align: center;
  border: none; /* 移除表头边框 */
}

/* 强制每行高度一致 */
:deep(.el-calendar-table tr) {
  height: 16.666%; /* 假设6行展示，强制均分 */
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
  height: 100% !important; /* 强制填满 td */
  min-height: 0 !important; /* 覆盖默认最小高度 */
  padding: 0;
  position: relative;
  z-index: 1;
}

/* 移除默认选中背景 */
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

/* 浮动卡片过渡动画 */
.schedule-card-enter-active,
.schedule-card-leave-active {
  transition: all 0.2s ease-out;
}
.schedule-card-enter-from,
.schedule-card-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* 遮罩层过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
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
