/**
 * 认证相关 API
 */
import request from '@/utils/request'

/**
 * 用户登录
 * @param {string} student_id - 学号
 * @param {string} password - 密码
 * @returns {Promise}
 */
export function login(student_id, password) {
    return request({
        url: '/api/v1/auth/login',
        method: 'post',
        data: {
            student_id,
            password
        }
    })
}

/**
 * 用户注册
 * @param {Object} data - 注册数据
 * @returns {Promise}
 */
export function register(data) {
    return request({
        url: '/api/v1/auth/register',
        method: 'post',
        data
    })
}

/**
 * 获取当前用户信息
 * @returns {Promise}
 */
export function getCurrentUser() {
    return request({
        url: '/api/v1/auth/me',
        method: 'get'
    })
}

/**
 * 修改密码
 * @param {string} old_password - 旧密码
 * @param {string} new_password - 新密码
 * @returns {Promise}
 */
export function changePassword(old_password, new_password) {
    return request({
        url: '/api/v1/auth/password',
        method: 'put',
        data: {
            old_password,
            new_password
        }
    })
}

/**
 * 退出登录（清除本地数据）
 */
export function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
}
