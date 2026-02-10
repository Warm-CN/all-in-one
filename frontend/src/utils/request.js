/**
 * Axios 请求封装
 * 自动添加 Token，处理响应拦截
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 获取 API 基础地址
// 生产环境使用 /api（由 Nginx 代理）
// 开发环境可以为空（使用 Vite 代理）或直接指定后端地址
const getBaseURL = () => {
    const envUrl = import.meta.env.VITE_API_BASE_URL
    // 如果环境变量存在（包括空字符串），使用它；否则使用默认值
    if (envUrl !== undefined) {
        return envUrl
    }
    return 'http://localhost:8001'
}

// 创建 axios 实例
const request = axios.create({
    baseURL: getBaseURL(),
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器 - 自动添加 Token
request.interceptors.request.use(
    config => {
        // 从 localStorage 获取 Token
        const token = localStorage.getItem('token')

        if (token) {
            // 在请求头中加入 Authorization
            config.headers.Authorization = `Bearer ${token}`
        }

        return config
    },
    error => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器 - 统一处理响应和错误
request.interceptors.response.use(
    response => {
        // Blob 响应（文件下载）直接返回
        if (response.config.responseType === 'blob') {
            return response.data
        }

        const res = response.data

        // 后端统一返回格式：{ code, msg, data }
        if (res.code === 200) {
            return res
        } else {
            // 业务错误
            ElMessage.error(res.msg || '请求失败')
            return Promise.reject(new Error(res.msg || '请求失败'))
        }
    },
    error => {
        console.error('响应错误:', error)

        if (error.response) {
            const { status, data } = error.response

            switch (status) {
                case 401:
                    // Token 无效或过期
                    ElMessage.error(data.msg || 'Token 已过期，请重新登录')

                    // 清除本地存储
                    localStorage.removeItem('token')
                    localStorage.removeItem('userInfo')

                    // 跳转到登录页
                    router.push('/login')
                    break

                case 403:
                    ElMessage.error(data.msg || '权限不足')
                    break

                case 404:
                    ElMessage.error(data.msg || '请求的资源不存在')
                    break

                case 422:
                    // 处理 FastAPI 验证错误
                    if (data.detail && Array.isArray(data.detail)) {
                        // 取第一个错误展示，或者拼接
                        const firstError = data.detail[0]
                        const field = firstError.loc ? firstError.loc[firstError.loc.length - 1] : '字段'
                        ElMessage.error(`参数校验失败: ${field} - ${firstError.msg}`)
                    } else {
                        ElMessage.error(data.msg || '参数校验失败')
                    }
                    break

                case 500:
                    ElMessage.error(data.msg || '服务器内部错误')
                    break

                default:
                    ElMessage.error(data.msg || `请求失败 (${status})`)
            }
        } else if (error.request) {
            // 请求发出但没有收到响应
            ElMessage.error('网络连接失败，请检查您的网络')
        } else {
            // 其他错误
            ElMessage.error(error.message || '请求失败')
        }

        return Promise.reject(error)
    }
)

export default request
