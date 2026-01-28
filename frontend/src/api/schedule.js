/**
 * 日程管理 API
 */
import request from '@/utils/request'

/**
 * 获取日程列表
 * @param {Object} params - 查询参数
 * @param {string} params.date - 指定日期 YYYY-MM-DD（可选）
 * @param {string} params.start_date - 起始日期 YYYY-MM-DD（可选）
 * @param {string} params.end_date - 结束日期 YYYY-MM-DD（可选）
 */
export function getSchedules(params) {
    return request({
        url: '/api/v1/schedules',
        method: 'get',
        params
    })
}

/**
 * 创建日程（管理员）
 * @param {Object} data - 日程数据
 * @param {string} data.title - 日程标题
 * @param {string} data.schedule_date - 日程日期 YYYY-MM-DD
 * @param {string} data.start_time - 开始时间 HH:mm
 * @param {string} data.end_time - 结束时间 HH:mm
 * @param {string} data.location - 地点（可选）
 * @param {string} data.color - 颜色标记（可选，默认 #3B82F6）
 */
export function createSchedule(data) {
    return request({
        url: '/api/v1/admin/schedules',
        method: 'post',
        data
    })
}

/**
 * 删除日程（管理员）
 * @param {number} id - 日程ID
 */
export function deleteSchedule(id) {
    return request({
        url: `/api/v1/admin/schedules/${id}`,
        method: 'delete'
    })
}

/**
 * 检查时间冲突（管理员）
 * @param {Object} params - 检查参数
 * @param {string} params.schedule_date - 日程日期 YYYY-MM-DD
 * @param {string} params.start_time - 开始时间 HH:mm
 * @param {string} params.end_time - 结束时间 HH:mm
 * @param {number} params.exclude_id - 排除的日程ID（可选）
 */
export function checkOverlap(params) {
    return request({
        url: '/api/v1/admin/schedules/check-overlap',
        method: 'get',
        params
    })
}
