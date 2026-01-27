<template>
  <div class="min-h-screen w-full flex items-center justify-center p-4 perspective-container">
    
    <!-- 卡片容器：控制尺寸平滑过渡 -->
    <div 
      class="relative transition-all duration-700 cubic-bezier-smooth"
      :style="{
        width: isFlipped ? '780px' : '440px',
        height: isFlipped ? '680px' : '640px'
      }"
    >
      <!-- 翻转容器 -->
      <div 
        class="w-full h-full relative preserve-3d transition-transform duration-700 shadow-2xl rounded-[24px]" 
        :class="{ 'rotate-y-180': isFlipped }"
      >
        
        <!-- =======================
             正面：登录 (Login)
             ======================= -->
        <div class="absolute inset-0 backface-hidden bg-white/95 backdrop-blur-2xl rounded-[24px] border border-white/60 p-10 flex flex-col items-center shadow-xl overflow-hidden z-20">
          
          <!-- 顶部 Logo -->
          <div class="mt-4 mb-8 flex flex-col items-center">
            <div class="w-24 h-24 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-[2rem] flex items-center justify-center shadow-xl shadow-blue-500/20 mb-4 transform hover:scale-105 transition-transform duration-300 ring-4 ring-blue-50">
              <el-icon class="text-white text-5xl"><Monitor /></el-icon>
            </div>
            <h1 class="text-3xl font-extrabold text-slate-800 tracking-tight">社团通行证</h1>
            <p class="text-slate-400 text-sm mt-2 tracking-[0.2em] uppercase font-medium">Club Passport</p>
          </div>

          <!-- 登录表单 -->
          <form @submit.prevent="handleLogin" class="w-full flex flex-col gap-8 px-4">
            <div class="flex flex-col gap-5">
              <el-input 
                v-model="loginForm.studentId" 
                placeholder="请输入学号 / Student ID" 
                class="!h-12 text-lg custom-input"
              >
                <template #prefix>
                  <el-icon class="text-slate-400 text-2xl ml-2"><User /></el-icon>
                </template>
              </el-input>

              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="请输入密码 / Password" 
                show-password
                class="!h-12 text-lg custom-input"
              >
                <template #prefix>
                  <el-icon class="text-slate-400 text-2xl ml-2"><Lock /></el-icon>
                </template>
              </el-input>
            </div>

            <el-button 
              type="primary" 
              class="w-full !h-12 !text-lg !font-bold !rounded-2xl !shadow-lg !shadow-blue-500/20 hover:!shadow-blue-500/40 transition-all" 
              :loading="loading"
              @click="handleLogin"
            >
              立即登录
            </el-button>
          </form>

          <!-- 底部切换 -->
          <div class="mt-auto mb-4 text-center">
            <span class="text-slate-400 text-base">内部人员录入？</span>
            <button 
              @click="toggleFlip" 
              class="text-blue-600 font-bold hover:text-blue-700 hover:underline ml-1 text-base transition-colors"
            >
              填写档案 &rarr;
            </button>
          </div>


          <!-- 背景装饰 -->
          <div class="absolute -bottom-20 -right-20 w-64 h-64 bg-blue-100 rounded-full blur-3xl opacity-50 pointer-events-none"></div>
          <div class="absolute -top-20 -left-20 w-64 h-64 bg-indigo-100 rounded-full blur-3xl opacity-50 pointer-events-none"></div>
        </div>

        <!-- =======================
             背面：注册申请表 (Register)
             ======================= -->
        <div class="absolute inset-0 backface-hidden bg-white/95 backdrop-blur-xl rounded-[24px] border border-white/50 p-0 flex flex-col shadow-lg overflow-hidden rotate-y-180 z-10">
          
          <!-- 头部标题栏 -->
          <div class="px-10 py-6 border-b border-slate-100 bg-slate-50/80 flex justify-between items-center backdrop-blur-sm shrink-0">
             <div>
               <h2 class="text-2xl font-extrabold text-slate-800 tracking-tight">内部档案录入</h2>
               <p class="text-slate-400 text-xs mt-1 font-medium tracking-wide">INTERNAL MEMBER REGISTRATION</p>
             </div>
             <div class="w-12 h-12 bg-white rounded-2xl border border-slate-200 flex items-center justify-center shadow-sm">
               <el-icon class="text-blue-600 text-2xl"><Document /></el-icon>
             </div>
          </div>

          <!-- 申请表单内容 -->
          <div class="flex-1 px-10 py-6 overflow-y-auto custom-scrollbar">
             <form class="h-full flex flex-col">
                <!-- Grid 布局 -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-x-12 gap-y-6">
                  
                  <!-- 左侧：基本信息 -->
                  <div class="flex flex-col gap-5">
                    <div class="flex items-center gap-3 pb-2 border-b border-slate-100">
                      <div class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                        <el-icon class="text-blue-600 text-base"><User /></el-icon>
                      </div>
                      <span class="font-bold text-slate-800 text-base tracking-wide">基本信息</span>
                    </div>

                    <div class="form-item">
                      <label class="block text-slate-500 text-xs font-bold mb-1.5 uppercase tracking-wider pl-1">Student ID</label>
                      <el-input v-model="registerForm.studentId" placeholder="请输入学号" class="!h-11 text-base" />
                    </div>

                    <div class="form-item">
                      <label class="block text-slate-500 text-xs font-bold mb-1.5 uppercase tracking-wider pl-1">Full Name</label>
                      <el-input v-model="registerForm.name" placeholder="请输入姓名" class="!h-11 text-base" />
                    </div>

                    <div class="form-item">
                      <label class="block text-slate-500 text-xs font-bold mb-1.5 uppercase tracking-wider pl-1">Mobile Phone</label>
                      <el-input v-model="registerForm.phone" placeholder="请输入手机号" class="!h-11 text-base" />
                    </div>

                    <div class="form-item">
                      <label class="block text-slate-500 text-xs font-bold mb-1.5 uppercase tracking-wider pl-1">Email Address</label>
                      <el-input v-model="registerForm.email" placeholder="请输入邮箱地址" class="!h-11 text-base" />
                    </div>
                  </div>

                  <!-- 右侧：职位与密码 -->
                  <div class="flex flex-col gap-5">
                    <div class="flex items-center gap-3 pb-2 border-b border-slate-100">
                      <div class="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center">
                        <el-icon class="text-indigo-600 text-base"><Suitcase /></el-icon>
                      </div>
                      <span class="font-bold text-slate-800 text-base tracking-wide">职位信息</span>
                    </div>

                    <div class="form-item">
                      <label class="block text-slate-500 text-xs font-bold mb-1.5 uppercase tracking-wider pl-1">Department</label>
                      <el-select v-model="registerForm.department" placeholder="请选择部门" class="w-full !h-11 text-base">
                        <el-option 
                          v-for="dept in departments" 
                          :key="dept" 
                          :label="dept" 
                          :value="dept" 
                        />
                      </el-select>
                    </div>

                    <div class="form-item">
                      <label class="block text-slate-500 text-xs font-bold mb-1.5 uppercase tracking-wider pl-1">Position</label>
                      <el-select 
                        v-model="registerForm.position" 
                        placeholder="请选择职位" 
                        class="w-full !h-11 text-base"
                        :disabled="!registerForm.department"
                      >
                         <el-option 
                           v-for="pos in positionOptions" 
                           :key="pos" 
                           :label="pos" 
                           :value="pos" 
                         />
                      </el-select>
                    </div>

                    <div class="flex items-center gap-3 pb-2 mt-2 border-b border-slate-100">
                      <div class="w-8 h-8 rounded-lg bg-red-50 flex items-center justify-center">
                        <el-icon class="text-red-500 text-base"><Lock /></el-icon>
                      </div>
                      <span class="font-bold text-slate-800 text-base tracking-wide">账户安全</span>
                    </div>

                    <div class="form-item">
                      <label class="block text-slate-500 text-xs font-bold mb-1.5 uppercase tracking-wider pl-1">Set Password</label>
                      <el-input v-model="registerForm.password" type="password" placeholder="设置登录密码" show-password class="!h-11 text-base" />
                    </div>
                  </div>
                </div>

                <!-- 底部说明与按钮 -->
                <div class="mt-auto pt-6 flex items-center justify-between border-t border-slate-100 shrink-0">
                  <button 
                    type="button" 
                    @click="toggleFlip" 
                    class="text-slate-400 hover:text-slate-600 text-base font-medium flex items-center gap-2 transition-colors px-4 py-2 rounded-xl hover:bg-slate-100"
                  >
                    <el-icon><Back /></el-icon> 返回
                  </button>

                  <el-button 
                    type="primary" 
                    class="!px-10 !h-12 !text-lg !font-bold !rounded-2xl !shadow-xl !shadow-blue-500/20"
                    @click="handleRegister"
                  >
                    确认录入档案
                  </el-button>
                </div>
             </form>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor, Document, Suitcase, Back } from '@element-plus/icons-vue'
import { register } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const isFlipped = ref(false)
const loading = ref(false)

const loginForm = reactive({
  studentId: '',
  password: ''
})

const registerForm = reactive({
  studentId: '',
  name: '',
  phone: '',
  email: '',
  department: '',
  position: '',
  password: ''
})

// 部门定义
const departments = [
  '科创部',
  '新媒体',
  '宣传部',
  '组织部',
  '外联部',
  '常委'
]

// 职位联动逻辑
const positionOptions = computed(() => {
  if (!registerForm.department) return []
  
  if (registerForm.department === '常委') {
    return ['会长', '副会长', '技术总监', '信息总监']
  } else {
    return ['部长', '副部长', '干事']
  }
})

// 监听部门变化，重置职位
watch(() => registerForm.department, () => {
  registerForm.position = ''
})

const toggleFlip = () => {
  isFlipped.value = !isFlipped.value
}

const handleLogin = async () => {
  if (!loginForm.studentId || !loginForm.password) {
    ElMessage.warning('请输入学号和密码')
    return
  }
  
  loading.value = true
  try {
    const success = await userStore.login(loginForm.studentId, loginForm.password)
    if (success) {
      ElMessage.success('欢迎回来')
      router.push('/home')
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  // 验证所有必填字段
  if (!registerForm.studentId || !registerForm.name || !registerForm.phone || 
      !registerForm.email || !registerForm.department || !registerForm.position || 
      !registerForm.password) {
    ElMessage.warning('请填写完整所有信息')
    return
  }
  
  loading.value = true
  try {
    const res = await register({
      student_id: registerForm.studentId,
      full_name: registerForm.name,
      phone: registerForm.phone,
      email: registerForm.email,
      department: registerForm.department,
      position: registerForm.position,
      password: registerForm.password
    })
    
    if (res.code === 200) {
      ElMessage.success('注册申请已提交，请等待管理员审核')
      // 清空表单
      Object.assign(registerForm, {
        studentId: '',
        name: '',
        phone: '',
        email: '',
        department: '',
        position: '',
        password: ''
      })
      // 翻转回登录页
      setTimeout(() => {
        toggleFlip()
      }, 1500)
    } else {
      ElMessage.error(res.msg || '注册失败')
    }
  } catch (error) {
    console.error('注册错误:', error)
    ElMessage.error('注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.perspective-container {
  perspective: 2000px; /* 增加视距，使翻转更自然 */
}

.preserve-3d {
  transform-style: preserve-3d;
}

.backface-hidden {
  backface-visibility: hidden;
}

.rotate-y-180 {
  transform: rotateY(180deg);
}

.cubic-bezier-smooth {
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* 覆盖 Element Plus 的一些细节以适配“纸质”感 */
.form-item :deep(.el-input__wrapper) {
  background-color: #f8fafc; /* slate-50 */
  border: 1px solid transparent;
  box-shadow: none !important;
}

.form-item :deep(.el-input__wrapper:hover) {
  background-color: #f1f5f9; /* slate-100 */
}

.form-item :deep(.el-input__wrapper.is-focus) {
  background-color: #ffffff;
  box-shadow: 0 0 0 2px #e2e8f0 !important; /* soft ring */
}
</style>
