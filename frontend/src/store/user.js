/**
 * 用户状态管理 Store
 * 使用 Pinia 管理用户登录状态和信息
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getCurrentUser, logout as logoutApi } from '@/api/auth'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
    // 状态
    const token = ref(localStorage.getItem('token') || '')
    const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

    // 计算属性
    const isLoggedIn = computed(() => !!token.value)
    const userName = computed(() => userInfo.value?.real_name || '')
    const userRole = computed(() => userInfo.value?.role || '')
    const studentId = computed(() => userInfo.value?.student_id || '')

    // 判断是否是管理员
    const isAdmin = computed(() => userRole.value === 'admin')

    // 判断是否是成员（包括管理员）
    const isMember = computed(() => ['member', 'admin'].includes(userRole.value))

    /**
     * 登录
     * @param {string} student_id - 学号
     * @param {string} password - 密码
     */
    const login = async (student_id, password) => {
        try {
            const res = await loginApi(student_id, password)

            if (res.code === 200) {
                // 保存 Token
                token.value = res.data.token.access_token
                localStorage.setItem('token', token.value)

                // 保存用户信息
                userInfo.value = res.data.user
                localStorage.setItem('userInfo', JSON.stringify(userInfo.value))

                return true
            }
            return false
        } catch (error) {
            console.error('登录失败:', error)
            return false
        }
    }

    /**
     * 获取用户信息
     */
    const getUserInfo = async () => {
        try {
            const res = await getCurrentUser()

            if (res.code === 200) {
                userInfo.value = res.data
                localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
                return true
            }
            return false
        } catch (error) {
            console.error('获取用户信息失败:', error)
            return false
        }
    }

    /**
     * 退出登录
     */
    const logout = () => {
        // 清除状态
        token.value = ''
        userInfo.value = null

        // 清除本地存储
        logoutApi()

        // 跳转到登录页
        router.push('/login')
    }

    /**
     * 重置状态（用于 Token 过期等情况）
     */
    const resetState = () => {
        token.value = ''
        userInfo.value = null
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
    }

    /**
     * 设置用户信息
     */
    const setUserInfo = (info) => {
        userInfo.value = info
        localStorage.setItem('userInfo', JSON.stringify(info))
    }

    /**
     * 设置用户姓名
     */
    const setUserName = (name) => {
        if (userInfo.value) {
            userInfo.value.full_name = name
            userInfo.value.real_name = name // 兼容字段
            localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
        }
    }

    return {
        // 状态
        token,
        userInfo,

        // 计算属性
        isLoggedIn,
        userName,
        userRole,
        studentId,
        isAdmin,
        isMember,

        // 方法
        login,
        getUserInfo,
        logout,
        resetState,
        setUserInfo,
        setUserName
    }
})
