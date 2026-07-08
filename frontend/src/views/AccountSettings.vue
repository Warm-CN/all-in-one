<template>
  <div class="animate-fade-in-up flex h-full flex-col gap-6">
    <!-- 顶部标题 -->
    <div class="flex items-center justify-between shrink-0">
      <div class="flex items-center gap-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 shadow-sm">
          <el-icon :size="16"><Setting /></el-icon>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-800 tracking-tight">账号设置</h1>
          <p class="text-gray-500 mt-1 text-sm">管理您的个人信息和安全设置</p>
        </div>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="custom-scrollbar flex-1 overflow-y-auto rounded-[24px] border border-gray-100/60 bg-white p-4 shadow-sm sm:p-6 lg:p-8">
      <div class="max-w-4xl mx-auto">
        <el-tabs v-model="activeTab" class="custom-tabs">
          <!-- 个人资料 -->
          <el-tab-pane label="个人资料" name="profile">
            <div class="pt-6">
              <el-form :model="profileForm" ref="profileFormRef" label-position="top" class="grid grid-cols-1 gap-5 md:grid-cols-2 md:gap-6">
                
                <!-- 头像区域 (仅展示) -->
                <div class="mb-4 flex flex-col gap-4 md:col-span-2 sm:flex-row sm:items-center sm:gap-6">
                  <div class="relative group">
                    <el-avatar :size="80" class="!bg-indigo-100 !text-indigo-600 !text-2xl !font-bold ring-4 ring-white shadow-lg">
                      {{ userStore.userName?.charAt(0) || 'U' }}
                    </el-avatar>
                  </div>
                  <div>
                    <h3 class="font-bold text-gray-800 text-lg">{{ userStore.userName }}</h3>
                    <p class="text-gray-500 text-sm mt-1">{{ userStore.studentId }}</p>
                  </div>
                </div>

                <el-form-item label="真实姓名" prop="full_name">
                  <el-input v-model="profileForm.full_name" placeholder="请输入真实姓名" disabled />
                </el-form-item>

                <el-form-item label="手机号码" prop="phone">
                  <el-input v-model="profileForm.phone" placeholder="请输入手机号码" />
                </el-form-item>

                <el-form-item label="电子邮箱" prop="email">
                  <el-input v-model="profileForm.email" placeholder="请输入电子邮箱" />
                </el-form-item>
                
                 <el-form-item label="所属部门" prop="department">
                    <el-select v-model="profileForm.department" placeholder="请选择部门" class="w-full">
                        <el-option 
                          v-for="dept in departments" 
                          :key="dept" 
                          :label="dept" 
                          :value="dept" 
                        />
                      </el-select>
                </el-form-item>
                
                 <el-form-item label="职位" prop="position">
                    <el-select 
                        v-model="profileForm.position" 
                        placeholder="请选择职位" 
                        class="w-full"
                        :disabled="!profileForm.department"
                      >
                         <el-option 
                           v-for="pos in positionOptions" 
                           :key="pos" 
                           :label="pos" 
                           :value="pos" 
                         />
                      </el-select>
                </el-form-item>

                <div class="md:col-span-2 flex justify-end pt-4">
                   <el-button type="primary" :loading="loading" @click="handleUpdateProfile" class="!h-10 !w-full !rounded-xl !px-8 text-sm font-bold shadow-md shadow-indigo-100 sm:!w-auto">
                     保存更改
                   </el-button>
                </div>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- 安全设置 -->
          <el-tab-pane label="密码安全" name="security">
             <div class="max-w-lg pt-6">
                <el-alert
                  title="为了保障您的账号安全，建议定期更换密码且设置高强度密码。"
                  type="info"
                  show-icon
                  :closable="false"
                  class="mb-6 !rounded-xl"
                />
                
                <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-position="top">
                  <el-form-item label="当前密码" prop="old_password">
                    <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入当前使用密码" />
                  </el-form-item>

                  <el-form-item label="新密码" prop="new_password">
                    <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码（至少6位）" />
                  </el-form-item>

                  <el-form-item label="确认新密码" prop="confirm_password">
                    <el-input v-model="passwordForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
                  </el-form-item>

                  <div class="flex justify-end pt-4">
                     <el-button type="warning" :loading="pwdLoading" @click="handleChangePassword" class="!h-10 !w-full !rounded-xl !px-8 text-sm font-bold shadow-md shadow-orange-100 sm:!w-auto">
                       修改密码
                     </el-button>
                  </div>
                </el-form>
             </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useUserStore } from '@/store/user'
import { updateProfile } from '@/api/user'
import { changePassword, getCurrentUser } from '@/api/auth'
import { ElMessage } from 'element-plus'
import { Setting } from '@element-plus/icons-vue'

const userStore = useUserStore()
const activeTab = ref('profile')
const loading = ref(false)
const pwdLoading = ref(false)

// 部门定义
const departments = [
  '科创部',
  '新媒体',
  '宣传部',
  '组织部',
  '外联部',
  '常委'
]

// 个人资料表单
const profileFormRef = ref(null)
const profileForm = reactive({
  full_name: '',
  phone: '',
  email: '',
  department: '',
  position: ''
})

// 职位联动逻辑
const positionOptions = computed(() => {
  if (!profileForm.department) return []
  
  if (profileForm.department === '常委') {
    return ['会长', '副会长', '技术总监', '信息总监']
  } else {
    return ['部长', '副部长', '干事']
  }
})

// 监听部门变化，重置职位 (仅当非初始加载导致的变动才重置，这里简单处理，实际需要注意初始化)
// 注意：初始化时也会触发 watch，需要与 fetchUserInfo 配合
// 为了避免 fetchUserInfo 更新 department 时清空 position，我们可以加个标志位或者简化处理
// 简化处理：从界面上手动改变 department 时才应该清除 position。
// 由于 watch 是深度的或立即的（如果设置了 immediate）。默认 watch 改动才触发。
// fetchUserInfo 是异步的，修改 profileForm.department 会触发 watch。
// 我们可以在 watch 里判断一下，如果新的 positionOptions 不包含当前 position，才清空。
watch(() => profileForm.department, (newVal, oldVal) => {
  // 如果是初始化（oldVal 为空字符串或 undefined 且 newVal 有值），通常不应该清空，
  // 但这里 fetchUserInfo 是依次赋值。
  // 更好的方式：判断当前 position 是否在新的 options 里
  if (newVal) {
     let options = []
     if (newVal === '常委') {
        options = ['会长', '副会长', '技术总监', '信息总监']
     } else {
        options = ['部长', '副部长', '干事']
     }
     
     if (profileForm.position && !options.includes(profileForm.position)) {
        profileForm.position = ''
     }
  } else {
     profileForm.position = ''
  }
})

// 密码表单

// 密码表单
const passwordFormRef = ref(null)
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPwd = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入密码不一致!'));
  } else {
    callback();
  }
};

const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirm_password: [{ validator: validateConfirmPwd, trigger: 'blur' }]
}

// 初始化数据
onMounted(async () => {
  // 从 Store 或 API 获取最新数据
  await fetchUserInfo()
})

const fetchUserInfo = async () => {
    try {
        const res = await getCurrentUser()
        if (res.code === 200) {
            const user = res.data
            profileForm.full_name = user.full_name
            profileForm.phone = user.phone
            profileForm.email = user.email
            profileForm.department = user.department
            profileForm.position = user.position
            // 更新 Store
            userStore.setUserInfo(user)
        }
    } catch (e) {
        console.error(e)
    }
}

// 更新资料
const handleUpdateProfile = async () => {
  loading.value = true
  try {
    const res = await updateProfile(profileForm)
    if (res.code === 200) {
      ElMessage.success('个人信息更新成功')
      userStore.setUserName(profileForm.full_name)
      await fetchUserInfo()
    }
  } catch (e) {
    // 错误已经在 request 拦截器中统一处理，这里不再重复提示
    console.error('更新失败:', e)
  } finally {
    loading.value = false
  }
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      pwdLoading.value = true
      try {
        const res = await changePassword(passwordForm.old_password, passwordForm.new_password)
        if (res.code === 200) {
          ElMessage.success('密码修改成功，请重新登录')
          // 清空表单
          passwordForm.old_password = ''
          passwordForm.new_password = ''
          passwordForm.confirm_password = ''
          // 延迟1秒后登出并跳转
          setTimeout(() => {
            userStore.logout()
          }, 1000)
        }
      } catch (e) {
        // 错误已经在 request 拦截器中统一处理
        console.error('修改失败:', e)
      } finally {
        pwdLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.5s ease-out;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.el-tabs__nav-wrap::after) {
    background-color: transparent;
}
:deep(.el-tabs__item) {
    font-size: 15px;
    font-weight: 500;
    color: #64748b;
}
:deep(.el-tabs__item.is-active) {
    color: #4f46e5;
    font-weight: 700;
}
:deep(.el-tabs__active-bar) {
    background-color: #4f46e5;
    height: 3px;
    border-radius: 1.5px;
}

@media (max-width: 640px) {
  :deep(.el-tabs__item) {
    padding-left: 14px;
    padding-right: 14px;
    font-size: 14px;
  }
}
</style>
