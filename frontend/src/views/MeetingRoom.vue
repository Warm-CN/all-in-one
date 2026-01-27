<template>
  <div class="flex flex-col h-full gap-5">
    <!-- 顶部控制烂 -->
    <div class="flex items-center justify-between bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex-shrink-0">
      <div class="flex items-center gap-4">
        <div class="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
           <el-icon :size="20"><Monitor /></el-icon>
        </div>
        <div>
           <h1 class="text-lg font-bold text-gray-800">第一会议室 A101</h1>
           <p class="text-xs text-gray-500">最大容量 50人 · 支持投影仪 · 白板</p>
        </div>
      </div>
      
      <div class="flex items-center gap-3">
         <el-button-group>
            <el-button :icon="ArrowLeft" circle size="small" @click="changeDate(-1)" />
            <el-date-picker
              v-model="currentDate"
              type="date"
              placeholder="选择日期"
              format="YYYY年MM月DD日"
              value-format="YYYY-MM-DD"
              :clearable="false"
              class="!w-[160px] mx-2"
              @change="fetchData"
            />
            <el-button :icon="ArrowRight" circle size="small" @click="changeDate(1)" />
         </el-button-group>
         <el-button type="primary" plain size="small" @click="goToToday">今天</el-button>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="flex flex-1 gap-5 min-h-0 overflow-hidden">
       <!-- 左侧：预约列表视图 (65%) -->
       <div class="w-[65%] bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col overflow-hidden relative group">
          <div class="p-4 border-b border-gray-50 flex items-center justify-between bg-white z-10 sticky top-0">
             <span class="font-bold text-gray-700">今日预约列表</span>
             <div class="flex items-center gap-4 text-xs">
                <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-md bg-indigo-100 border border-indigo-200"></span>他人预约</div>
                <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-md bg-emerald-100 border border-emerald-200"></span>我的预约</div>
             </div>
          </div>

          <div class="flex-1 overflow-y-auto custom-scrollbar p-5">
             <div v-if="bookings.length === 0" class="flex flex-col items-center justify-center h-64 text-gray-400">
                <el-icon :size="48" class="mb-3 opacity-20"><Calendar /></el-icon>
                <p>该日期暂无预约记录</p>
             </div>

             <div v-else class="space-y-3">
                <div v-for="booking in bookings" :key="booking.id"
                     class="flex items-center justify-between p-4 rounded-xl border transition-all hover:shadow-md group/card"
                     :class="isMyBooking(booking) ? 'bg-emerald-50/50 border-emerald-100' : 'bg-white border-gray-100 hover:border-indigo-100 hover:bg-indigo-50/10'"
                >
                   <div class="flex items-center gap-6">
                      <!-- 时间信息 -->
                      <div class="flex flex-col items-center min-w-[100px] border-r border-gray-100 pr-6">
                         <span class="text-lg font-bold font-mono text-gray-700">{{ booking.start_time }}</span>
                         <div class="w-0.5 h-3 bg-gray-200 my-1 rounded-full"></div>
                         <span class="text-sm font-medium text-gray-400 font-mono">{{ booking.end_time }}</span>
                      </div>

                      <!-- 用户信息 -->
                      <div class="flex flex-col gap-1">
                         <div class="flex items-center gap-2">
                             <el-avatar :size="28" :class="isMyBooking(booking) ? '!bg-emerald-100 !text-emerald-600' : '!bg-indigo-100 !text-indigo-600'" class="!text-xs font-bold">
                                {{ booking.user_name ? booking.user_name.charAt(0) : 'U' }}
                             </el-avatar>
                             <span class="font-bold text-gray-800">{{ booking.user_name }}</span>
                             <span class="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-500">{{ booking.user_dept || '部门' }}</span>
                         </div>
                         <div class="text-sm text-gray-500 flex items-center gap-2">
                            <span v-if="booking.remarks" class="truncate max-w-[300px]">{{ booking.remarks }}</span>
                            <span v-else class="italic text-gray-300 text-xs">暂无备注</span>
                         </div>
                      </div>
                   </div>

                   <!-- 操作按钮 -->
                   <div class="flex items-center gap-3">
                      <div class="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded">{{ booking.num_people }}人</div>
                      
                      <el-popconfirm 
                          v-if="isMyBooking(booking)"
                          title="确认取消此预约?" 
                          @confirm="handleCancel(booking.id)"
                          width="200"
                          confirm-button-text="确认取消"
                          cancel-button-text="暂不"
                          confirm-button-type="danger"
                      >
                        <template #reference>
                            <el-button type="danger" plain circle size="small" class="opacity-0 group-hover/card:opacity-100 transition-opacity">
                                <el-icon><Delete /></el-icon>
                            </el-button>
                        </template>
                      </el-popconfirm>
                   </div>
                </div>
             </div>
          </div>
       </div>

       <!-- 右侧：预约表单 (35%) -->
       <div class="w-[35%] flex flex-col gap-5">
           <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex-1 flex flex-col">
              <h2 class="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
                 <span class="w-1 h-5 bg-indigo-600 rounded-full"></span>
                 预约申请
              </h2>

              <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="flex-1 flex flex-col" :disabled="loading">
                 <el-form-item label="预约日期">
                    <div class="w-full px-3 py-2 bg-gray-50 rounded-lg text-gray-500 text-sm font-bold border border-gray-200">
                        {{ currentDateFormatted }}
                    </div>
                 </el-form-item>

                 <div class="grid grid-cols-2 gap-4">
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
import { Monitor, ArrowLeft, ArrowRight, Delete, Calendar } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import isBetween from 'dayjs/plugin/isBetween'
import { ElMessage } from 'element-plus'
import { getBookings, createBooking, cancelBooking } from '@/api/booking'
import { useUserStore } from '@/store/user'

dayjs.extend(isBetween)

const userStore = useUserStore()
const currentDate = ref(dayjs().format('YYYY-MM-DD'))
const bookings = ref([])
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

// 检查是否是我的预约
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

const submitBooking = async () => {
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
        } else {
            ElMessage.error(res.msg || '取消失败')
        }
    } catch (err) {
        ElMessage.error('系统错误')
    }
}

onMounted(() => {
    fetchData()
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