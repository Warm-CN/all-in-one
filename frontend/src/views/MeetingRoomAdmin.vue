<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="flex flex-col gap-3 border-b border-gray-100 bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-end sm:px-6">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
        <el-date-picker
          v-model="exportMonth"
          type="month"
          placeholder="选择导出月份"
          class="w-full sm:!w-[160px]"
          :clearable="false"
          format="YYYY年MM月"
          value-format="YYYY-MM"
        />
        <el-button type="primary" :loading="exportLoading" @click="handleExport" class="!w-full !rounded-md sm:!w-auto">
          <el-icon class="mr-1"><Download /></el-icon>
          导出表格
        </el-button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-hidden p-3 sm:p-4 lg:p-6">
        <div class="flex h-full flex-col rounded-2xl border border-gray-100 bg-white shadow-sm">
          <!-- Filters/Tabs -->
           <div class="flex flex-col gap-3 border-b border-gray-100 p-4 lg:flex-row lg:items-center lg:justify-between">
             <div class="text-gray-600 text-sm">
                当前显示: <span class="font-medium text-gray-900">{{ formatDate(startDate) }}</span> 至 <span class="font-medium text-gray-900">{{ formatDate(endDate) }}</span>
                (共 {{ bookings.length }} 条记录)
             </div>
             
             <el-radio-group v-model="viewRange" size="small" @change="fetchBookings" class="admin-booking-radios">
                <el-radio-button label="all">近15天</el-radio-button>
                <el-radio-button label="past">过去7天</el-radio-button>
                <el-radio-button label="today">今天</el-radio-button>
                <el-radio-button label="future">未来7天</el-radio-button>
             </el-radio-group>
           </div>
           
           <!-- Table -->
           <div class="min-h-0 flex-1 overflow-x-auto">
             <el-table 
               v-loading="loading" 
               :data="bookings" 
               class="custom-table min-h-0"
               height="100%"
               stripe
               style="min-width: 860px"
             >
              <el-table-column prop="booking_date" label="日期" width="120" sortable fixed="left">
                 <template #default="{ row }">
                   <div :class="getDateClass(row.booking_date)">
                     {{ row.booking_date }}
                   </div>
                 </template>
              </el-table-column>
              <el-table-column label="时间段" width="140">
                <template #default="{ row }">
                  <span class="font-medium font-mono text-gray-700">
                    {{ row.start_time }} - {{ row.end_time }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="user_name" label="预约人" width="120" show-overflow-tooltip/>
              <el-table-column prop="user_dept" label="部门" width="120" show-overflow-tooltip/>
              <el-table-column prop="num_people" label="人数" width="80" align="center" />
              <el-table-column prop="remarks" label="备注" min-width="150" show-overflow-tooltip />
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="{ row }">
                  <el-popconfirm
                    title="确定要删除这条预约吗？"
                    confirm-button-text="删除"
                    cancel-button-text="取消"
                    confirm-button-type="danger"
                    @confirm="handleDelete(row)"
                  >
                    <template #reference>
                      <el-button type="danger" link size="small">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </template>
                  </el-popconfirm>
                </template>
              </el-table-column>
             </el-table>
           </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminBookings, exportBookings, cancelBooking } from '@/api/booking'
import { ElMessage } from 'element-plus'
import { Calendar, Download, Delete } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import isBetween from 'dayjs/plugin/isBetween'

dayjs.extend(isBetween)

const loading = ref(false)
const exportLoading = ref(false)
const bookings = ref([])
const exportMonth = ref(dayjs().format('YYYY-MM'))
const viewRange = ref('all')

const startDate = ref('')
const endDate = ref('')

const fetchBookings = async () => {
  loading.value = true
  try {
    const today = dayjs()
    let start, end
    
    // User requested: "past 7 days, today, and future week"
    // 'all' combines them: -7 to +7 = 15 days roughly
    
    if (viewRange.value === 'all') {
       start = today.subtract(7, 'day')
       end = today.add(7, 'day')
    } else if (viewRange.value === 'past') {
       start = today.subtract(7, 'day')
       end = today.subtract(1, 'day')
    } else if (viewRange.value === 'today') {
       start = today
       end = today
    } else if (viewRange.value === 'future') {
       start = today.add(1, 'day')
       end = today.add(7, 'day')
    }
    
    startDate.value = start
    endDate.value = end
    
    const res = await getAdminBookings(start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'))
    bookings.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleExport = async () => {
  if (!exportMonth.value) return
  
  exportLoading.value = true
  try {
    const d = dayjs(exportMonth.value)
    const res = await exportBookings(d.year(), d.month() + 1)
    
    // Download logic
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `会议室预约_${d.format('YYYY年MM月')}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('导出失败')
  } finally {
    exportLoading.value = false
  }
}

const handleDelete = async (row) => {
    try {
        await cancelBooking(row.id)
        ElMessage.success('删除成功')
        fetchBookings()
    } catch (error) {
        // Error handling mostly done in request interceptor
    }
}

const formatDate = (d) => {
    return dayjs(d).format('YYYY-MM-DD')
}

const getDateClass = (dateStr) => {
    const d = dayjs(dateStr)
    const today = dayjs().startOf('day')
    if (d.isSame(today, 'day')) return 'text-blue-600 font-bold'
    if (d.isBefore(today, 'day')) return 'text-gray-500'
    return 'text-green-600'
}

onMounted(() => {
  fetchBookings()
})
</script>

<style scoped>
.custom-table :deep(th.el-table__cell) {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.admin-booking-radios {
  display: flex;
  flex-wrap: wrap;
}
</style>
