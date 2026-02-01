import request from '@/utils/request'

export function updateProfile(data) {
    return request({
        url: '/api/v1/users/me',
        method: 'put',
        data
    })
}

export function getPendingUsers() {
    return request({
        url: '/api/admin/users/pending',
        method: 'get'
    })
}
