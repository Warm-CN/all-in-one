<template>
  <div class="h-full flex flex-col">
    <!-- 主体内容 -->
    <div class="flex-1 overflow-auto p-3 sm:p-4 lg:p-6">
      <section class="mb-4 rounded-2xl border border-slate-200 bg-white px-4 py-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.22)] sm:px-6 sm:py-6">
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600 shadow-sm">
            <el-icon :size="16"><UserFilled /></el-icon>
          </div>
          <div>
            <span class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-[11px] font-semibold tracking-[0.18em] text-blue-600">MEMBERS</span>
            <h2 class="mt-1 text-2xl font-bold text-slate-800">成员管理</h2>
          </div>
        </div>
      </section>
      <el-tabs v-model="activeTab" class="custom-tabs">
        <!-- 入社审批 -->
        <el-tab-pane label="入社审批" name="approval">
          <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm sm:p-5 lg:p-6">
            <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div class="flex items-center gap-2">
                <span class="text-base font-bold text-gray-700">待审核用户</span>
                <el-tag type="warning" size="small" round>{{ pendingUsers.length }}</el-tag>
              </div>
              <el-button 
                type="primary" 
                :disabled="selectedPendingIds.length === 0"
                @click="batchApprove"
                class="!w-full !rounded-xl sm:!w-auto"
              >
                批量通过 ({{ selectedPendingIds.length }})
              </el-button>
            </div>

            <div class="overflow-x-auto">
              <el-table 
                :data="pendingUsers" 
                @selection-change="handleSelectionChange"
                class="custom-table"
                style="width: 100%; min-width: 940px"
              >
                <el-table-column type="selection" width="55" />
                <el-table-column prop="real_name" label="姓名" min-width="100" />
                <el-table-column prop="student_id" label="学号" min-width="120" />
                <el-table-column prop="phone" label="手机号" min-width="130" />
                <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
                <el-table-column prop="department" label="部门" min-width="120" />
                <el-table-column label="申请时间" min-width="160">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="220" fixed="right">
                  <template #default="{ row }">
                    <div class="flex flex-wrap gap-2">
                      <el-button type="success" size="small" @click="approveUser(row.id)" class="!rounded-lg">
                        通过
                      </el-button>
                      <el-button type="danger" size="small" plain @click="rejectUser(row.id)" class="!rounded-lg">
                        拒绝
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
                <template #empty>
                  <div class="py-8 text-center text-gray-400">
                    <el-icon :size="48" class="mb-3"><CircleCheck /></el-icon>
                    <p>暂无待审核用户</p>
                  </div>
                </template>
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <!-- 成员维护 -->
        <el-tab-pane label="成员维护" name="members">
          <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm sm:p-5 lg:p-6">
            <!-- 搜索和筛选 -->
            <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索姓名或学号..."
                clearable
                @clear="fetchMembers"
                @keyup.enter="fetchMembers"
                class="w-full sm:!w-80"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              
              <el-select
                v-model="selectedDepartment"
                placeholder="选择部门"
                clearable
                @change="fetchMembers"
                class="w-full sm:!w-48"
              >
                <el-option label="全部部门" value="" />
                <el-option label="科创部" value="科创部" />
                <el-option label="新媒体" value="新媒体" />
                <el-option label="宣传部" value="宣传部" />
                <el-option label="组织部" value="组织部" />
                <el-option label="外联部" value="外联部" />
                <el-option label="常委" value="常委" />
              </el-select>

              <el-button type="primary" @click="fetchMembers" class="!w-full !rounded-xl sm:!w-auto">
                <el-icon class="mr-1"><Search /></el-icon>
                查询
              </el-button>
            </div>

            <!-- 成员列表 -->
            <div class="w-full overflow-x-auto">
              <el-table :data="activeMembers" class="custom-table" style="width: 100%; min-width: 980px;">
                <el-table-column prop="real_name" label="姓名" min-width="100" fixed="left" />
                <el-table-column prop="student_id" label="学号" min-width="120" />
                <el-table-column prop="department" label="部门" min-width="120" />
                <el-table-column prop="position" label="职位" min-width="120">
                  <template #default="{ row }">
                    {{ row.position || '-' }}
                  </template>
                </el-table-column>
                <el-table-column label="角色" width="100">
                  <template #default="{ row }">
                    <el-tag v-if="row.role === 'admin'" type="danger" size="small" round>Admin</el-tag>
                    <el-tag v-else type="success" size="small" round>Member</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="phone" label="手机号" min-width="130" />
                <el-table-column label="操作" width="340" fixed="right">
                  <template #default="{ row }">
                    <div class="flex flex-wrap gap-2">
                      <el-button 
                        type="warning" 
                        size="small" 
                        plain
                        @click="showResetPasswordDialog(row)"
                        class="!rounded-lg"
                      >
                        重置密码
                      </el-button>
                      <el-button 
                        v-if="row.role !== 'admin'"
                        type="primary" 
                        size="small"
                        @click="promoteToAdmin(row)"
                        class="!rounded-lg"
                      >
                        设为管理员
                      </el-button>
                      <el-popconfirm
                        title="确认移出该成员？"
                        @confirm="removeUser(row.id)"
                        width="200"
                      >
                        <template #reference>
                          <el-button type="danger" size="small" plain class="!rounded-lg">
                            移出社团
                          </el-button>
                        </template>
                      </el-popconfirm>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div v-if="activeMembers.length === 0" class="text-center py-16 text-gray-400">
              <el-icon :size="48" class="mb-3"><UserFilled /></el-icon>
              <p>暂无成员</p>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

      <el-dialog
        v-model="resetPasswordDialogVisible"
        title="重置密码"
        width="400px"
        :close-on-click-modal="false"
        class="custom-dialog !rounded-2xl"
      >
      <div class="text-center py-6">
        <el-icon :size="64" color="#faad14" class="mb-4"><Warning /></el-icon>
        <p class="text-base text-gray-700 mb-2">确认重置以下用户的密码？</p>
        <p class="text-lg font-bold text-gray-800 mb-4">{{ currentUser?.real_name }} ({{ currentUser?.student_id }})</p>
        <el-alert type="warning" :closable="false" show-icon class="!rounded-xl">
            <template #default>
              <div class="flex flex-col">
                  <span class="font-bold">密码将被重置为随机生成的8位强密码</span>
                  <span class="text-xs mt-1">请重置后在弹窗中复制并保存</span>
              </div>
            </template>
        </el-alert>
      </div>
      <template #footer>
        <div class="flex flex-col justify-center gap-3 sm:flex-row">
          <el-button @click="resetPasswordDialogVisible = false" class="!rounded-xl">取消</el-button>
          <el-button type="primary" @click="confirmResetPassword" class="!rounded-xl">确认重置</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 重置成功弹窗 -->
    <el-dialog
      v-model="resetSuccessVisible"
      title="重置成功"
      width="400px"
      :close-on-click-modal="false"
      class="custom-dialog !rounded-2xl"
      center
      align-center
    >
      <div class="text-center py-4">
        <div class="mb-4 flex justify-center">
            <div class="w-16 h-16 bg-green-50 text-green-500 rounded-full flex items-center justify-center">
                <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
        </div>
        <p class="text-gray-600 mb-4">请务必记录新密码，点击下方密码可复制</p>
        
        <div 
            class="bg-gray-50 border border-gray-200 rounded-xl p-4 cursor-pointer hover:bg-gray-100/80 hover:border-indigo-200 transition-all group relative"
            @click="copyPassword"
        >
            <p class="font-mono text-2xl font-bold text-indigo-600 tracking-wider select-all">{{ newPassword }}</p>
            <div class="absolute inset-0 flex items-center justify-center bg-black/5 opacity-0 group-hover:opacity-100 rounded-xl transition-opacity">
                <span class="text-xs font-bold text-gray-600 bg-white/90 px-2 py-1 rounded shadow-sm">点击复制</span>
            </div>
        </div>
        
        <p class="text-xs text-gray-400 mt-4">点击确定后可以通过修改密码功能更改</p>
      </div>
      <template #footer>
        <div class="flex justify-center">
          <el-button type="primary" size="large" @click="resetSuccessVisible = false" class="!w-full !rounded-xl !px-8 sm:!w-auto">我已记录</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Search, CircleCheck, UserFilled, Warning } from '@element-plus/icons-vue'
import request from '@/utils/request'
import dayjs from 'dayjs'

const activeTab = ref('approval')
const pendingUsers = ref([])
const activeMembers = ref([])
const selectedPendingIds = ref([])
const searchKeyword = ref('')
const selectedDepartment = ref('')
const resetPasswordDialogVisible = ref(false)
const resetSuccessVisible = ref(false)
const newPassword = ref('')
const currentUser = ref(null)

// 复制密码
const copyPassword = async () => {
  if (!newPassword.value) return
  
  // 优先尝试使用 Clipboard API
  if (navigator.clipboard && window.isSecureContext) {
    try {
        await navigator.clipboard.writeText(newPassword.value)
        ElMessage.success('密码已复制到剪贴板')
        return
    } catch (err) {
        console.error('Clipboard API failed:', err)
    }
  }

  // 降级使用 document.execCommand
  try {
    const textArea = document.createElement("textarea")
    textArea.value = newPassword.value
    
    // 确保 textarea 不可见 but part of DOM
    textArea.style.position = "fixed"
    textArea.style.left = "-9999px"
    textArea.style.top = "0"
    
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    const successful = document.execCommand('copy')
    document.body.removeChild(textArea)
    
    if (successful) {
      ElMessage.success('密码已复制到剪贴板')
    } else {
      ElMessage.info('请手动复制')
    }
  } catch (err) {
    console.error('Fallback copy failed:', err)
    ElMessage.info('请手动复制')
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

// 获取待审核用户
const fetchPendingUsers = async () => {
  try {
    const res = await request({
      url: '/api/admin/users/pending',
      method: 'get'
    })
    if (res.code === 200) {
      pendingUsers.value = res.data
    }
  } catch (err) {
    ElMessage.error('获取待审核用户失败')
  }
}

// 获取成员列表
const fetchMembers = async () => {
  try {
    const res = await request({
      url: '/api/admin/users',
      method: 'get',
      params: {
        status: 'active',
        keyword: searchKeyword.value || undefined,
        department: selectedDepartment.value || undefined
      }
    })
    if (res.code === 200) {
      activeMembers.value = res.data
    }
  } catch (err) {
    ElMessage.error('获取成员列表失败')
  }
}

// 多选变化
const handleSelectionChange = (selection) => {
  selectedPendingIds.value = selection.map(item => item.id)
}

// 批量通过
const batchApprove = async () => {
  try {
    const res = await request({
      url: '/api/admin/users/approve',
      method: 'post',
      data: selectedPendingIds.value
    })
    if (res.code === 200) {
      ElMessage.success(res.msg)
      selectedPendingIds.value = []
      fetchPendingUsers()
      fetchMembers()
    }
  } catch (err) {
    ElMessage.error('批量审核失败')
  }
}

// 单个通过
const approveUser = async (userId) => {
  try {
    const res = await request({
      url: `/api/admin/users/approve/${userId}`,
      method: 'post'
    })
    if (res.code === 200) {
      ElMessage.success(res.msg)
      fetchPendingUsers()
      fetchMembers()
    }
  } catch (err) {
    ElMessage.error('审核失败')
  }
}

// 拒绝
const rejectUser = async (userId) => {
  try {
    await ElMessageBox.confirm('确认拒绝该用户的入社申请？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await request({
      url: `/api/admin/users/reject/${userId}`,
      method: 'post'
    })
    if (res.code === 200) {
      ElMessage.success(res.msg)
      fetchPendingUsers()
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 显示重置密码弹窗
const showResetPasswordDialog = (user) => {
  currentUser.value = user
  resetPasswordDialogVisible.value = true
}

// 确认重置密码
const confirmResetPassword = async () => {
  try {
    const res = await request({
      url: '/api/admin/users/reset-password',
      method: 'post',
      params: { user_id: currentUser.value.id }
    })
    if (res.code === 200) {
      resetPasswordDialogVisible.value = false
      newPassword.value = res.data.new_password
      resetSuccessVisible.value = true
    }
  } catch (err) {
    ElMessage.error('重置密码失败')
  }
}

// 提升为管理员
const promoteToAdmin = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确认将 ${user.real_name} 提升为管理员？`,
      '提示',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await request({
      url: '/api/admin/users/promote',
      method: 'post',
      params: { user_id: user.id }
    })
    if (res.code === 200) {
      ElMessage.success(res.msg)
      fetchMembers()
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 移出社团
const removeUser = async (userId) => {
  try {
    const res = await request({
      url: `/api/admin/users/${userId}`,
      method: 'delete'
    })
    if (res.code === 200) {
      ElMessage.success(res.msg)
      fetchMembers()
    }
  } catch (err) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchPendingUsers()
  fetchMembers()
})
</script>

<style scoped>
/* 自定义 Tabs */
:deep(.el-tabs__header) {
  margin: 0;
  border: none;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 600;
  color: #94a3b8;
  padding: 0 24px;
  height: 48px;
  line-height: 48px;
}

:deep(.el-tabs__item.is-active) {
  color: #4f46e5;
}

:deep(.el-tabs__active-bar) {
  height: 3px;
  background: linear-gradient(90deg, #4f46e5, #6366f1);
  border-radius: 3px 3px 0 0;
}

/* 自定义表格 */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  font-size: 13px;
  border: none;
}

:deep(.el-table td.el-table__cell) {
  border: none;
  padding: 16px 0;
}

:deep(.el-table__body tr:hover > td) {
  background-color: #f8fafc !important;
}

:deep(.el-table__row) {
  border-bottom: 1px solid #f1f5f9;
}

/* 自定义弹窗 */
:deep(.el-dialog) {
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
}

:deep(.el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

:deep(.el-dialog__body) {
  padding: 0 24px;
}

:deep(.el-dialog__footer) {
  padding: 20px 24px;
  border-top: 1px solid #f1f5f9;
}

@media (max-width: 640px) {
  :deep(.el-tabs__item) {
    padding: 0 14px;
    font-size: 14px;
  }
}
</style>
