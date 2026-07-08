import request from '@/utils/request'

// 意见列表
export function getSuggestions(params = {}) {
  return request.get('/api/v1/suggestions', { params })
}

// 提交意见
export function createSuggestion(data) {
  return request.post('/api/v1/suggestions', data)
}

// 意见详情
export function getSuggestionDetail(id) {
  return request.get(`/api/v1/suggestions/${id}`)
}

// 更新状态(管理员)
export function updateSuggestionStatus(id, data) {
  return request.patch(`/api/v1/suggestions/${id}/status`, data)
}

// 追加意见/评论
export function createReply(id, data) {
  return request.post(`/api/v1/suggestions/${id}/replies`, data)
}

// 复议/取消复议
export function toggleEndorse(replyId) {
  return request.post(`/api/v1/suggestions/replies/${replyId}/endorse`)
}

// 截图图片 URL(仅用于不需要认证的场景)
export function screenshotImageUrl(screenshotId) {
  return `/api/v1/suggestions/screenshots/${screenshotId}/image`
}

// 带认证头获取截图图片(返回 Blob)
export async function fetchScreenshotImage(screenshotId) {
  return await request.get(`/api/v1/suggestions/screenshots/${screenshotId}/image`, {
    responseType: 'blob'
  })
}
