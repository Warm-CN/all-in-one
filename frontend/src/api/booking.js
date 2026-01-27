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
 */
export function getMyBookings() {
    return request({
        url: '/api/bookings/my',
        method: 'get'
    })
}
