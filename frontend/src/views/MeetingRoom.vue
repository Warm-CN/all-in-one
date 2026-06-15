<template>
  <div class="flex h-full flex-col gap-5">
    <!-- 顶部控制烂 -->
    <div class="flex shrink-0 flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-4">
        <div class="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
           <el-icon :size="20"><Monitor /></el-icon>
        </div>
        <div>
           <h1 class="text-lg font-bold text-gray-800">北三会议室</h1>
           <p class="text-xs text-gray-500">密码锁密码为：812604</p>
        </div>
      </div>
      
      <div class="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:justify-end">
         <el-button :icon="ArrowLeft" circle size="default" @click="changeDate(-1)" :disabled="isToday" />
         <el-date-picker
              v-model="currentDate"
              type="date"
              placeholder="选择日期"
              format="YYYY年MM月DD日"
              value-format="YYYY-MM-DD"
              :clearable="false"
              class="w-full sm:!w-[170px]"
              :disabled-date="disabledDate"
              @change="fetchData"
              teleported
            />
         <el-button :icon="ArrowRight" circle size="default" @click="changeDate(1)" :disabled="isMaxDate" />
         <el-button type="primary" text bg size="default" @click="goToToday" class="sm:!ml-1" :disabled="isToday">今天</el-button>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="flex flex-col lg:flex-row flex-1 gap-5 min-h-0 overflow-auto lg:overflow-hidden pb-4">
       <!-- 左侧：预约列表视图 (65%) -->
       <div class="w-full lg:w-[65%] flex flex-col gap-4 min-h-0 shrink-0">
          
          <!-- 上半部分：今日预约列表 -->
          <div class="relative flex flex-1 flex-col overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm group">
              <div class="sticky top-0 z-10 flex flex-col gap-2 border-b border-gray-50 bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
                 <span class="font-bold text-gray-700 flex items-center gap-2">
                    <el-icon class="text-indigo-500"><Calendar /></el-icon> 今日预约列表
                    <span class="text-xs font-normal text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">{{ bookings.length }}</span>
                 </span>
                 <div class="flex items-center gap-4 text-xs">
                    <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-indigo-500"></span>全部</div>
                 </div>
              </div>

              <div class="flex-1 overflow-y-auto custom-scrollbar p-5">
                 <div v-if="bookings.length === 0" class="flex flex-col items-center justify-center h-48 text-gray-400">
                    <el-icon :size="48" class="mb-3 opacity-20"><Calendar /></el-icon>
                    <p class="text-sm">该日期暂无预约记录</p>
                 </div>

                 <div v-else class="space-y-3">
                    <div v-for="booking in bookings" :key="booking.id"
                         class="relative flex flex-col gap-3 overflow-hidden rounded-xl border border-gray-100 bg-white p-4 transition-all group/card hover:border-indigo-100 hover:shadow-sm md:flex-row md:items-center md:justify-between">
                       <!-- 左侧装饰条 -->
                       <div class="absolute left-0 top-0 bottom-0 w-1 bg-indigo-500 rounded-l-xl opacity-0 group-hover/card:opacity-100 transition-opacity"></div>
                       
                       <div class="flex flex-col gap-3 pl-2 sm:flex-row sm:items-center sm:gap-4">
                          <!-- 时间 -->
                          <div class="flex items-center gap-2 text-sm font-bold font-mono text-gray-600 bg-gray-50 px-2 py-1 rounded-lg">
                             <span>{{ booking.start_time }}</span>
                             <span class="text-gray-300">→</span>
                             <span>{{ booking.end_time }}</span>
                          </div>

                          <!-- 用户 -->
                          <div class="flex items-center gap-2">
                             <el-avatar :size="24" class="!bg-indigo-100 !text-indigo-600 !text-[10px] font-bold">
                                {{ booking.user_name ? booking.user_name.charAt(0) : 'U' }}
                             </el-avatar>
                             <span class="font-bold text-gray-700 text-sm">{{ booking.user_name }}</span>
                             <span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{{ booking.user_dept }}</span>
                          </div>
                       </div>
                       
                       <!-- 备注 -->
                       <div class="flex w-full items-center text-xs text-gray-400 md:max-w-[200px] md:justify-end">
                           {{ booking.remarks || '无备注' }}
                       </div>
                    </div>
                 </div>
              </div>
          </div>

          <!-- 下半部分：我的预约 -->
          <div class="relative flex h-[320px] shrink-0 flex-col overflow-hidden rounded-2xl border border-gray-100 border-t-4 border-t-emerald-400/20 bg-white shadow-sm sm:h-[280px]">
              <div class="sticky top-0 z-10 flex flex-col gap-2 border-b border-gray-50 bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
                 <span class="font-bold text-gray-800 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-emerald-500"></div> 我的预约
                 </span>
                 <span class="text-[10px] text-emerald-600 bg-emerald-50 px-2 py-1 rounded">未来预约列表</span>
              </div>

              <div class="flex-1 overflow-y-auto custom-scrollbar p-5">
                 <div v-if="myBookings.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400">
                    <p class="text-sm">暂无未来预约</p>
                 </div>
                 
                 <div v-else class="space-y-3">
                    <div v-for="booking in myBookings" :key="booking.id"
                         class="flex flex-col gap-3 rounded-xl border border-emerald-100 bg-emerald-50/30 p-3.5 transition-all group/my hover:bg-emerald-50/60 sm:flex-row sm:items-center sm:justify-between">
                       
                       <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
                          <div class="flex flex-col items-center min-w-[70px] border-r border-emerald-100 pr-3 mr-1">
                             <div class="text-[10px] text-emerald-500 font-bold bg-white px-1.5 rounded-full mb-1 border border-emerald-100 whitespace-nowrap">
                                {{ dayjs(booking.booking_date).format('MM-DD') }}
                             </div>
                             <span class="text-base font-bold text-emerald-700 font-mono leading-none">{{ booking.start_time }}</span>
                             <span class="text-[10px] text-emerald-500/80 font-mono mt-0.5">至 {{ booking.end_time }}</span>
                          </div>
                          
                          <div class="flex flex-col gap-0.5">
                             <span class="text-sm font-bold text-gray-700">{{ booking.remarks || '无备注' }}</span>
                             <span class="text-xs text-gray-400">{{ booking.num_people }} 人参与</span>
                             <span v-if="dayjs(booking.booking_date).isSame(dayjs(currentDate), 'day')" class="text-[10px] text-indigo-500 bg-indigo-50 px-1 rounded w-fit mt-0.5">当前选中日期</span>
                          </div>
                       </div>

                       <el-popconfirm 
                          title="确认取消此预约?" 
                          @confirm="handleCancel(booking.id)"
                          width="240"
                          confirm-button-text="确认取消"
                          cancel-button-text="暂不"
                          confirm-button-type="danger"
                          icon-color="red"
                      >
                        <template #reference>
                            <el-button type="danger" plain size="small" class="!px-3 !rounded-lg hover:!bg-red-50 hover:!text-red-600 transition-colors">
                                取消
                            </el-button>
                        </template>
                      </el-popconfirm>
                    </div>
                 </div>
              </div>
          </div>

       </div>

       <!-- 右侧：预约表单 (35%) -->
       <div class="flex w-full flex-col gap-5 lg:w-[35%]">
           <div class="relative flex h-auto min-h-[560px] flex-1 flex-col overflow-hidden rounded-2xl border border-gray-100 bg-white p-4 shadow-sm sm:p-5 lg:h-auto lg:p-6">
              <div v-if="isPastDate || isTooFarFuture" class="absolute inset-0 bg-gray-50/80 z-20 flex flex-col items-center justify-center backdrop-blur-[1px]">
                  <el-icon :size="48" class="text-gray-300 mb-2"><CircleCloseFilled /></el-icon>
                  <p class="text-gray-500 font-bold">{{ isPastDate ? '无法在过去日期进行预约' : '只能预约未来7天内的日期' }}</p>
                  <el-button type="primary" link @click="goToToday" class="mt-2">返回今天</el-button>
              </div>

              <h2 class="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
                 <span class="w-1 h-5 bg-indigo-600 rounded-full"></span>
                 预约申请
              </h2>

              <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="flex-1 flex flex-col" :disabled="loading || isPastDate || isTooFarFuture">
                 <el-form-item label="预约日期">
                    <div class="w-full px-3 py-2 bg-gray-50 rounded-lg text-gray-500 text-sm font-bold border border-gray-200">
                        {{ currentDateFormatted }}
                    </div>
                 </el-form-item>

                 <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <el-form-item label="开始时间" prop="start_time">
                        <el-time-select
                           v-model="form.start_time"
                           start="00:00"
                           step="00:30"
                           end="23:30"
                           placeholder="00:00"
                           class="!w-full"
                        />
                    </el-form-item>
                    <el-form-item label="结束时间" prop="end_time">
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

                 <el-form-item label="参与人数" prop="num_people">
                    <el-input-number v-model="form.num_people" :min="1" :max="50" class="!w-full" controls-position="right" />
                 </el-form-item>
                 
                 <el-form-item label="会议备注" prop="remarks">
                    <el-input v-model="form.remarks" type="textarea" :rows="3" placeholder="例如：技术分享会" />
                 </el-form-item>

                 <div class="mt-auto pt-6">
                    <el-button type="primary" size="large" class="w-full !rounded-xl !h-12 !text-base !font-bold !shadow-lg shadow-indigo-100" 
                        @click="submitBooking" :loading="submitting">
                        立即预约
                    </el-button>
                    <p class="text-xs text-center text-gray-400 mt-3">提交即表示同意《会议室使用规范》</p>
                 </div>
              </el-form>
           </div>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Monitor, ArrowLeft, ArrowRight, Delete, Calendar, CircleCloseFilled } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import isBetween from 'dayjs/plugin/isBetween'
import { ElMessage } from 'element-plus'
import { getBookings, createBooking, cancelBooking, getMyBookings } from '@/api/booking'
import { useUserStore } from '@/store/user'

dayjs.extend(isBetween)

const userStore = useUserStore()
const currentDate = ref(dayjs().format('YYYY-MM-DD'))
const bookings = ref([])
const myBookings = ref([])
const loading = ref(false)
const submitting = ref(false)
const formRef = ref(null)

// 8:00 到 22:00 的小时数
const hours = Array.from({ length: 15 }, (_, i) => i + 8)

const form = ref({
    start_time: '',
    end_time: '',
    num_people: 1,
    remarks: ''
})

const rules = {
    start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
    end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
    num_people: [{ required: true, message: '请输入人数', trigger: 'blur' }],
}

// 格式化日期显示
const currentDateFormatted = computed(() => {
    return dayjs(currentDate.value).format('YYYY年MM月DD日 dddd')
})

// 是否为今天
const isToday = computed(() => {
    return currentDate.value === dayjs().format('YYYY-MM-DD')
})

// 是否为过去的日期
const isPastDate = computed(() => {
    return dayjs(currentDate.value).isBefore(dayjs(), 'day')
})

// 是否超过未来7天
const isTooFarFuture = computed(() => {
    return dayjs(currentDate.value).isAfter(dayjs().add(7, 'day'), 'day')
})

// 是否为最大可选日期（今天+7天）
const isMaxDate = computed(() => {
    return dayjs(currentDate.value).isSame(dayjs().add(7, 'day'), 'day') || isTooFarFuture.value
})

// 日期禁用逻辑
const disabledDate = (time) => {
    const date = dayjs(time)
    const today = dayjs().startOf('day')
    const maxDate = today.add(7, 'day')
    return date.isBefore(today) || date.isAfter(maxDate)
}

// 检查是否是我的预约 (用于今日列表高亮)
const isMyBooking = (booking) => {
    return booking.user_id === userStore.userInfo?.id || userStore.userRole === 'admin'
}

// 切换日期
const changeDate = (days) => {
    currentDate.value = dayjs(currentDate.value).add(days, 'day').format('YYYY-MM-DD')
    fetchData()
}

const goToToday = () => {
    currentDate.value = dayjs().format('YYYY-MM-DD')
    fetchData()
}

// API 操作
const fetchData = async () => {
    loading.value = true
    try {
        const res = await getBookings(currentDate.value)
        if (res.code === 200) {
            bookings.value = res.data
        }
    } catch (err) {
        console.error(err)
    } finally {
        loading.value = false
    }
}

const fetchMyBookings = async () => {
    try {
        const res = await getMyBookings(true) // true 仅获取未来预约
        if (res.code === 200) {
            myBookings.value = res.data
        }
    } catch (err) {
        console.error(err)
    }
}

const submitBooking = async () => {
    if (isPastDate.value) {
        ElMessage.warning('不能预约过去的日期')
        return
    }
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true
            try {
                const res = await createBooking({
                    booking_date: currentDate.value,
                    ...form.value
                })
                
                if (res.code === 200) {
                    ElMessage.success('预约成功')
                    form.value = { start_time: '', end_time: '', num_people: 1, remarks: '' } // 重置表单
                    fetchData()
                    fetchMyBookings()
                } else {
                    ElMessage.error(res.msg || '预约失败')
                }
            } catch (err) {
                 ElMessage.error(err.message || '系统错误')
            } finally {
                submitting.value = false
            }
        }
    })
}

const handleCancel = async (id) => {
    try {
        const res = await cancelBooking(id)
        if (res.code === 200) {
            ElMessage.success('已取消预约')
            fetchData()
            fetchMyBookings()
        } else {
            ElMessage.error(res.msg || '取消失败')
        }
    } catch (err) {
        ElMessage.error('系统错误')
    }
}

onMounted(() => {
    fetchData()
    fetchMyBookings()
})
</script>

<style scoped>
/* 隐藏 el-input-number 的边框以适应风格 */
:deep(.el-input__wrapper) {
    box-shadow: 0 0 0 1px #e5e7eb inset;
}
:deep(.el-input__wrapper:hover) {
    box-shadow: 0 0 0 1px #a5b4fc inset;
}
:deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 1px #6366f1 inset !important;
    ring: 2px #e0e7ff;
}
</style>
