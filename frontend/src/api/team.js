import request from '@/utils/request'

/**
 * 报名通道状态
 */
export function getSignupStatus(params) {
    return request({
        url: '/api/v1/signup_status',
        method: 'get',
        params
    })
}

/**
 * 选题通道状态
 */
export function getTopicStatus(params) {
    return request({
        url: '/api/v1/topic_status',
        method: 'get',
        params
    })
}

/**
 * 队伍信息修改通道状态
 */
export function getTeamUpdateStatus(params) {
    return request({
        url: '/api/v1/team_update_status',
        method: 'get',
        params
    })
}

/**
 * 获取题目列表
 */
export function getTopics(params) {
    return request({
        url: '/api/v1/topics',
        method: 'get',
        params
    })
}

/**
 * 公开端提交队伍报名
 */
export function createTeam(data) {
    return request({
        url: '/api/v1/teams',
        method: 'post',
        data
    })
}

/**
 * 公开端按学号查询队伍
 */
export function getTeamBySid(sid, params) {
    return request({
        url: `/api/v1/teams/by_sid/${sid}`,
        method: 'get',
        params
    })
}

/**
 * 公开端修改队伍信息
 */
export function updateTeam(teamId, data) {
    return request({
        url: `/api/v1/teams/${teamId}`,
        method: 'put',
        data
    })
}

/**
 * 公开端修改队伍选题
 */
export function updateTeamTopic(teamId, data) {
    return request({
        url: `/api/v1/teams/${teamId}/topic`,
        method: 'put',
        data
    })
}

/**
 * 公开端删除队伍
 */
export function deleteTeam(teamId, data) {
    return request({
        url: `/api/v1/teams/${teamId}`,
        method: 'delete',
        data
    })
}

/**
 * 成员/管理员查看队伍列表
 */
export function getTeams(params) {
    return request({
        url: '/api/v1/teams',
        method: 'get',
        params
    })
}

/**
 * 成员/管理员导出队伍
 */
export function exportTeams(params) {
    return request({
        url: '/api/v1/teams/export',
        method: 'get',
        params,
        responseType: 'blob'
    })
}

/**
 * 管理员查看队伍详情
 */
export function getTeamDetail(teamId) {
    return request({
        url: `/api/v1/teams/${teamId}`,
        method: 'get'
    })
}

/**
 * 管理员批量删除队伍
 */
export function batchDeleteTeams(data) {
    return request({
        url: '/api/v1/teams/batch-delete',
        method: 'post',
        data
    })
}

/**
 * 管理员确认彻底删除队伍
 */
export function confirmDeleteTeam(teamId) {
    return request({
        url: `/api/v1/teams/${teamId}/confirm-delete`,
        method: 'post'
    })
}

/**
 * 管理员批量修改队伍选题
 */
export function batchUpdateTeamTopic(data) {
    return request({
        url: '/api/v1/teams/batch-topic',
        method: 'post',
        data
    })
}

/**
 * 管理员更新验收安排
 */
export function updateTeamInspection(teamId, data) {
    return request({
        url: `/api/v1/teams/${teamId}/inspection`,
        method: 'put',
        data
    })
}

/**
 * 管理员更新通道配置
 */
export function updateTeamChannelConfig(data) {
    return request({
        url: '/api/v1/teams/channel-config',
        method: 'put',
        data
    })
}

/**
 * 管理员新增题目
 */
export function createTopic(data) {
    return request({
        url: '/api/v1/topics',
        method: 'post',
        data
    })
}

/**
 * 管理员修改题目
 */
export function updateTopic(topicId, data) {
    return request({
        url: `/api/v1/topics/${topicId}`,
        method: 'put',
        data
    })
}
