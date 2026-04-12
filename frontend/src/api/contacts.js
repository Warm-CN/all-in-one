import request from '@/utils/request'

/**
 * 获取通讯录列表
 * @param {Object} params - 查询参数 { keyword, department }
 */
export function getContacts(params) {
    return request({
        url: '/api/v1/users/',
        method: 'get',
        params
    })
}
