import request from '@/utils/request'

/**
 * 获取活跃的报名配置
 */
export function getActiveConfigs(params) {
    return request({
        url: '/api/v1/signups/configs',
        method: 'get',
        params
    })
}

/**
 * 提交报名表单
 */
export function submitApply(data) {
    return request({
        url: '/api/v1/signups/apply',
        method: 'post',
        data
    })
}

/**
 * 查询报名状态和面试信息
 */
export function queryStatus(data) {
    return request({
        url: '/api/v1/signups/query-status',
        method: 'post',
        data
    })
}

/**
 * 修改报名信息
 */
export function updateApply(applicationId, data) {
    return request({
        url: `/api/v1/signups/apply/${applicationId}`,
        method: 'put',
        data
    })
}

/**
 * 内部查看报名列表（成员可见）
 */
export function getInternalApplications(params) {
    return request({
        url: '/api/v1/signups/applications/internal',
        method: 'get',
        params
    })
}

/**
 * 管理员修改报名记录
 */
export function adminUpdateApplication(applicationId, data) {
    return request({
        url: `/api/v1/signups/applications/${applicationId}/admin`,
        method: 'put',
        data
    })
}

/**
 * 管理员删除报名记录
 */
export function adminDeleteApplication(applicationId) {
    return request({
        url: `/api/v1/signups/applications/${applicationId}`,
        method: 'delete'
    })
}

/**
 * 管理员导出报名表
 */
export function exportApplications(params) {
    return request({
        url: '/api/v1/signups/applications/export',
        method: 'get',
        params,
        responseType: 'blob'
    })
}

/**
 * 管理员导入面试安排
 */
export function importInterviewArrangements(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request({
        url: '/api/v1/signups/applications/import',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

/**
 * 管理员查看报名配置
 */
export function getAdminSignupConfigs(params) {
    return request({
        url: '/api/v1/signups/admin/configs',
        method: 'get',
        params
    })
}

/**
 * 管理员新建报名配置
 */
export function createAdminSignupConfig(data) {
    return request({
        url: '/api/v1/signups/admin/configs',
        method: 'post',
        data
    })
}

/**
 * 管理员更新报名配置
 */
export function updateAdminSignupConfig(configId, data) {
    return request({
        url: `/api/v1/signups/admin/configs/${configId}`,
        method: 'put',
        data
    })
}
