/**
 * 会议室预约 API
 */
import request from '@/utils/request'

/**
 * 获取指定日期的预约列表
 * @param {string} date - 日期 YYYY-MM-DD
 */
export function getBookings(date) {
    return request({
        url: '/api/bookings',
        method: 'get',
        params: { date }
    })
}

/**
 * 提交会议室预约
 * @param {Object} data 
 */
export function createBooking(data) {
    return request({
        url: '/api/bookings',
        method: 'post',
        data
    })
}

/**
 * 取消预约
 * @param {number} id 
 */
export function cancelBooking(id) {
    return request({
        url: `/api/bookings/${id}`,
        method: 'delete'
    })
}

/**
 * 获取我的预约
 * @param {boolean} upcoming - 是否仅获取未来预约
 */
export function getMyBookings(upcoming = false) {
    return request({
        url: '/api/bookings/my',
        method: 'get',
        params: { upcoming }
    })
}

/**
 * 获取管理员视角的预约列表（支持时间范围）
 * @param {string} startDate - 开始日期 YYYY-MM-DD
 * @param {string} endDate - 结束日期 YYYY-MM-DD
 */
export function getAdminBookings(startDate, endDate) {
    return request({
        url: '/api/v1/admin/bookings/range',
        method: 'get',
        params: { start_date: startDate, end_date: endDate }
    })
}

/**
 * 导出月度预约记录
 * @param {number} year 
 * @param {number} month 
 */
export function exportBookings(year, month) {
    return request({
        url: '/api/v1/admin/bookings/export',
        method: 'get',
        params: { year, month },
        responseType: 'blob'
    })
}
