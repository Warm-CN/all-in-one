import request from '@/utils/request'

export function getCompetitionEvents(cupType) {
  return request({
    url: '/api/v1/competitions/events',
    method: 'get',
    params: { cup_type: cupType }
  })
}

export function getCompetitionEventDetail(eventId) {
  return request({
    url: `/api/v1/competitions/events/${eventId}`,
    method: 'get'
  })
}

export function getCurrentCompetitionEvent() {
  return request({
    url: '/api/v1/competitions/current-event',
    method: 'get'
  })
}

export function createCompetitionEvent(data) {
  return request({
    url: '/api/v1/competitions/events',
    method: 'post',
    data
  })
}

export function updateCompetitionEvent(eventId, data) {
  return request({
    url: `/api/v1/competitions/events/${eventId}`,
    method: 'put',
    data
  })
}

export function createCompetitionTopic(eventId, payload) {
  const formData = new FormData()
  formData.append('title', payload.title)
  if (payload.description) formData.append('description', payload.description)
  if (payload.document) formData.append('document', payload.document)

  return request({
    url: `/api/v1/competitions/events/${eventId}/topics`,
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function updateCompetitionTopic(eventId, topicId, payload) {
  const formData = new FormData()
  formData.append('title', payload.title)
  if (payload.description) formData.append('description', payload.description)
  if (payload.document) formData.append('document', payload.document)

  return request({
    url: `/api/v1/competitions/events/${eventId}/topics/${topicId}`,
    method: 'put',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function updateCompetitionPortalTitle(eventId, portalTitle) {
  return request({
    url: `/api/v1/competitions/events/${eventId}/portal-config`,
    method: 'put',
    data: { portal_title: portalTitle }
  })
}

export function updateCompetitionEventName(eventId, name) {
  return request({
    url: `/api/v1/competitions/events/${eventId}/name`,
    method: 'put',
    data: { name }
  })
}

export function updateCompetitionActiveState(eventId, isCurrent) {
  return request({
    url: `/api/v1/competitions/events/${eventId}/active-state`,
    method: 'put',
    data: { is_current: isCurrent }
  })
}
